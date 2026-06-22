# -*- coding: utf-8 -*-
"""Assemble the self-contained single-page dashboard.
Data is inlined (no fetch) so it runs offline from file:// for the live demo.
ponytail: one hand-written HTML file, no framework, no build step."""
import json
from pathlib import Path

DASH = Path(r"C:\Vision\outputs\dashboard")
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
  --crisis:#A32D2D; --warn:#BA7517; --mid:#185FA5; --good:#0F6E56;
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
    <div class="kicker">台中市衛生局決策視覺化 · HAAI 醫療可及性缺口指數</div>
    <h1>醫療繁榮的假象</h1>
    <p class="sub">台中市醫療量能名列全台前三，但把 29 個行政區的「資源供給」攤開對上「老化需求」與「就醫距離」，最需要醫療的人，反而最難就醫。</p>
    <div class="kpis">
      <div class="kpi k-good"><div class="lab">全市開放病床</div><div class="val num">__BEDS__<small>床</small></div><div class="meta">醫療量能名列全台前三</div></div>
      <div class="kpi k-warn"><div class="lab">最高齡行政區</div><div class="val">__OLD_D__ <small class="num">__OLD_E__%</small></div><div class="meta">已超過超高齡社會 20% 門檻</div></div>
      <div class="kpi k-crisis"><div class="lab">北屯區每床急診壓力</div><div class="val num">__BEITUN__<small>人次/床</small></div><div class="meta">僅 __BEITUN_B__ 床 · 結構性資源錯配</div></div>
      <div class="kpi k-crisis"><div class="lab">和平區距最近醫學中心</div><div class="val num">__HEPING__<small>公里</small></div><div class="meta">__NOLOCAL__ 區無在地急診資源</div></div>
    </div>
  </div>
</header>

<section>
  <div class="wrap reveal">
    <div class="eyebrow">S Situation</div>
    <div class="h-step"><b>見</b><h2>先看見繁榮</h2></div>
    <p class="lede">台中市擁有中國醫大附醫、中山醫大附醫、台中榮總三大醫學中心，醫療院所超過 3,600 家，全市平均每萬人病床數約 58 床、高於全台平均。單看總量，這是一座醫療資源充裕的城市。問題不在總量，在於它落在哪裡。</p>
  </div>
</section>

<section>
  <div class="wrap reveal">
    <div class="eyebrow">C Complication · Q Question</div>
    <div class="h-step"><b>識</b><h2>揭穿假象：HAAI 缺口指數</h2></div>
    <p class="lede">HAAI 把每一區的「供給力」除以「需求壓力與就醫距離」，量化各區的醫療可及性。分數越低，代表越是「需求高、可及性低」的高風險區。</p>
    <div class="formula">
      HAAI（費米式）=（每萬人病床數 × 醫師密度係數）÷（老年人口比率 × 就醫距離衰減因子）
      <div class="v3">下方圖表採 V3 正規化版（0–100，偏態 1.36→0.13 修正後），將供給、需求、可及三因子標準化，避免小人口區的人均值灌爆排名。</div>
    </div>

    <div class="legend">
      <span><i style="background:var(--crisis)"></i>跨區依賴 · 無在地急診床</span>
      <span><i style="background:var(--warn)"></i>高齡高 · HAAI 低</span>
      <span><i style="background:var(--mid)"></i>高齡高 · HAAI 中高</span>
      <span><i style="background:var(--good)"></i>相對平衡</span>
    </div>

    <figure>
      <img src="assets/01_choropleth.png" alt="台中市各區 HAAI 旗標分色熱力圖">
      <figcaption>空間分布：紅色「醫療沙漠」集中於山線與海線外圍，綠色「相對平衡」集中於市中心與屯區。</figcaption>
    </figure>

    <figure>
      <img src="assets/02_dual_axis_v3.png" alt="高齡率與 HAAI V3 分數雙軸長條圖，依高齡率排序">
      <figcaption>長條＝高齡率（依高齡率由高到低排序），折線＝HAAI V3 分數。左側高齡最重的東勢、石岡、新社、和平，HAAI 反而墊底，落差就是洞察核心。</figcaption>
    </figure>

    <div class="grid2">
      <div>
        <h3 style="font-size:16px;margin-bottom:6px">各區 HAAI V3 排名（點任一列看診斷）</h3>
        <table>
          <thead><tr>
            <th class="r">#</th><th>行政區</th><th class="r">V3</th>
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
    <p class="lede">10 個無在地急診資源的行政區，居民必須跨區就醫。桑基圖呈現各區「往哪裡流」與流量規模，紅色越粗代表越多急診需求被推往鄰近核心區。</p>
    <iframe class="sankey" src="assets/sankey.html" title="跨區就醫流向桑基圖" loading="lazy"></iframe>
    <figcaption style="font-size:12px;color:var(--faint);margin-top:9px">流向依「最近區域級以上醫院」估算，為結構推估，非健保實際就醫移動紀錄。</figcaption>
  </div>
</section>

<section>
  <div class="wrap reveal">
    <div class="eyebrow">A Answer</div>
    <div class="h-step"><b>斷</b><h2>該誰做、何時介入</h2></div>
    <p class="lede">點擊上方任一行政區，即時輸出該區的現況診斷、介入建議與驗證指標。以下為兩個全市層級的優先情境（規劃書推估值）。</p>
    <div class="scn">
      <div class="card star">
        <div class="tag">★ 最高效益</div>
        <h3>情境 A · 於東勢設立區域醫院 1 家</h3>
        <p>補上山線四區最大的供給缺口。</p>
        <div class="eff">HAAI 指數提升約 42%，覆蓋人口約 3.8 萬人</div>
      </div>
      <div class="card">
        <div class="tag s2">短期應急</div>
        <h3>情境 B · 增加山線巡迴醫療班次</h3>
        <p>不需建院，先改善就醫距離衰減。</p>
        <div class="eff">距離衰減因子改善約 20%，成本僅情境 A 的 1/10</div>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap reveal">
    <h3>資料來源</h3>
    <p class="src">台中市 Open Data 醫院基本資料、衛福部醫院一般病床數、台中市民政局人口結構、衛福部醫療機構人員統計、衛福部縣市別急診就醫概況、g0v/twgeojson 行政區界線。HAAI 建模與分區急診推估由本組計算。</p>
    <h3 style="margin-top:22px">誠實註記（方法論限制）</h3>
    <ul>
      <li>急診原始資料僅為全市/縣市層級；分區急診需求係以費米加權（高齡權重 ×3）推估分配，非各區實測值。</li>
      <li>急診資料年（2024）與人口資料年（2026）不一致，趨勢推估固定總人口、僅讓高齡結構演進。</li>
      <li>就醫距離採行政區中心點直線距離代理，非 Google Maps 行車距離（無 API key）。</li>
      <li>清水、石岡標示為「跨區依賴」係因其院所為精神/慢性療養醫院，一般急性病床為 0，非全無醫療設施。</li>
      <li>跨區就醫流向為結構估算，非健保實際就醫移動紀錄。</li>
    </ul>
  </div>
</footer>

<script>
const DATA = __DATA__;
const PAL = {crisis:'#A32D2D',warn:'#BA7517',mid:'#185FA5',good:'#0F6E56'};
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
  const crisis = r.flag.includes('跨區')||r.flag.includes('無在地');
  const capColor = crisis?PAL.crisis:(r.flag.includes('低')?PAL.warn:(r.flag.includes('中高')?PAL.mid:PAL.good));
  panel.innerHTML = `
    <div class="pd"><h3>${r.district}</h3><span class="rk">HAAI 第 ${r.rank} / 29 名</span></div>
    <span class="cap" style="background:${capColor}1A;color:${capColor}">${r.capacity||r.flag}</span>
    <div class="big">
      <div>V3 分數<b style="color:${PAL.mid}">${r.v3.toFixed(1)}</b></div>
      <div>高齡率<b>${r.elderly.toFixed(1)}%</b></div>
      <div>距大醫院<b>${r.km===0?'就近':r.km.toFixed(1)+'km'}</b></div>
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
    "__BEDS__": f"{KPI['total_beds']:,}",
    "__OLD_D__": KPI["oldest"]["d"], "__OLD_E__": f"{KPI['oldest']['el']:.1f}",
    "__BEITUN__": f"{KPI['beitun_pressure']:,}", "__BEITUN_B__": f"{KPI['beitun_beds']}",
    "__HEPING__": f"{KPI['heping_km']:.1f}", "__NOLOCAL__": str(KPI["no_local_count"]),
}
for k, v in repl.items():
    HTML = HTML.replace(k, v)

(DASH / "dashboard.html").write_text(HTML, encoding="utf-8")
print("wrote dashboard.html", len(HTML), "bytes")
print("inlined", len(DATA), "districts")
