# -*- coding: utf-8 -*-
"""Assemble the self-contained single-page dashboard.
Data is inlined (no fetch) so it runs offline from file:// for the live demo.
ponytail: one hand-written HTML file, no framework, no build step."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DASH = BASE / "outputs" / "dashboard"
DATA = json.loads((DASH / "diagnosis_data.json").read_text(encoding="utf-8"))
KPI = json.loads((DASH / "kpi.json").read_text(encoding="utf-8"))

HTML = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>醫療繁榮的假象 — 台中市醫療可及性 HAAI 分析</title>
<style>
:root{
  --bg:#FBFAF7; --surface:#FFFFFF; --ink:#1F1E1C; --muted:#5F5E5A; --faint:#8A8983;
  --line:rgba(31,30,28,.12); --line2:rgba(31,30,28,.22);
  --crisis:#C0392B; --warn:#B9770E; --mid:#3A7CA5; --good:#1F5C8B;
  --r:10px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Microsoft JhengHei","PingFang TC","Noto Sans TC",system-ui,sans-serif;
  line-height:1.75;-webkit-font-smoothing:antialiased;font-variant-numeric:tabular-nums}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
h1,h2,h3{font-weight:500;line-height:1.3;margin:0}
.num{font-variant-numeric:tabular-nums}
a{color:var(--mid)}

.hero{padding:64px 0 36px;border-bottom:1px solid var(--line)}
.kicker{font-size:13px;color:var(--crisis);letter-spacing:.04em;margin-bottom:14px}
.hero h1{font-size:46px;letter-spacing:-.01em}
.hero .sub{font-size:18px;color:var(--muted);margin-top:14px;max-width:62ch}

.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:34px 0 0}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px 18px 16px}
.kpi .lab{font-size:12.5px;color:var(--faint);margin-bottom:8px}
.kpi .val{font-size:30px;font-weight:500;line-height:1.05}
.kpi .val small{font-size:15px;color:var(--muted);font-weight:400;margin-left:4px}
.kpi .meta{font-size:12px;color:var(--muted);margin-top:7px}
.kpi.k-good .val{color:var(--good)} .kpi.k-crisis .val{color:var(--crisis)} .kpi.k-warn .val{color:var(--warn)}

section{padding:54px 0;border-bottom:1px solid var(--line)}
.eyebrow{font-size:13px;color:var(--faint);margin-bottom:10px}
.h-step{display:inline-flex;align-items:baseline;gap:10px}
.h-step b{font-size:22px;color:var(--crisis);font-weight:500}
section h2{font-size:27px;letter-spacing:-.01em}
section .lede{font-size:17px;color:var(--muted);margin:14px 0 0;max-width:68ch}

.formula{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--mid);
  border-radius:0 var(--r) var(--r) 0;padding:14px 18px;margin:22px 0;font-size:15px;color:var(--ink)}
.formula .v3{color:var(--muted);font-size:13.5px;margin-top:6px}

.legend{display:flex;flex-wrap:wrap;gap:18px;margin:20px 0 14px;font-size:13px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:7px}
.legend i{width:13px;height:13px;border-radius:3px;display:inline-block}

figure{margin:18px 0 0}
figure img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:var(--r);background:#fff}
figcaption{font-size:13px;color:var(--faint);margin-top:9px}

.grid2{display:grid;grid-template-columns:1.15fr .85fr;gap:26px;align-items:start;margin-top:26px}
@media(max-width:900px){.grid2{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:34px}}

table{width:100%;border-collapse:collapse;font-size:13px}
thead th{font-size:11.5px;font-weight:500;color:var(--faint);text-align:left;padding:8px 9px;border-bottom:1px solid var(--line2);white-space:nowrap}
thead th.r{text-align:right}
tbody td{padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:middle}
tbody td.r{text-align:right;font-variant-numeric:tabular-nums}
tbody tr{cursor:pointer;transition:background .12s}
tbody tr:hover{background:#F4F2EC}
tbody tr.on{background:#F0EDE5;box-shadow:inset 3px 0 0 var(--crisis)}
.badge{display:inline-block;font-size:10.5px;padding:1px 6px;border-radius:5px;margin-left:5px;vertical-align:1px}
.badge.proxy{background:#FAEEDA;color:#854F0B}
.score{font-size:14px;font-weight:500;color:var(--mid)}
.stack{display:flex;height:8px;width:120px;border-radius:3px;overflow:hidden;background:#EEEbE3}
.stack i{display:block;height:100%}

.panel{position:sticky;top:18px;background:var(--surface);border:1px solid var(--line2);border-radius:var(--r);padding:20px}
.panel .pd{display:flex;align-items:baseline;justify-content:space-between;gap:10px}
.panel .pd h3{font-size:21px}
.panel .pd .rk{font-size:12.5px;color:var(--faint)}
.panel .cap{display:inline-block;font-size:12px;padding:3px 9px;border-radius:6px;margin-top:10px}
.panel .big{display:flex;gap:22px;margin:16px 0 4px}
.panel .big div{font-size:12px;color:var(--faint)}
.panel .big b{display:block;font-size:23px;font-weight:500;color:var(--ink);margin-top:2px}
.facs{margin:16px 0}
.fac{display:flex;align-items:center;gap:10px;margin:6px 0;font-size:12.5px;color:var(--muted)}
.fac .bar{flex:1;height:7px;border-radius:3px;background:#EEEbE3;overflow:hidden}
.fac .bar i{display:block;height:100%}
.fac .pv{width:34px;text-align:right;color:var(--ink)}
.diag{margin-top:14px;border-top:1px solid var(--line);padding-top:14px}
.diag .row{margin:11px 0}
.diag .k{font-size:11.5px;color:var(--crisis);letter-spacing:.03em;margin-bottom:3px}
.diag .t{font-size:14px;color:var(--ink);line-height:1.65}
.hint{font-size:12px;color:var(--faint);margin-top:12px}

.scn{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px}
@media(max-width:760px){.scn{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px}
.card.star{border-color:var(--good);box-shadow:inset 0 0 0 1px var(--good)}
.card .tag{font-size:11.5px;color:var(--good);margin-bottom:8px}
.card .tag.s2{color:var(--muted)}
.card h3{font-size:16px;margin-bottom:6px}
.card p{font-size:13.5px;color:var(--muted);margin:0}
.card .eff{font-size:13.5px;color:var(--ink);margin-top:9px}

iframe.sankey{width:100%;height:560px;border:1px solid var(--line);border-radius:var(--r);background:#fff;margin-top:20px}

footer{padding:40px 0 70px}
footer h3{font-size:14px;color:var(--muted);margin-bottom:10px}
footer ul{margin:0;padding-left:18px;font-size:12.5px;color:var(--faint);line-height:1.85}
footer .src{font-size:12px;color:var(--faint);margin-top:14px}

.reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none}html{scroll-behavior:auto}}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <div class="kicker">台中市衛生局決策視覺化 · HAAI 醫療可及性指數</div>
    <h1>醫療繁榮的假象</h1>
    <p class="sub">台中市醫療總量可觀，但把 29 個行政區的「資源供給」攤開對上「老化需求」與「就醫距離」，就會看到總量平均掩蓋的空間錯配。</p>
    <div class="kpis">
      <div class="kpi k-good"><div class="lab">全市許可一般病床</div><div class="val num">__LICENSED_BEDS__<small>床</small></div><div class="meta">開放 __OPEN_BEDS__ 床 · __OPEN_PER10K__/萬人</div></div>
      <div class="kpi k-warn"><div class="lab">最高齡行政區</div><div class="val">__OLD_D__ <small class="num">__OLD_E__%</small></div><div class="meta">已超過超高齡社會 20% 門檻</div></div>
      <div class="kpi k-crisis"><div class="lab">北屯區混合壓力（推估）</div><div class="val num">__BEITUN__<small>人次/床</small></div><div class="meta">__BEITUN_B__ 床為官方值 · 分區需求為費米估算</div></div>
      <div class="kpi k-crisis"><div class="lab">和平區跨區代理距離</div><div class="val num">__HEPING__<small>公里</small></div><div class="meta">__NOLOCAL__ 區無開放一般病床</div></div>
    </div>
  </div>
</header>

<section>
  <div class="wrap reveal">
    <div class="eyebrow">S Situation</div>
    <div class="h-step"><b>見</b><h2>先看見繁榮</h2></div>
    <p class="lede">資料表列 66 家醫院、4 家具醫學中心資格的院所（分布於 3 個行政區）、11,153 床許可一般病床與 7,555 名西醫師。模型採用的是 10,541 床開放一般病床（每萬人 36.8 床）。問題不在總量，而在資源是否落在需求與距離壓力最高的地方。</p>
  </div>
</section>

<section>
  <div class="wrap reveal">
    <div class="eyebrow">C Complication · Q Question</div>
    <div class="h-step"><b>識</b><h2>揭穿假象：醫療可及性指數</h2></div>
    <p class="lede">可及性指數（0–100，分數越高代表可及性越佳；缺口 = 100 − 指數）將各區「供給力 × 距離可及性」除以「高齡需求壓力」。分數越低、缺口越大，越是「需求高、可及性低」的高風險區。</p>
    <div class="formula">
      可及性指數 = 100 ×（供給力 × 距離可及性 ÷ 高齡需求壓力）÷ 全市最高原始值
      <div class="v3">距離可及性 = max(0.10, 1 − 0.15×距離/10)。無床區先以「最近核心區床密度×距離可及性」作有效床密度，再取 ln 標準化；供給力 = 0.6×病床標準分 + 0.4×醫師標準分；需求壓力 = 老年率÷全市最高。9 組合理權重/衰減情境的最低排名相關 ρ = 0.987。</div>
    </div>

    <div class="legend">
      <span><i style="background:#CC6677"></i>無在地一般病床 · 跨區依賴</span>
      <span><i style="background:#EE7733"></i>高齡高 · 可及性低</span>
      <span><i style="background:#4477AA"></i>高齡高 · 可及性中高</span>
      <span><i style="background:#AA4499"></i>需求較低 · 可及性仍低</span>
      <span><i style="background:#228833"></i>相對平衡</span>
    </div>

    <figure>
      <img src="assets/choropleth_continuous.png" alt="台中市醫療可及性連續色階熱力圖">
      <figcaption>空間分布（連續色階 · 色覺友善 cividis）：色越深可及性越低，和平與山線最深，海線梧棲、沙鹿最亮。</figcaption>
    </figure>

    <figure>
      <img src="assets/observed_conflict.png" alt="醫療供給與高齡需求的獨立行政資料檢驗">
      <figcaption>猜想 vs 行政資料：病床密度沒有隨高齡率增加（r=-0.09, p=.633）；高齡率越高的區，代理距離反而越遠（r=+.41, p=.027）。相關不等於因果。</figcaption>
    </figure>

    <figure>
      <img src="assets/scatter_quadrant.png" alt="高齡率與可及性指數四象限散點圖">
      <figcaption>高齡率 × 可及性指數：右下象限（高齡高、可及性低）為高風險區，和平、東勢、新社、石岡落於此。各區為離散點、不以折線連接，避免製造假連續趨勢。</figcaption>
    </figure>

    <figure>
      <img src="assets/pressure_bar.png" alt="各區每床急診壓力與承載假設">
      <figcaption>急診壓力分開解讀：有床區呈現「官方一般床位＋推估需求」的混合壓力；零床區呈現跨區代理距離。一般病床不是急診實際承載量。</figcaption>
    </figure>

    <div class="grid2">
      <div>
        <h3 style="font-size:16px;margin-bottom:6px">各區可及性指數排名（點任一列看診斷）</h3>
        <table>
          <thead><tr>
            <th class="r">#</th><th>行政區</th><th class="r">指數</th>
            <th>因子分解 供給/需求/可及</th><th class="r">高齡率</th><th class="r">距大醫院</th>
          </tr></thead>
          <tbody id="tbl"></tbody>
        </table>
      </div>
      <div>
        <div class="panel" id="panel"></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap reveal">
    <div class="eyebrow">資源錯置的證據</div>
    <div class="h-step"><b>謀</b><h2>跨區就醫流向</h2></div>
    <p class="lede">10 個行政區在資料中無開放一般病床。下列流向依最近區域級以上醫院所在區推估，用來提出待驗證的後送假說，不代表居民實際移動。</p>
    <iframe class="sankey" src="assets/sankey.html" title="跨區就醫流向桑基圖" loading="lazy"></iframe>
    <figcaption style="font-size:12px;color:var(--faint);margin-top:9px">流向依「最近區域級以上醫院」估算，為結構推估，非健保實際就醫移動紀錄。</figcaption>
  </div>
</section>

<section>
  <div class="wrap reveal">
    <div class="eyebrow">A Answer</div>
    <div class="h-step"><b>斷</b><h2>該誰做、何時介入</h2></div>
    <p class="lede">點擊上方任一行政區，可查看證據等級、現況診斷與應蒐集的真實成效指標。長期設施評估與短期服務補位應平行推進，不用模型分數取代居民結果。</p>
    <div class="scn">
      <div class="card star">
        <div class="tag">長期決策門檻</div>
        <h3>情境 A · 山線急重症固定據點可行性評估</h3>
        <p>衛生局主責，會同區域醫療網、消防局與潛在營運院方；6 個月完成需求、選址、人力與財務評估。</p>
        <div class="eff">以 119 實際到院時間、跨區轉送率與急重症病例量決定是否進入建置，不預設一定蓋醫院。</div>
      </div>
      <div class="card">
        <div class="tag s2">立即平行啟動</div>
        <h3>情境 B · 山線巡迴與遠距轉診試辦</h3>
        <p>衛生局與在地衛生所/醫院於 3 個月內上路，先建立基線再追蹤 6 個月。</p>
        <div class="eff">KPI：服務覆蓋率、實際使用率、轉診完成率、到院時間與非計畫急診；未達標則增班或設固定據點。</div>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap reveal">
    <h3>資料來源</h3>
    <p class="src">主要本地檔案：臺中市115年5月人口結構、臺中市醫院一般病床數、64家醫院分級名冊（115-01-07）、臺中地區113年醫療職位統計、113年縣市別急診就醫概況、g0v/twgeojson 行政區界線。完整檔名、年度、欄位與方法限制收錄於書面報告。</p>
    <h3 style="margin-top:22px">誠實註記（方法論限制）</h3>
    <ul>
      <li>急診原始資料僅為全市/縣市層級；分區急診需求係以費米加權（高齡權重 ×3）推估分配，非各區實測值。</li>
      <li>急診資料年（2024）與人口資料年（2026）不一致，趨勢推估固定總人口、僅讓高齡結構演進。</li>
      <li>就醫距離採行政區中心點直線距離代理，非 Google Maps 行車距離（無 API key）。</li>
      <li>以開放一般病床數對照推估急診需求，是混合壓力指標；一般病床不等於急診檢傷、留觀或人力承載。</li>
      <li>清水、石岡標示為「跨區依賴」係因其院所為精神/慢性療養醫院，一般急性病床為 0，非全無醫療設施。</li>
      <li>跨區就醫流向為結構估算，非健保實際就醫移動紀錄。</li>
    </ul>
  </div>
</footer>

<script>
const DATA = __DATA__;
const PAL = {crisis:'#C0392B',warn:'#B9770E',mid:'#3A7CA5',good:'#1F5C8B'};
const tbody = document.getElementById('tbl');
const panel = document.getElementById('panel');

function stack(sup,dem,acc){
  const t = sup+dem+acc;
  const w = v => (v/t*100).toFixed(1)+'%';
  return `<div class="stack" title="供給 ${sup} / 需求 ${dem} / 可及 ${acc}">
    <i style="width:${w(sup)};background:${PAL.mid}"></i>
    <i style="width:${w(dem)};background:${PAL.crisis}"></i>
    <i style="width:${w(acc)};background:${PAL.warn}"></i></div>`;
}
DATA.forEach(r=>{
  const km = r.km===0 ? '就近' : r.km.toFixed(1)+' km';
  const proxy = r.data_complete!=='complete' ? '<span class="badge proxy">代理</span>' : '';
  const tr = document.createElement('tr');
  tr.dataset.d = r.district;
  tr.innerHTML = `<td class="r" style="color:var(--faint)">${r.rank}</td>
    <td>${r.district}${proxy}</td>
    <td class="r"><span class="score">${r.v3.toFixed(1)}</span></td>
    <td>${stack(r.sup,r.dem,r.acc)}</td>
    <td class="r" style="color:${r.elderly>=24?PAL.crisis:'inherit'}">${r.elderly.toFixed(1)}%</td>
    <td class="r" style="color:${r.km>15?PAL.crisis:'inherit'}">${km}</td>`;
  tr.onclick = ()=>select(r.district);
  tbody.appendChild(tr);
});

function facBar(label,v){
  return `<div class="fac"><span style="width:34px">${label}</span>
    <span class="bar"><i style="width:${(v*100).toFixed(0)}%;background:${PAL.mid}"></i></span>
    <span class="pv">${v.toFixed(2)}</span></div>`;
}
function select(d){
  const r = DATA.find(x=>x.district===d);
  document.querySelectorAll('#tbl tr').forEach(t=>t.classList.toggle('on',t.dataset.d===d));
  const capColor = r.flag_color;
  panel.innerHTML = `
    <div class="pd"><h3>${r.district}</h3><span class="rk">可及性指數 第 ${r.rank} / 29 名</span></div>
    <span class="cap" style="background:${capColor}1A;color:${capColor}">${r.flag}</span>
    <div style="font-size:11.5px;color:var(--faint);margin-top:8px">證據等級：${r.evidence_tier}</div>
    <div class="big">
      <div>可及性指數<b style="color:${PAL.mid}">${r.v3.toFixed(1)}</b></div>
      <div>高齡率<b>${r.elderly.toFixed(1)}%</b></div>
      <div>代理距離<b>${r.km===0?'同區':r.km.toFixed(1)+'km'}</b></div>
    </div>
    <div class="facs">
      ${facBar('供給',r.sup)}${facBar('需求',r.dem)}${facBar('可及',r.acc)}
    </div>
    <div style="font-size:12.5px;color:var(--muted)">急診需求 2024→2035：<b class="num" style="color:var(--ink)">${r.demand_2024.toLocaleString()}</b> → <b class="num" style="color:var(--ink)">${r.demand_2035.toLocaleString()}</b> 人次（+${r.growth}%）</div>
    <div class="diag">
      <div class="row"><div class="k">現況診斷</div><div class="t">${r.diag.situation}</div></div>
      <div class="row"><div class="k">介入建議 · 謀</div><div class="t">${r.diag.plan}</div></div>
      <div class="row"><div class="k">驗證指標 · 斷</div><div class="t">${r.diag.decide}</div></div>
    </div>`;
}
select('和平區');

const io = new IntersectionObserver((es)=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
</script>
</body>
</html>"""

repl = {
    "__DATA__": json.dumps(DATA, ensure_ascii=False),
    "__LICENSED_BEDS__": f"{KPI['licensed_general_beds']:,}",
    "__OPEN_BEDS__": f"{KPI['open_general_beds']:,}",
    "__OPEN_PER10K__": f"{KPI['open_beds_per_10k']:.1f}",
    "__OLD_D__": KPI["oldest"]["district"], "__OLD_E__": f"{KPI['oldest']['elderly_rate_pct']:.1f}",
    "__BEITUN__": f"{KPI['beitun']['estimated_pressure']:,.0f}", "__BEITUN_B__": f"{KPI['beitun']['open_general_beds']}",
    "__HEPING__": f"{KPI['heping_proxy_distance_km']:.1f}", "__NOLOCAL__": str(KPI["zero_open_general_bed_districts"]),
}
for k, v in repl.items():
    HTML = HTML.replace(k, v)

for filename in ("dashboard.html", "index.html"):
    (DASH / filename).write_text(HTML, encoding="utf-8")
print("wrote dashboard.html + index.html", len(HTML), "bytes each")
print("inlined", len(DATA), "districts")
