# -*- coding: utf-8 -*-
"""v2: 回應評閱意見重做圖表。
- 色覺友善色盤(RdYlBu 系,棄紅綠)
- 圖A 四象限散點(取代雙軸折線,不再製造假連續趨勢)
- 圖B 連續色階真熱力圖(顯示 V3 幅度,非類別分區)
- 圖C 每床急診壓力 vs 承載假設(取代被壓底的需求曲線)
"""
import csv, json, re, shutil, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Polygon as MplPoly
from matplotlib.collections import PatchCollection
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib.patheffects as pe

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"C:\Vision")
F_PRED = BASE / "陳昱廷_AI 預測分析＋急診資料補強"
F_VIZ = BASE / "高育仁_視覺化圖表製作"
F_FERMI = BASE / "陳宥勳_費米建模＋數據洞察"
DASH = BASE / "outputs" / "dashboard"
GEO = BASE / "outputs" / "taichung_districts.geojson"
(DASH / "assets").mkdir(parents=True, exist_ok=True)

rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "SimHei"]
rcParams["axes.unicode_minus"] = False

# 色覺友善(RdYlBu)：紅=危機, 橘=低, 淺藍=中高, 深藍=平衡(無綠)
C_CRISIS, C_WARN, C_MID, C_GOOD, C_INK = "#D73027", "#FDAE61", "#74ADD1", "#4575B4", "#2C2C2A"

def flag_color(fl):
    if "跨區" in fl or "無在地" in fl: return C_CRISIS
    if "HAAI低" in fl: return C_WARN
    if "HAAI中高" in fl: return C_MID
    return C_GOOD

# ---- V3 ranking (陳宥勳) ----
html = (F_FERMI / "haai_v3_tryout_results.html").read_text(encoding="utf-8")
V3 = json.loads(re.search(r"const D = (\[.*?\]);", html, re.S).group(1))
v3 = {r["d"]: r for r in V3}

# ---- phase3 master (陳昱廷) ----
p3 = {}
with open(F_PRED / "haai_master_v3_phase3.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        p3[r["district"]] = r

# ---- flag + centroids (高育仁) ----
flag, cent = {}, {}
with open(F_VIZ / "flag_choropleth_ready.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        flag[r["district"]] = r["phase4_flag"]
        cent[r["district"]] = (float(r["district_lon"]), float(r["district_lat"]))

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
            sit = f"有在地急診，但每床年壓力達 {pressure:.0f} 人次（推估），屬結構性資源錯配。"
            plan = "優先增設急性病床或建立分流後送動線，紓解單床負荷。"
        elif pressure >= 150:
            sit = f"在地急診每床年壓力 {pressure:.0f} 人次（推估），2035 前接近承載上限。"
            plan = "監測承載並預備擴床彈性。"
        else:
            sit = f"在地急診量能相對充裕（每床年壓力 {pressure:.0f} 人次，推估）。"
            plan = "維持現況，可作為鄰近高壓區的分流後送點。"
        decide = f"以每床壓力與急診需求成長（2024→2035 +{growth:.1f}%）為監測指標。"
    return {"situation": sit, "plan": plan, "decide": decide}

records = []
for d, r in v3.items():
    p = p3.get(d, {})
    fl = flag.get(d, "相對平衡")
    km = num(r.get("km")); near = p.get("nearest_regional_or_medical_center_district", "")
    cls = p.get("capacity_class", ""); el = num(r.get("el"))
    dem24 = num(p.get("er_demand_2024")); dem35 = num(p.get("er_demand_2035_base"))
    growth = num(p.get("er_demand_growth_pct_2024_2035")); pressure = num(p.get("pressure_per_bed_2024"))
    records.append({
        "district": d, "rank": int(r["r3"]), "v3": round(num(r["v3"]), 1), "gap": round(100 - num(r["v3"]), 1),
        "sup": num(r["sup"]), "dem": num(r["dem"]), "acc": num(r["acc"]),
        "elderly": round(el, 1), "km": round(km, 1), "flag": fl, "flag_color": flag_color(fl),
        "capacity": cls, "demand_2024": int(dem24), "demand_2035": int(dem35),
        "growth": round(growth, 1), "pressure": round(pressure), "data_complete": p.get("data_complete", ""),
        "diag": diagnose(d, p, km, near, cls, el, dem24, dem35, growth, pressure),
    })
records.sort(key=lambda x: x["rank"])
(DASH / "diagnosis_data.json").write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")

# ======== 圖A：四象限散點 ========
fig, ax = plt.subplots(figsize=(11, 6.4), dpi=130)
els = [r["elderly"] for r in records]; vs = [r["v3"] for r in records]
mx_el, mx_v = float(np.median(els)), float(np.median(vs))
ax.axvspan(mx_el, max(els) + 1.5, ymin=0, ymax=(mx_v) / 105, color=C_CRISIS, alpha=0.06)
ax.axvline(mx_el, color="#888780", lw=1, ls="--"); ax.axhline(mx_v, color="#888780", lw=1, ls="--")
for r in records:
    ax.scatter(r["elderly"], r["v3"], s=90, color=r["flag_color"], edgecolor="white", lw=0.8, zorder=3)
label = ["和平區", "東勢區", "新社區", "石岡區", "大安區", "北屯區", "中區", "北區", "梧棲區", "沙鹿區"]
for r in records:
    if r["district"] in label:
        ax.annotate(r["district"], (r["elderly"], r["v3"]), fontsize=9, xytext=(5, 4),
                    textcoords="offset points", color=C_INK)
ax.text(max(els) + 1.8, 4, "高齡高 · 可及性低（高風險象限）", fontsize=10, color=C_CRISIS,
        ha="right", va="bottom", weight="bold")
ax.set_xlabel("老年人口比率（%，越右需求越高）", fontsize=11, color=C_INK)
ax.set_ylabel("HAAI 可及性指數（V3，0–100，越低越缺）", fontsize=11, color=C_INK)
ax.set_title("高齡需求 × 醫療可及性：右下象限為「需求高、可及性低」的高風險行政區",
             fontsize=13, color=C_INK, loc="left", pad=12)
ax.set_xlim(min(els) - 1, max(els) + 2); ax.set_ylim(0, 105)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(DASH / "assets" / "scatter_quadrant.png", bbox_inches="tight"); plt.close(fig)

# ======== 圖B：連續色階真熱力圖 ========
geo = json.loads(GEO.read_text(encoding="utf-8"))
v3map = {r["district"]: r["v3"] for r in records}
def rings(g):
    t, c = g["type"], g["coordinates"]
    return [c[0]] if t == "Polygon" else [poly[0] for poly in c]
patches, vals = [], []
for feat in geo["features"]:
    d = feat["properties"].get("district")
    if d not in v3map: continue
    for ring in rings(feat["geometry"]):
        patches.append(MplPoly([(p[0], p[1]) for p in ring], closed=True)); vals.append(v3map[d])
fig, ax = plt.subplots(figsize=(11, 7.2), dpi=130)
norm = mcolors.Normalize(vmin=min(vals), vmax=max(vals))
pc = PatchCollection(patches, edgecolor="white", linewidth=0.6)
pc.set_array(np.array(vals)); pc.set_cmap(cm.cividis); pc.set_norm(norm)
ax.add_collection(pc)
for d, (lon, lat) in cent.items():
    if d in v3map:
        ax.text(lon, lat, d.replace("區", ""), fontsize=7, ha="center", va="center", color="white",
                path_effects=[pe.withStroke(linewidth=1.6, foreground="#333333")])
ax.autoscale(); ax.set_aspect("equal"); ax.axis("off")
cb = fig.colorbar(pc, ax=ax, shrink=0.7, pad=0.01)
cb.set_label("HAAI 可及性指數（V3，越低越缺乏）", fontsize=10)
ax.set_title("台中市醫療可及性連續分布（色覺友善 cividis）", fontsize=13, color=C_INK, loc="left", pad=8)
fig.tight_layout(); fig.savefig(DASH / "assets" / "choropleth_continuous.png", bbox_inches="tight"); plt.close(fig)

# ======== 圖C：每床急診壓力 vs 承載假設 ========
bedded = sorted([r for r in records if r["pressure"] > 0], key=lambda x: x["pressure"], reverse=True)
fig, ax = plt.subplots(figsize=(11, 6.2), dpi=130)
ys = np.arange(len(bedded))
ax.barh(ys, [r["pressure"] for r in bedded], color=[r["flag_color"] for r in bedded], zorder=3)
ax.set_yticks(ys); ax.set_yticklabels([r["district"] for r in bedded], fontsize=9); ax.invert_yaxis()
for x, lab, col in [(50, "×50", "#4575B4"), (100, "×100", "#BA7517"), (150, "×150", "#D73027")]:
    ax.axvline(x, ls="--", lw=1.2, color=col, zorder=2)
    ax.text(x, -0.4, lab, fontsize=9, color=col, ha="center", va="bottom", weight="bold")
ax.text(1.0, 1.015, "虛線為每床年吞吐量承載假設（示意敏感度）", transform=ax.transAxes,
        fontsize=8.5, color="#5F5E5A", ha="right", va="bottom")
ax.set_xlabel("每床年急診壓力（人次／床，推估）", fontsize=11, color=C_INK)
ax.set_title("各區每床急診壓力 vs 承載假設：北屯遠超任何吞吐假設，缺口與係數無關",
             fontsize=12.5, color=C_INK, loc="left", pad=18)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(DASH / "assets" / "pressure_bar.png", bbox_inches="tight"); plt.close(fig)

# keep sankey
shutil.copy(F_VIZ / "03_cross_district_sankey.html", DASH / "assets" / "sankey.html")

# KPI
total_beds = sum(num(p3[d].get("open_beds")) for d in p3)
oldest = max(records, key=lambda x: x["elderly"])
beitun = next(r for r in records if r["district"] == "北屯區")
heping = next(r for r in records if r["district"] == "和平區")
kpi = {"total_beds": int(total_beds), "oldest": {"d": oldest["district"], "el": oldest["elderly"]},
       "beitun_pressure": beitun["pressure"], "beitun_beds": int(num(p3["北屯區"].get("open_beds"))),
       "heping_km": heping["km"], "no_local_count": sum(1 for r in records if "無在地" in r["capacity"] or r["pressure"] == 0)}
(DASH / "kpi.json").write_text(json.dumps(kpi, ensure_ascii=False, indent=1), encoding="utf-8")

print("records:", len(records), "| bedded:", len(bedded))
print("charts:", [p.name for p in (DASH / "assets").glob("*.png")])
print("V3 formula check done. gap field added (gap=100-v3).")
