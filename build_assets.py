from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as MplPolygon
import numpy as np
import pandas as pd
from scipy import stats


BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "outputs"
DASH = OUT / "dashboard"
ASSETS = DASH / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

COLORS = {
    "無在地一般病床·跨區依賴": "#CC6677",
    "高齡高·可及性低": "#EE7733",
    "高齡高·可及性中高": "#4477AA",
    "需求較低·可及性仍低": "#AA4499",
    "相對平衡": "#228833",
}
INK = "#252422"
MUTED = "#6B6A65"
GRID = "#D8D5CE"


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def policy_legend() -> list[Line2D]:
    return [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color, markeredgecolor="white",
               markersize=8, label=label)
        for label, color in COLORS.items()
    ]


def draw_map(df: pd.DataFrame) -> None:
    geo = json.loads((OUT / "taichung_districts.geojson").read_text(encoding="utf-8"))
    score = df.set_index("district")["accessibility_index"].to_dict()

    def rings(geometry: dict) -> list:
        coords = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            return [coords[0]]
        return [polygon[0] for polygon in coords]

    patches, values = [], []
    for feature in geo["features"]:
        district = feature["properties"].get("district")
        if district not in score:
            continue
        for ring in rings(feature["geometry"]):
            patches.append(MplPolygon([(point[0], point[1]) for point in ring], closed=True))
            values.append(score[district])

    fig, ax = plt.subplots(figsize=(11.2, 6.8))
    norm = mcolors.Normalize(vmin=0, vmax=100)
    collection = PatchCollection(patches, edgecolor="white", linewidth=0.65, cmap=cm.cividis, norm=norm)
    collection.set_array(np.asarray(values))
    ax.add_collection(collection)

    for _, row in df.iterrows():
        ax.text(
            row["district_lon"], row["district_lat"], row["district"].replace("區", ""),
            fontsize=7.2, ha="center", va="center", color="white",
            path_effects=[pe.withStroke(linewidth=1.8, foreground="#202020")],
        )
    ax.autoscale()
    ax.set_aspect("equal")
    ax.axis("off")
    colorbar = fig.colorbar(collection, ax=ax, shrink=0.76, pad=0.015)
    colorbar.set_label("醫療可及性指數（0–100；越高越佳）", fontsize=10)
    ax.set_title("台中市醫療可及性指數：連續色階空間分布", loc="left", fontsize=15, color=INK, pad=12)
    ax.text(0, -0.035, "註：距離為行政區中心點至最近區域級以上醫院所在區中心點的直線代理。",
            transform=ax.transAxes, fontsize=9, color=MUTED)
    save(fig, "choropleth_continuous.png")


def regression_panel(ax: plt.Axes, x: pd.Series, y: pd.Series, title: str, ylabel: str, color: str) -> None:
    ax.scatter(x, y, s=44, color=color, alpha=0.88, edgecolor="white", linewidth=0.6, zorder=3)
    slope, intercept = np.polyfit(x, y, 1)
    xx = np.linspace(float(x.min()), float(x.max()), 100)
    ax.plot(xx, slope * xx + intercept, color=INK, lw=1.3, ls="--", zorder=2)
    r, p = stats.pearsonr(x, y)
    ax.text(0.03, 0.96, f"Pearson r = {r:+.2f}；p = {p:.3f}", transform=ax.transAxes,
            va="top", fontsize=10, color=INK,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": GRID})
    ax.set_title(title, loc="left", fontsize=12.5, color=INK)
    ax.set_xlabel("65歲以上人口比率（%）", fontsize=10.5)
    ax.set_ylabel(ylabel, fontsize=10.5)
    ax.grid(alpha=0.25, color=GRID)
    ax.spines[["top", "right"]].set_visible(False)


def draw_observed_conflict(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2))
    regression_panel(
        axes[0], df["elderly_rate_pct"], df["beds_per_10k_population"],
        "A｜病床沒有跟著老化需求配置", "每萬人開放一般病床數", "#4477AA",
    )
    regression_panel(
        axes[1], df["elderly_rate_pct"], df["nearest_regional_or_medical_center_km"],
        "B｜老化越高，代理就醫距離反而越遠", "距區域級以上醫院所在區中心點（km）", "#CC6677",
    )
    for district in ["北屯區", "中區"]:
        row = df[df["district"].eq(district)].iloc[0]
        axes[0].annotate(district, (row["elderly_rate_pct"], row["beds_per_10k_population"]),
                         xytext=(4, 4), textcoords="offset points", fontsize=8.5, color=INK)
    for district in ["和平區", "東勢區", "新社區", "石岡區", "北屯區"]:
        row = df[df["district"].eq(district)].iloc[0]
        axes[1].annotate(district, (row["elderly_rate_pct"], row["nearest_regional_or_medical_center_km"]),
                         xytext=(4, 4), textcoords="offset points", fontsize=8.5, color=INK)
    fig.suptitle("猜想 vs. 行政資料：醫療供給與高齡需求並未同步", x=0.02, ha="left", fontsize=15, color=INK)
    fig.text(0.02, 0.005, "左圖顯示病床密度與高齡率無顯著關聯；右圖顯示高齡率與代理距離呈顯著正相關。相關不等於因果。",
             fontsize=9.2, color=MUTED)
    save(fig, "observed_conflict.png")


def draw_quadrant(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    age_median = float(df["elderly_rate_pct"].median())
    score_median = float(df["accessibility_index"].median())
    ax.axvspan(age_median, df["elderly_rate_pct"].max() + 1.2, ymin=0, ymax=score_median / 105,
               color="#EE7733", alpha=0.08)
    ax.axvline(age_median, color="#888780", lw=1, ls="--")
    ax.axhline(score_median, color="#888780", lw=1, ls="--")
    for flag, group in df.groupby("policy_flag"):
        ax.scatter(group["elderly_rate_pct"], group["accessibility_index"], s=58,
                   color=COLORS[flag], edgecolor="white", linewidth=0.7, label=flag, zorder=3)
    for district in ["和平區", "東勢區", "新社區", "石岡區", "北屯區", "梧棲區", "北區", "中區"]:
        row = df[df["district"].eq(district)].iloc[0]
        ax.annotate(district, (row["elderly_rate_pct"], row["accessibility_index"]),
                    xytext=(5, 4), textcoords="offset points", fontsize=8.5, color=INK)
    ax.text(df["elderly_rate_pct"].max() + 0.8, 4, "優先查核區\n高齡高 × 可及性低",
            ha="right", va="bottom", fontsize=10, color="#B24B20", weight="bold")
    ax.set_xlim(df["elderly_rate_pct"].min() - 1, df["elderly_rate_pct"].max() + 1.3)
    ax.set_ylim(0, 105)
    ax.set_xlabel("65歲以上人口比率（%；越右需求越高）", fontsize=10.5)
    ax.set_ylabel("醫療可及性指數（0–100；越高越佳）", fontsize=10.5)
    ax.set_title("政策篩選：高齡需求 × 醫療可及性四象限", loc="left", fontsize=15, color=INK, pad=12)
    ax.legend(handles=policy_legend(), loc="upper right", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.18, color=GRID)
    ax.text(0, -0.12, "註：此圖用於政策排序；因高齡率是指數構成要素之一，不作獨立統計驗證。",
            transform=ax.transAxes, fontsize=9, color=MUTED)
    save(fig, "scatter_quadrant.png")


def draw_pressure(df: pd.DataFrame) -> None:
    bedded = df[df["open_beds"].gt(0)].sort_values("pressure_per_bed_2024", ascending=False)
    zero = df[df["open_beds"].eq(0)].sort_values("nearest_regional_or_medical_center_km", ascending=False)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 6.5), gridspec_kw={"width_ratios": [1.45, 0.85]})

    y = np.arange(len(bedded))
    ax.barh(y, bedded["pressure_per_bed_2024"], color="#4477AA", zorder=3)
    ax.set_yticks(y, bedded["district"], fontsize=9)
    ax.invert_yaxis()
    for threshold, color in [(50, "#228833"), (100, "#D98E04"), (150, "#CC6677")]:
        ax.axvline(threshold, ls="--", lw=1.2, color=color, label=f"情境門檻 ×{threshold}")
    ax.set_xlabel("推估急診人次 ÷ 開放一般病床（人次/床）", fontsize=10)
    ax.set_title("A｜有床區：相對壓力排序", loc="left", fontsize=12.5)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    ax.grid(axis="x", alpha=0.2, color=GRID)
    ax.spines[["top", "right"]].set_visible(False)

    y2 = np.arange(len(zero))
    ax2.barh(y2, zero["nearest_regional_or_medical_center_km"], color="#CC6677", zorder=3)
    ax2.set_yticks(y2, zero["district"], fontsize=9)
    ax2.invert_yaxis()
    for pos, (_, row) in zip(y2, zero.iterrows()):
        ax2.text(row["nearest_regional_or_medical_center_km"] + 0.5, pos,
                 f"{int(row['er_demand_2024']):,}人次(推估)", va="center", fontsize=7.8, color=MUTED)
    ax2.set_xlabel("代理距離（km）", fontsize=10)
    ax2.set_title("B｜零床區：跨區代理距離", loc="left", fontsize=12.5)
    ax2.grid(axis="x", alpha=0.2, color=GRID)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle("急診壓力須分開解讀：有床區看混合壓力，零床區看跨區距離", x=0.02, ha="left", fontsize=15, color=INK)
    fig.text(0.02, 0.002, "註：急診需求為費米推估；一般病床不是急診實際承載量。門檻僅作敏感度比較，不是超載定論。",
             fontsize=9.2, color=MUTED)
    save(fig, "pressure_bar.png")


def copy_sankey() -> None:
    candidates = list(BASE.rglob("03_cross_district_sankey.html"))
    if candidates:
        shutil.copy2(candidates[0], ASSETS / "sankey.html")


def main() -> None:
    df = pd.read_csv(OUT / "haai_analysis.csv", encoding="utf-8-sig")
    draw_map(df)
    draw_observed_conflict(df)
    draw_quadrant(df)
    draw_pressure(df)
    copy_sankey()
    print("Built:", ", ".join(path.name for path in sorted(ASSETS.glob("*.png"))))


if __name__ == "__main__":
    main()
