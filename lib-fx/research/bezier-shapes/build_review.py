"""Writes review.html (the Swirl Slash Shapes artifact page) from preview2/data.json and preview/data.json."""
import json
from pathlib import Path
HERE = Path(__file__).parent
d2 = json.loads((HERE / "preview3/data.json").read_text())
sm = json.loads((HERE / "out3/smoothness_f3-5.json").read_text())
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
table.metrics{{border-collapse:collapse;font:13px var(--mono);font-variant-numeric:tabular-nums;min-width:560px;width:100%}}
table.metrics caption{{text-align:left;font:13px var(--body);color:var(--muted);padding-bottom:8px;caption-side:top}}
table.metrics th,table.metrics td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left}}
table.metrics thead th{{color:var(--muted);font-weight:500}}
table.metrics td:last-child{{color:var(--ok)}}
.vtag{{font:500 11px var(--mono);padding:2px 7px;border-radius:99px;border:1px solid var(--line);color:var(--muted);margin-left:6px;vertical-align:2px}}
</style>
<div class="wrap">
<header style="display:flex;flex-direction:column;gap:10px">
  <span class="eyebrow">lib-fx / research / bezier-shapes · bản v3: tự làm đều nét</span>
  <h1>Swirl Slash Shapes</h1>
  <p class="lead">V3 thêm bước tự làm đều nét theo kiểu Illustrator: nối nét, giữ góc thật, làm trơn độ cong, gộp đoạn và bỏ điểm neo thừa. Hình và màu giữ như v2. Bản v2 và v1 ở cuối trang.</p>
  <p class="lead"><strong>Cập nhật băng (mượt tối đa):</strong> bỏ đường tối giữa lưỡi trắng và ngọn lửa xanh (đo lại thì đó chỉ là 2 px pha màu, không phải nét), bỏ viền sáng lấm tấm quanh mép, làm trơn mạnh hơn (σ 7 px), gộp đoạn dài hơn và nối khe tới 2,5 px.</p>
</header>

<section id="changes">
  <div><span class="eyebrow">Đã thêm gì</span><h2>Tự làm đều nét (Smooth &amp; Simplify)</h2>
  <p>Ghép từ cách Illustrator (Simplify: độ bám đường và ngưỡng góc), Potrace / Image Trace (ngưỡng góc và gộp đoạn cong) và lý thuyết "fair curve" (đường đẹp là đường có độ cong đổi ít nhất). Mỗi viền đi qua 6 bước:</p></div>
  <div class="changes">
    <div class="change"><h3>1 · Nối nét</h3><p>Khe hở dưới 1,5 px trong cùng một lớp được nối liền, mảnh vụn bị bỏ, giống lệnh Join.</p></div>
    <div class="change"><h3>2 · Giữ góc thật</h3><p>Một điểm chỉ là góc khi nó nhọn ở cả hai tầm nhìn: sát (±4 px) và rộng (±8 px). Răng cưa nhỏ chỉ nhọn ở tầm sát nên bị loại.</p></div>
    <div class="change"><h3>3 · Làm trơn độ cong</h3><p>Giữa hai góc, đường được kéo sao cho độ cong thay đổi ít nhất, như kéo một thanh dẻo qua các điểm (bend tool). Phần diện tích bị co được bù lại.</p></div>
    <div class="change"><h3>4–5 · Ít điểm neo</h3><p>Đường được fit bằng Bézier, rồi hai đoạn liền nhau được gộp làm một khi đoạn gộp vẫn bám đường trong 0,9 px. Góc nào gãy dưới 35° thì nắn thành neo trơn.</p></div>
    <div class="change"><h3>6 · Tay nắm gọn</h3><p>Tay nắm dài tối đa 0,45 lần dây cung (đường vẽ tay đo được 0,21–0,38), nên không sinh vòng hay phình.</p></div>
  </div>
  <div style="overflow-x:auto"><table class="metrics">
    <caption>Đo trung bình trên frame 3–5. Gốc: điểm neo / độ biến thiên độ cong của đường vẽ tay. v2, v3: điểm neo / điểm gãy / độ biến thiên độ cong. Điểm gãy là neo bị gấp 5–35°, không trơn mà cũng không phải góc. Độ biến thiên càng thấp, đường càng đều.</caption>
    <thead><tr><th>Lớp</th><th>Gốc (vẽ tay)</th><th>v2</th><th>v3</th></tr></thead>
    <tbody>@@ROWS@@</tbody></table></div>
</section>

<section id="motion">
  <div><span class="eyebrow">1 · Chuyển động v3</span><h2>Gộp các frame dựng lại</h2>
  <p>Trái là bản gốc, phải là v3. Bấm "Gốc | v2 | v3" để thấy bản trước ở giữa. Mỗi frame vẫn được dựng độc lập.</p></div>
  <div class="bar" role="group" aria-label="So sánh">
    <button class="cmp" data-c="side" aria-pressed="true">Gốc | v3</button>
    <button class="cmp" data-c="v2v3" aria-pressed="false">Gốc | v2 | v3</button>
    <button class="cmp" data-c="v3" aria-pressed="false">Chỉ v3</button>
    <span style="width:12px"></span>
    <button class="speed" data-s="" aria-pressed="true">25 fps (gốc)</button>
    <button class="speed" data-s="_slow" aria-pressed="false">8 fps (chậm)</button>
  </div>
  <div class="gifgrid">
    <figure><img class="gif" data-v="fire" src="preview3/fire_side.gif" alt="Lửa: gốc và v3"><figcaption>Lửa · frame 2–12</figcaption></figure>
    <figure><img class="gif" data-v="frost" src="preview3/frost_side.gif" alt="Băng: gốc và v3"><figcaption>Băng · frame 2–9</figcaption></figure>
  </div>
</section>

<section id="shapes">
  <div><span class="eyebrow">2 · Từng shape theo frame (v3)</span><h2>Duyệt từng lớp màu</h2>
  <p>Ảnh frame: gốc · v2 hình phẳng · v3 hình phẳng · v3 hoàn chỉnh (gradient và quầng sáng). Mỗi lớp có ba ô: mục tiêu · v3 hình phẳng · đường pen v3. Phím ← → để chuyển frame. Bấm Đạt / Cần sửa, ghi chú, rồi bấm "Sao chép nhận xét" để gửi lại.</p></div>
  <div class="bar" role="group" aria-label="Biến thể">
    <button class="variant" data-v="fire" aria-pressed="true">Lửa</button>
    <button class="variant" data-v="frost" aria-pressed="false">Băng</button>
  </div>
  <div class="bar" id="frames" role="group" aria-label="Frame"></div>
  <figure><div class="heads" style="--n:4"><span>gốc</span><span>v2 phẳng</span><span>v3 phẳng</span><span>v3 hoàn chỉnh</span></div><img id="frameimg" alt="Frame: gốc, v1, v2"><figcaption id="framecap"></figcaption></figure>
  <div class="legend"><span><i style="background:#f0f0f0"></i>neo trơn</span><span><i style="background:#ff4646"></i>neo góc (mũi nhọn)</span><span>ngưỡng IoU: lớp lớn ≥ 0,85 · lớp nhỏ ≥ 0,70</span></div>
  <div id="layers" style="display:flex;flex-direction:column;gap:16px"></div>
  <div class="bar"><button id="copy">Sao chép nhận xét</button><span id="copied" aria-live="polite"></span></div>
  <textarea id="copybox" hidden readonly style="width:100%;min-height:120px;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:8px;font:12px var(--mono)"></textarea>
</section>

<section id="v1">
  <details>
    <summary>Bản cũ: v2 (gradient + tô chồng) và v1</summary>
    <div style="display:flex;flex-direction:column;gap:16px">
      <div class="gifgrid">
        <figure><img src="preview2/fire_v1v2.gif" alt="Gốc, v1, v2 lửa" loading="lazy"><figcaption>Lửa · gốc | v1 | v2</figcaption></figure>
        <figure><img src="preview2/frost_v1v2.gif" alt="Gốc, v1, v2 băng" loading="lazy"><figcaption>Băng · gốc | v1 | v2</figcaption></figure>
      </div>
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
const KEY = "swirl-review-v3";
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
  document.getElementById("frameimg").src = `preview3/${{v}}_${{f}}_frame.png`;
  document.getElementById("framecap").textContent = `${{v === "fire" ? "Lửa" : "Băng"}} · frame ${{+f}}`;
  const box = document.getElementById("layers"); box.innerHTML = "";
  const L = DATA[v].frames[f].layers;
  if (!Object.keys(L).length) box.innerHTML = '<p>Frame này không còn lớp màu nào.</p>';
  for (const [l, d] of Object.entries(L)) {{
    const key = `${{v}}/${{f}}/${{l}}`, r = rev[key] || {{}};
    const el = document.createElement("article"); el.className = "layer";
    el.innerHTML = `
      <div class="layer-top"><h3><span class="sw" style="background:${{PAL[v][l]}}"></span>${{NAMES[l]}} <span class="eyebrow">· ${{BIG.has(l) ? "lớp lớn" : "lớp nhỏ"}}</span></h3>
        <div class="chips"><span class="chip ${{pass(l, d.iou) ? "pass" : "fail"}}">IoU ${{fmt(d.iou)}}</span><span class="chip">${{d.anchors}} điểm neo</span><span class="chip">${{d.corners}} góc nhọn</span><span class="chip">${{d.kinks}} điểm gãy</span><span class="chip">độ cong đổi ${{fmt(d.curv_var)}}</span></div></div>
      <div class="heads" style="--n:3"><span>mục tiêu</span><span>v3 hình phẳng (cả frame)</span><span>đường pen v3 của lớp</span></div>
      <img src="preview3/${{d.img}}" alt="${{NAMES[l]}} frame ${{+f}}" loading="lazy" style="width:100%;height:auto;border-radius:6px;display:block">
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
function gifs(){{document.querySelectorAll("img.gif").forEach(g => g.src = `preview3/${{g.dataset.v}}_${{cmp}}${{spd}}.gif`)}}
document.querySelectorAll(".cmp").forEach(b => b.onclick = () => {{cmp = b.dataset.c; document.querySelectorAll(".cmp").forEach(x => x.setAttribute("aria-pressed", x === b)); gifs()}});
document.querySelectorAll(".speed").forEach(b => b.onclick = () => {{spd = b.dataset.s; document.querySelectorAll(".speed").forEach(x => x.setAttribute("aria-pressed", x === b)); gifs()}});
document.getElementById("copy").onclick = () => {{
  const lines = Object.entries(rev).filter(([k, r]) => r.r || (r.n && r.n.trim()))
    .map(([k, r]) => {{const [vv, ff, l] = k.split("/"); return `v3 ${{vv}} f${{+ff}} ${{l}}: ${{r.r === "ok" ? "ĐẠT" : r.r === "fix" ? "CẦN SỬA" : "-"}}${{r.n && r.n.trim() ? " — " + r.n.trim() : ""}}`}});
  const txt = lines.length ? lines.join("\\n") : "(chưa có nhận xét)";
  const box = document.getElementById("copybox"), msg = document.getElementById("copied");
  box.value = txt;
  const fallback = () => {{box.hidden = false; box.select(); msg.textContent = "Không sao chép tự động được: chọn và copy ở ô bên dưới."}};
  try {{navigator.clipboard.writeText(txt).then(() => {{msg.textContent = `Đã sao chép ${{lines.length}} nhận xét.`}}, fallback)}} catch (e) {{fallback()}}
}};
draw();
</script>
'''
rows = "".join(
    f'<tr><th scope="row">{"Lửa" if k.split("/")[0] == "fire" else "Băng"} · {NAMES[k.split("/")[1]]}</th>'
    f'<td>{r["orig"][0]:.0f} / {r["orig"][2]:.2f}</td><td>{r["v2"][0]:.0f} / {r["v2"][1]:.1f} / {r["v2"][2]:.2f}</td>'
    f'<td>{r["v3"][0]:.0f} / {r["v3"][1]:.1f} / {r["v3"][2]:.2f}</td></tr>' for k, r in sm.items())
html = html.replace("@@ROWS@@", rows)
(HERE / "review.html").write_text(html)
print("review.html", len(html))
