"""Writes review.html (the Swirl Slash Shapes artifact page) from preview2/data.json and preview/data.json."""
import json
from pathlib import Path
HERE = Path(__file__).parent
d2 = json.loads((HERE / "preview2/data.json").read_text())
d1 = json.loads((HERE / "preview/data.json").read_text())
style = (HERE / "review_style.css").read_text()
NAMES = {"yellow": "vàng (gồm dải cam ở mép)", "pink": "hồng", "crimson": "đỏ sẫm", "amber": "hổ phách",
         "ice": "trắng (lưỡi băng)", "cyan": "cyan (lông vũ)", "mid": "xanh (ngọn lửa xanh)", "deep": "xanh sẫm (viền)"}
PAL = {"fire": {"yellow": "#ffd670", "amber": "#feac4c", "pink": "#ff628c", "crimson": "#d12f57"},
       "frost": {"ice": "#efffff", "cyan": "#69e7fe", "mid": "#3ba9e2", "deep": "#1e6d9d"}}
html = f'''<title>Swirl Slash Shapes</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
{style}
<style>
.changes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:14px}}
.change{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px;display:flex;flex-direction:column;gap:6px;min-width:0}}
.change p{{color:var(--fg);opacity:.82;font-size:14px}}
details{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 14px}}
details summary{{cursor:pointer;font:600 15px var(--body)}}
details[open] summary{{margin-bottom:14px}}
.vtag{{font:500 11px var(--mono);padding:2px 7px;border-radius:99px;border:1px solid var(--line);color:var(--muted);margin-left:6px;vertical-align:2px}}
</style>
<div class="wrap">
<header style="display:flex;flex-direction:column;gap:10px">
  <span class="eyebrow">lib-fx / research / bezier-shapes · bản sửa v2</span>
  <h1>Swirl Slash Shapes</h1>
  <p class="lead">Bản v2 sửa theo hai nhận xét: nét lổm chổm, gấp khúc và thiếu gradient. Xem chuyển động trước, sau đó duyệt từng lớp theo frame. Bản v1 vẫn ở cuối trang để so sánh.</p>
</header>

<section id="changes">
  <div><span class="eyebrow">Đã sửa gì</span><h2>Ba thay đổi chính</h2></div>
  <div class="changes">
    <div class="change"><h3>Đọc lại đúng hình gốc</h3><p>Lớp vàng và lưỡi trắng có một dải chuyển màu sát mép (vàng sang cam, trắng sang xanh nhạt). Mặt nạ v1 chỉ lấy đúng mã màu nên làm mất dải đó: lớp vàng hụt khoảng 30% diện tích, lưỡi lửa hồng mất mũi, và giữa các lớp còn khe tối. V2 coi dải mép là một phần của chính lớp đó, còn "hổ phách" thật ra là dải mép của lớp vàng.</p></div>
    <div class="change"><h3>Vẽ lại bằng "pen tool"</h3><p>Các lớp được tô chồng lên nhau theo thứ tự. Lớp dưới chạy liền một khối bên dưới lớp trên, nên hết khe và hết mối nối. Sau đó mỗi lớp được vẽ lại thành ít đường cong trơn, chỉ giữ điểm gãy ở mũi nhọn thật. Ô "đường pen" bên dưới cho thấy điểm neo: trắng là neo trơn, đỏ là góc nhọn.</p></div>
    <div class="change"><h3>Gradient và quầng sáng</h3><p>Gradient trong lớp đo từ bản gốc: vàng ngả sang cam (255,163,69) trong khoảng 8 px sát mép, trắng ngả sang xanh nhạt trong khoảng 3 px. Quầng sáng phía sau lan theo khoảng cách tới hình (lửa: đỏ, giảm một nửa sau khoảng 26 px; băng: xanh, sau khoảng 19 px).</p></div>
  </div>
</section>

<section id="motion">
  <div><span class="eyebrow">1 · Chuyển động v2</span><h2>Gộp các frame dựng lại</h2>
  <p>Trái là bản gốc, phải là v2. Bấm "Gốc | v1 | v2" để thấy bản cũ ở giữa. Mỗi frame vẫn được dựng độc lập, chưa ràng buộc giữa các frame.</p></div>
  <div class="bar" role="group" aria-label="So sánh">
    <button class="cmp" data-c="side" aria-pressed="true">Gốc | v2</button>
    <button class="cmp" data-c="v1v2" aria-pressed="false">Gốc | v1 | v2</button>
    <button class="cmp" data-c="v2" aria-pressed="false">Chỉ v2</button>
    <span style="width:12px"></span>
    <button class="speed" data-s="" aria-pressed="true">25 fps (gốc)</button>
    <button class="speed" data-s="_slow" aria-pressed="false">8 fps (chậm)</button>
  </div>
  <div class="gifgrid">
    <figure><img class="gif" data-v="fire" src="preview2/fire_side.gif" alt="Lửa: gốc và v2"><figcaption>Lửa · frame 2–12</figcaption></figure>
    <figure><img class="gif" data-v="frost" src="preview2/frost_side.gif" alt="Băng: gốc và v2"><figcaption>Băng · frame 2–9</figcaption></figure>
  </div>
</section>

<section id="shapes">
  <div><span class="eyebrow">2 · Từng shape theo frame (v2)</span><h2>Duyệt từng lớp màu</h2>
  <p>Ảnh frame: gốc · v1 · v2 hình phẳng · v2 hoàn chỉnh (gradient và quầng sáng). Mỗi lớp có ba ô: mục tiêu · v2 hình phẳng · đường pen. Phím ← → để chuyển frame. Bấm Đạt / Cần sửa, ghi chú, rồi bấm "Sao chép nhận xét" để gửi lại.</p></div>
  <div class="bar" role="group" aria-label="Biến thể">
    <button class="variant" data-v="fire" aria-pressed="true">Lửa</button>
    <button class="variant" data-v="frost" aria-pressed="false">Băng</button>
  </div>
  <div class="bar" id="frames" role="group" aria-label="Frame"></div>
  <figure><div class="heads" style="--n:4"><span>gốc</span><span>v1</span><span>v2 hình phẳng</span><span>v2 hoàn chỉnh</span></div><img id="frameimg" alt="Frame: gốc, v1, v2"><figcaption id="framecap"></figcaption></figure>
  <div class="legend"><span><i style="background:#f0f0f0"></i>neo trơn</span><span><i style="background:#ff4646"></i>neo góc (mũi nhọn)</span><span>ngưỡng IoU: lớp lớn ≥ 0,85 · lớp nhỏ ≥ 0,70</span></div>
  <div id="layers" style="display:flex;flex-direction:column;gap:16px"></div>
  <div class="bar"><button id="copy">Sao chép nhận xét</button><span id="copied" aria-live="polite"></span></div>
  <textarea id="copybox" hidden readonly style="width:100%;min-height:120px;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:8px;font:12px var(--mono)"></textarea>
</section>

<section id="v1">
  <details>
    <summary>Bản v1 (trước review): ảnh so sánh và GIF cũ</summary>
    <div style="display:flex;flex-direction:column;gap:16px">
      <div class="cols">
        <figure><img src="compare_fire.png" alt="v1 lửa frame 3 đến 5" loading="lazy"><figcaption>v1 · Lửa, frame 3–5 (gốc | mục tiêu | dựng lại | lỗi)</figcaption></figure>
        <figure><img src="compare_frost.png" alt="v1 băng frame 3 đến 5" loading="lazy"><figcaption>v1 · Băng, frame 3–5</figcaption></figure>
      </div>
      <div class="gifgrid">
        <figure><img src="preview/fire_side.gif" alt="v1 lửa chuyển động" loading="lazy"><figcaption>v1 · Lửa · gốc | dựng lại</figcaption></figure>
        <figure><img src="preview/frost_side.gif" alt="v1 băng chuyển động" loading="lazy"><figcaption>v1 · Băng · gốc | dựng lại</figcaption></figure>
      </div>
      <figure style="max-width:760px"><img src="generated_demo.png" alt="Hình mới sinh từ luật" loading="lazy"><figcaption>Hình mới sinh từ luật (bản thử, chưa cập nhật theo v2)</figcaption></figure>
    </div>
  </details>
</section>
</div>
<script>
const DATA = {json.dumps(d2)};
const BIG = new Set(["yellow","pink","ice","mid"]);
const NAMES = {json.dumps(NAMES, ensure_ascii=False)};
const PAL = {json.dumps(PAL)};
let v = "fire", f = null, cmp = "side", spd = "";
const KEY = "swirl-review-v2";
const store = {{get(){{try{{return JSON.parse(localStorage.getItem(KEY)||"{{}}")}}catch(e){{return {{}}}}}},
               set(o){{try{{localStorage.setItem(KEY,JSON.stringify(o))}}catch(e){{}}}}}};
let rev = store.get();
const fmt = x => x.toFixed(3).replace(".", ",");
const frames = () => Object.keys(DATA[v].frames);
const pass = (l, iou) => iou >= (BIG.has(l) ? 0.85 : 0.70);
function drawFrames(){{
  const box = document.getElementById("frames"); box.innerHTML = "";
  frames().forEach(k => {{
    const L = DATA[v].frames[k].layers, ls = Object.keys(L);
    const b = document.createElement("button");
    b.className = "frame-btn" + (ls.length && ls.every(l => pass(l, L[l].iou)) ? " all-ok" : ls.some(l => !pass(l, L[l].iou)) ? " has-bad" : "");
    b.innerHTML = "f" + k + '<span class="dot"></span>';
    b.setAttribute("aria-pressed", k === f); b.onclick = () => {{f = k; draw()}};
    box.appendChild(b);
  }});
}}
function draw(){{
  if (!frames().includes(f)) f = frames().includes("04") ? "04" : frames()[0];
  document.querySelectorAll(".variant").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === v));
  drawFrames();
  document.getElementById("frameimg").src = `preview2/${{v}}_${{f}}_frame.png`;
  document.getElementById("framecap").textContent = `${{v === "fire" ? "Lửa" : "Băng"}} · frame ${{+f}}`;
  const box = document.getElementById("layers"); box.innerHTML = "";
  const L = DATA[v].frames[f].layers;
  if (!Object.keys(L).length) box.innerHTML = '<p>Frame này không còn lớp màu nào.</p>';
  for (const [l, d] of Object.entries(L)) {{
    const key = `${{v}}/${{f}}/${{l}}`, r = rev[key] || {{}};
    const el = document.createElement("article"); el.className = "layer";
    el.innerHTML = `
      <div class="layer-top"><h3><span class="sw" style="background:${{PAL[v][l]}}"></span>${{NAMES[l]}} <span class="eyebrow">· ${{BIG.has(l) ? "lớp lớn" : "lớp nhỏ"}}</span></h3>
        <div class="chips"><span class="chip ${{pass(l, d.iou) ? "pass" : "fail"}}">IoU ${{fmt(d.iou)}}</span><span class="chip">${{d.anchors}} điểm neo</span><span class="chip">${{d.corners}} góc nhọn</span><span class="chip">${{d.strokes}} nét công thức</span></div></div>
      <div class="heads" style="--n:3"><span>mục tiêu</span><span>v2 hình phẳng (cả frame)</span><span>đường pen của lớp</span></div>
      <img src="preview2/${{d.img}}" alt="${{NAMES[l]}} frame ${{+f}}" loading="lazy" style="width:100%;height:auto;border-radius:6px;display:block">
      <div class="review">
        <button class="rv" data-r="ok" aria-pressed="${{r.r === "ok"}}">Đạt</button>
        <button class="rv" data-r="fix" aria-pressed="${{r.r === "fix"}}">Cần sửa</button>
        <textarea id="note-${{v}}-${{f}}-${{l}}" placeholder="Ghi chú cho lớp này">${{r.n ? r.n.replace(/</g,"&lt;") : ""}}</textarea>
      </div>`;
    el.querySelectorAll(".rv").forEach(b => b.onclick = () => {{
      const cur = rev[key] || {{}}; cur.r = cur.r === b.dataset.r ? null : b.dataset.r; rev[key] = cur; store.set(rev);
      el.querySelectorAll(".rv").forEach(x => x.setAttribute("aria-pressed", x.dataset.r === cur.r));
    }});
    el.querySelector("textarea").oninput = e => {{const cur = rev[key] || {{}}; cur.n = e.target.value; rev[key] = cur; store.set(rev)}};
    box.appendChild(el);
  }}
}}
document.querySelectorAll(".variant").forEach(b => b.onclick = () => {{v = b.dataset.v; draw()}});
document.addEventListener("keydown", e => {{
  if (e.target.tagName === "TEXTAREA") return;
  const fs = frames(), i = fs.indexOf(f);
  if (e.key === "ArrowRight" && i < fs.length - 1) {{f = fs[i + 1]; draw()}}
  if (e.key === "ArrowLeft" && i > 0) {{f = fs[i - 1]; draw()}}
}});
function gifs(){{document.querySelectorAll("img.gif").forEach(g => g.src = `preview2/${{g.dataset.v}}_${{cmp}}${{spd}}.gif`)}}
document.querySelectorAll(".cmp").forEach(b => b.onclick = () => {{cmp = b.dataset.c; document.querySelectorAll(".cmp").forEach(x => x.setAttribute("aria-pressed", x === b)); gifs()}});
document.querySelectorAll(".speed").forEach(b => b.onclick = () => {{spd = b.dataset.s; document.querySelectorAll(".speed").forEach(x => x.setAttribute("aria-pressed", x === b)); gifs()}});
document.getElementById("copy").onclick = () => {{
  const lines = Object.entries(rev).filter(([k, r]) => r.r || (r.n && r.n.trim()))
    .map(([k, r]) => {{const [vv, ff, l] = k.split("/"); return `v2 ${{vv}} f${{+ff}} ${{l}}: ${{r.r === "ok" ? "ĐẠT" : r.r === "fix" ? "CẦN SỬA" : "-"}}${{r.n && r.n.trim() ? " — " + r.n.trim() : ""}}`}});
  const txt = lines.length ? lines.join("\\n") : "(chưa có nhận xét)";
  const box = document.getElementById("copybox"), msg = document.getElementById("copied");
  box.value = txt;
  const fallback = () => {{box.hidden = false; box.select(); msg.textContent = "Không sao chép tự động được: chọn và copy ở ô bên dưới."}};
  try {{navigator.clipboard.writeText(txt).then(() => {{msg.textContent = `Đã sao chép ${{lines.length}} nhận xét.`}}, fallback)}} catch (e) {{fallback()}}
}};
draw();
</script>
'''
(HERE / "review.html").write_text(html)
print("review.html", len(html))
