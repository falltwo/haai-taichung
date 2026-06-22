# -*- coding: utf-8 -*-
"""Unify the three members' outputs on V3 HAAI, regen the dual-axis chart on V3,
and pre-bake per-district diagnosis cards for the click demo.
ponytail: reuse teammates' choropleth + sankey as-is; only the dual-axis bar
(which plots the conflicting raw 0-492 HAAI) gets rebuilt on V3."""
import csv, json, re, shutil, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"C:\Vision")
F_PRED = BASE / "陳昱廷_AI 預測分析＋急診資料補強"
F_VIZ = BASE / "高育仁_視覺化圖表製作"
F_FERMI = BASE / "陳宥勳_費米建模＋數據洞察"
DASH = BASE / "outputs" / "dashboard"
(DASH / "assets").mkdir(parents=True, exist_ok=True)

rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "SimHei"]
rcParams["axes.unicode_minus"] = False

# locked palette (meaning -> color), shared with the dashboard
C_CRISIS, C_WARN, C_MID, C_GOOD, C_INK = "#A32D2D", "#BA7517", "#185FA5", "#0F6E56", "#2C2C2A"

def flag_color(fl):
    if "跨區" in fl or "無在地" in fl: return C_CRISIS
    if "HAAI低" in fl: return C_WARN
    if "HAAI中高" in fl: return C_MID
    return C_GOOD

# --- V3 ranking (陳宥勳, source of truth) ---
html = (F_FERMI / "haai_v3_tryout_results.html").read_text(encoding="utf-8")
V3 = json.loads(re.search(r"const D = (\[.*?\]);", html, re.S).group(1))
v3 = {r["d"]: r for r in V3}

# --- phase3 master (陳昱廷): demand / pressure / capacity ---
p3 = {}
with open(F_PRED / "haai_master_v3_phase3.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        p3[r["district"]] = r

# --- phase4 flag (高育仁): choropleth category ---
flag = {}
with open(F_VIZ / "flag_choropleth_ready.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        flag[r["district"]] = r["phase4_flag"]

def num(x, d=0.0):
    try: return float(x)
    except (TypeError, ValueError): return d

def diagnose(d, p, km, near, cls, el, dem24, dem35, growth, pressure):
    no_local = "無在地" in cls or num(p.get("open_beds")) == 0
    if no_local:
        sit = f"區內無一般急診病床，急診須跨區至{near}（約 {km:.1f} 公里）。"
        if km >= 15:
            sit += "屬距離型可及性危機。"
            plan = "優先評估設立在地急診據點或固定巡迴醫療班次，而非僅增設病床。"
        else:
            plan = f"短期依賴{near}量能，中期評估在地急診據點與跨區轉診動線。"
        decide = f"以老年率（{el:.1f}%）與跨區距離為監測指標，距離未改善前列為高風險。"
    else:
        if pressure >= 300:
            sit = f"有在地急診，但每床年壓力達 {pressure:.0f} 人次，屬結構性資源錯配。"
            plan = "優先增設急性病床或建立分流後送動線，紓解單床負荷。"
        elif pressure >= 150:
            sit = f"在地急診每床年壓力 {pressure:.0f} 人次，2035 前接近承載上限。"
            plan = "監測承載並預備擴床彈性。"
        else:
            sit = f"在地急診量能相對充裕（每床年壓力 {pressure:.0f} 人次）。"
            plan = "維持現況，可作為鄰近高壓區的分流後送點。"
        decide = f"以每床壓力與急診需求成長（2024→2035 +{growth:.1f}%）為監測指標。"
    return {"situation": sit, "plan": plan, "decide": decide}

records = []
for d, r in v3.items():
    p = p3.get(d, {})
    fl = flag.get(d, "相對平衡")
    km = num(r.get("km"))
    near = p.get("nearest_regional_or_medical_center_district", "")
    cls = p.get("capacity_class", "")
    el = num(r.get("el"))
    dem24 = num(p.get("er_demand_2024"))
    dem35 = num(p.get("er_demand_2035_base"))
    growth = num(p.get("er_demand_growth_pct_2024_2035"))
    pressure = num(p.get("pressure_per_bed_2024"))
    records.append({
        "district": d, "rank": int(r["r3"]), "v3": round(num(r["v3"]), 1),
        "sup": num(r["sup"]), "dem": num(r["dem"]), "acc": num(r["acc"]),
        "elderly": round(el, 1), "km": round(km, 1), "flag": fl,
        "flag_color": flag_color(fl), "capacity": cls,
        "demand_2024": int(dem24), "demand_2035": int(dem35), "growth": round(growth, 1),
        "pressure": round(pressure), "data_complete": p.get("data_complete", ""),
        "diag": diagnose(d, p, km, near, cls, el, dem24, dem35, growth, pressure),
    })
records.sort(key=lambda x: x["rank"])

(DASH / "diagnosis_data.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")

# --- regen dual-axis bar on V3: bars = elderly%, line = V3 score, sorted by elderly desc ---
rows = sorted(records, key=lambda x: -x["elderly"])
names = [r["district"] for r in rows]
elderly = [r["elderly"] for r in rows]
v3score = [r["v3"] for r in rows]
colors = [r["flag_color"] for r in rows]
city_avg_el = sum(elderly) / len(elderly)

fig, ax1 = plt.subplots(figsize=(12, 5.2), dpi=130)
ax1.bar(range(len(names)), elderly, color=colors, width=0.72, zorder=2)
ax1.axhline(city_avg_el, ls="--", lw=1, color="#888780", zorder=1)
ax1.text(len(names) - 0.5, city_avg_el + 0.2, f"全市平均高齡率 {city_avg_el:.1f}%",
         ha="right", va="bottom", fontsize=9, color="#5F5E5A")
ax1.set_ylabel("高齡率（%）", fontsize=11, color=C_INK)
ax1.set_ylim(0, max(elderly) * 1.25)
ax1.set_xticks(range(len(names)))
ax1.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
ax1.set_xlim(-0.7, len(names) - 0.3)

ax2 = ax1.twinx()
ax2.plot(range(len(names)), v3score, marker="o", ms=4, lw=1.6, color="#16324f", zorder=3)
ax2.set_ylabel("HAAI V3 分數（0–100，越低越缺）", fontsize=11, color="#16324f")
ax2.set_ylim(0, 105)

ax1.set_title("高齡率越高，HAAI 反而越低：東勢、石岡、新社、和平的「需求高、可及性低」結構",
              fontsize=13, color=C_INK, pad=12, loc="left")
for s in ["top"]:
    ax1.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(DASH / "assets" / "02_dual_axis_v3.png", bbox_inches="tight")
plt.close(fig)

# --- copy reused assets so the dashboard folder is self-contained ---
shutil.copy(F_VIZ / "01_flag_choropleth.png", DASH / "assets" / "01_choropleth.png")
shutil.copy(F_VIZ / "03_cross_district_sankey.html", DASH / "assets" / "sankey.html")

# --- KPI numbers for the header ---
total_beds = sum(num(p3[d].get("open_beds")) for d in p3)
oldest = max(records, key=lambda x: x["elderly"])
beitun = next(r for r in records if r["district"] == "北屯區")
heping = next(r for r in records if r["district"] == "和平區")
kpi = {
    "total_beds": int(total_beds),
    "oldest": {"d": oldest["district"], "el": oldest["elderly"]},
    "beitun_pressure": beitun["pressure"], "beitun_beds": int(num(p3["北屯區"].get("open_beds"))),
    "heping_km": heping["km"],
    "no_local_count": sum(1 for r in records if "無在地" in r["capacity"] or r["pressure"] == 0),
}
(DASH / "kpi.json").write_text(json.dumps(kpi, ensure_ascii=False, indent=1), encoding="utf-8")

print("records:", len(records))
print("v3 range:", min(r["v3"] for r in records), "-", max(r["v3"] for r in records))
print("top3:", [(r["rank"], r["district"], r["v3"]) for r in records[:3]])
print("bottom3:", [(r["rank"], r["district"], r["v3"]) for r in records[-3:]])
print("KPI:", json.dumps(kpi, ensure_ascii=False))
print("sample diag (和平區):", json.dumps(heping["diag"], ensure_ascii=False))
print("assets:", [p.name for p in (DASH / "assets").iterdir()])
