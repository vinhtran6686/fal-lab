"use strict";
// Lion Rig & Pose Studio client. Pixels come from the Puppet Kit (server /api/render); this file only draws overlays and edits data.

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else if (v !== null && v !== undefined && v !== false) e.setAttribute(k, v);
  }
  for (const c of kids.flat(Infinity)) if (c !== null && c !== undefined && c !== false) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
};
const clone = (o) => JSON.parse(JSON.stringify(o));
const r1 = (v) => Math.round(v * 10) / 10;
const fmt = (v) => (Number.isInteger(v) ? String(v) : String(Math.round(v * 10) / 10));
const DEF = { rot: 0, tx: 0, ty: 0, sx: 1, sy: 1, shx: 0 };
const CH = Object.keys(DEF);
const CH_VN = { rot: "Xoay", tx: "Dịch ngang", ty: "Dịch dọc", sx: "Co giãn ngang", sy: "Co giãn dọc", shx: "Nghiêng" };
const DRAFT = 0.3;
const DRAG_PX = 4;
const SEG = { upper_arm: "cánh tay", forearm: "cẳng tay", hand: "bàn tay", thigh: "đùi", shin: "cẳng chân", foot: "bàn chân", foot_target: "đích bàn chân", head: "đầu", spine: "thân trên", hips: "hông", tail: "đuôi", root: "gốc" };
const viName = (n) => { const m = n.match(/^(near|far)_(.+)$/); return (SEG[m ? m[2] : n] || (m ? m[2] : n)) + (m ? (m[1] === "near" ? " gần" : " xa") : ""); };
const DEFAULT_LIMITS = { upper_arm: [-170, 140], forearm: [-160, 80], hand: [-70, 70], thigh: [-90, 60], shin: [0, 150], foot: [-30, 30], head: [-40, 40], spine: [-20, 35], hips: [-15, 15], tail: [-70, 70] };

const S = {
  rig: null, saved: null, parts: [], rigFile: "rig.json", rigFiles: [], topology: "",
  pose: { bones: {}, ik: {} }, poseBase: '{"bones":{},"ik":{}}', poseId: null,
  tool: "pose", sel: null, selPart: null, editPart: null, selVert: null, libSel: null, libFocus: false,
  leftTab: "layers", rightTab: "pose", selLink: 0, hover: null, mouse: null, hitLimit: null,
  vis: { skeleton: true, labels: true, pivots: true, bounds: false, polys: false, skin: false, rigid: false, sockets: true, ik: true, links: true, limits: true, influence: true },
  hide: new Set(), rest: false, bg: "dark", grid: true, showChar: true, ghostRig: false,
  view: { zoom: 0.6, px: 0, py: 0 }, poses: [], rigSync: true, cutRev: 0,
  render: null, img: null, game: null, gameH: 60, bad: null,
  cmp: { on: false, a: "working", b: "rest", showing: "a", onion: true },
  undo: [], redo: [],
};
const chainOpt = { follow: 0.6, stretch: true, maxStretch: 1.35 };

// ---------------------------------------------------------------- api, toast, modal
async function api(path, body) {
  const r = await fetch(path, body === undefined ? {} : { method: "POST", headers: { "X-Studio": "1", "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json();
  if (!r.ok || j.error) throw new Error(j.error || r.statusText);
  return j;
}
function toast(msg, err = false, ms = 3500) {
  const t = $("#toast");
  t.textContent = msg; t.className = err ? "err" : ""; t.style.display = "block";
  clearTimeout(toast.t); toast.t = setTimeout(() => (t.style.display = "none"), ms);
}
function modal({ title, fields = [], text = "", ok = "OK", node = null, noCancel = false }) {
  return new Promise((res) => {
    const m = $("#modal"), body = $("#mBody");
    $("#mTitle").textContent = title; body.replaceChildren();
    if (text) body.append(el("p", {}, text));
    if (node) body.append(node);
    $("#mCancel").hidden = noCancel; $(".box").classList.toggle("wide", !!node);
    const inputs = fields.map((f) => {
      const i = f.area ? el("textarea", { rows: 3 }) : el("input", { type: "text" });
      i.value = f.value || ""; body.append(el("label", {}, f.label), i); return i;
    });
    const done = (v) => { m.hidden = true; $("#mOk").onclick = $("#mCancel").onclick = null; res(v); };
    $("#mOk").textContent = ok; $("#mOk").onclick = () => done(inputs.map((i) => i.value)); $("#mCancel").onclick = () => done(null);
    m.hidden = false; (inputs[0] || $("#mOk")).focus();
    if (inputs[0]) inputs[0].onkeydown = (e) => { if (e.key === "Enter" && !fields[0].area) $("#mOk").click(); if (e.key === "Escape") $("#mCancel").click(); };
  });
}

// ---------------------------------------------------------------- rig helpers
const bone = (n) => S.rig.bones.find((b) => b.name === n);
const children = (n) => S.rig.bones.filter((b) => b.parent === n);
const partOf = (n) => S.rig.parts.find((p) => p.name === n);
const sideColor = (n) => (n.startsWith("near_") ? "#ff9a3d" : n.startsWith("far_") ? "#5aa9ff" : "#4cd08a");
const world = (n) => (S.render && S.render.world[n]) || [1, 0, 0, 1, 0, 0];
const mapPt = (m, x, y) => [m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]];
const inv2 = (m) => { const d = m[0] * m[3] - m[1] * m[2] || 1e-9; return [m[3] / d, -m[1] / d, -m[2] / d, m[0] / d, 0, 0]; };
function invPt(m, x, y) { const i = inv2(m), dx = x - m[4], dy = y - m[5]; return [i[0] * dx + i[2] * dy, i[1] * dx + i[3] * dy]; }
const posedPivot = (n) => { const b = bone(n); return mapPt(world(n), b.pivot[0], b.pivot[1]); };
const isLeaf = (n) => !children(n).length;
function boneEndRest(n) {
  const c = children(n)[0];
  if (c) return { rest: c.pivot, from: `khớp con ${c.name}` };
  for (const p of S.rig.parts) if (p.skin && p.skin.bones[p.skin.bones.length - 1] === n) return { rest: p.skin.tip, from: `đầu mút của layer ${p.name}` };
  return null;
}
function boneEnd(n) { const e = boneEndRest(n); return e ? { pt: mapPt(world(n), e.rest[0], e.rest[1]), from: e.from, rest: e.rest } : null; }
const chVal = (n, ch) => ((S.pose.bones[n] || {})[ch] ?? DEF[ch]);
const ikOf = (n) => (S.rig.ik || []).find((i) => i.upper === n || i.lower === n || i.end_bone === n);
const ikOn = (ik) => S.pose.ik[ik.upper] !== false;
const ikDriven = (n) => { const i = ikOf(n); return !!i && ikOn(i); };
const footTarget = (ik) => (ik && ik.target.bone !== "root" ? ik.target.bone : null);
const ikTargetWorld = (ik) => mapPt(world(ik.target.bone), ik.target.pt[0], ik.target.pt[1]);
const linkOf = (arm) => (S.rig.links || []).find((l) => l.arm === arm);
const rigDirty = () => JSON.stringify(S.rig) !== JSON.stringify(S.saved);
const cleanPose = () => JSON.stringify({ bones: S.pose.bones, ik: S.pose.ik });
const poseDirty = () => cleanPose() !== S.poseBase;
const locked = () => S.cmp.on || S.rest;
function blockedMsg() { toast(S.cmp.on ? "Đang so sánh (chỉ xem): thoát so sánh để chỉnh" : "Đang xem 'Dáng gốc': tắt ô đó để chỉnh dáng đang làm"); }

// Joint limits: the rig's bone.limit.rot wins; null = free; otherwise a default by bone name. Edits are clamped, loads are not.
function limitOf(n) {
  const b = bone(n); if (!b) return null;
  if (b.limit && "rot" in b.limit) return b.limit.rot;
  for (const [k, v] of Object.entries(DEFAULT_LIMITS)) if (n === k || n.endsWith("_" + k)) return v;
  return null;
}
let freeLimits = false;
function setCh(n, ch, v) {
  if (ch === "rot" && !freeLimits) {
    const L = limitOf(n);
    if (L && (v < L[0] || v > L[1])) { v = Math.max(L[0], Math.min(L[1], v)); S.hitLimit = { bone: n, t: performance.now() }; }
  }
  const o = (S.pose.bones[n] = S.pose.bones[n] || {});
  if (Math.abs(v - DEF[ch]) < 1e-9) delete o[ch]; else o[ch] = v;
  if (!Object.keys(o).length) delete S.pose.bones[n];
}
function displayPose() {
  if (S.rest) return {};
  if (S.cmp.on) return poseByRef(S.cmp[S.cmp.showing]);
  return S.pose;
}
function poseByRef(ref) {
  if (ref === "working") return S.pose;
  if (ref === "rest") return {};
  const p = S.poses.find((q) => q.id === ref);
  return p ? { bones: p.bones || {}, ik: p.ik || {} } : {};
}

// ---------------------------------------------------------------- undo / redo / autosave
const snapshot = () => JSON.stringify({ rig: S.rig, pose: { bones: S.pose.bones, ik: S.pose.ik } });
let editSnap = null;
function beginEdit() { if (!editSnap) editSnap = snapshot(); }
function commitEdit() {
  if (!editSnap) return;
  if (editSnap !== snapshot()) { S.undo.push(editSnap); if (S.undo.length > 150) S.undo.shift(); S.redo.length = 0; }
  editSnap = null; scheduleAutosave(); refreshPanels(); render("final");
}
function restore(snap) {
  const o = JSON.parse(snap);
  S.rig = o.rig; S.pose = o.pose; S.rigSync = true;
  if (S.editPart && !partOf(S.editPart)) S.editPart = null;
  S.selVert = null; refreshPanels(); render("final");
}
function undo() { if (!S.undo.length) return; S.redo.push(snapshot()); restore(S.undo.pop()); scheduleAutosave(); }
function redo() { if (!S.redo.length) return; S.undo.push(snapshot()); restore(S.redo.pop()); scheduleAutosave(); }
let autoT = null;
function scheduleAutosave() {
  clearTimeout(autoT);
  autoT = setTimeout(() => api("/api/autosave", { rig_file: S.rigFile, rig: S.rig, pose: S.pose, time: new Date().toISOString(), rig_dirty: rigDirty() }).catch(() => {}), 1200);
}

// ---------------------------------------------------------------- render scheduling
let rendering = false, pending = null, finalTimer = null;
function render(q = "draft") {
  if (q === "draft") { clearTimeout(finalTimer); finalTimer = setTimeout(() => render("final"), 450); }
  else clearTimeout(finalTimer);
  pending = q === "final" ? "final" : pending || "draft";
  if (!rendering) pump();
}
async function pump() {
  rendering = true;
  while (pending) {
    const q = pending; pending = null;
    if (q === "final" && (drag && drag.type !== "pan" || press && press.moved)) { finalTimer = setTimeout(() => render("final"), 450); continue; }
    $("#loading").textContent = "đang vẽ…"; $("#loading").className = "busy";
    try { await renderNow(q); S.bad = null; } catch (e) { S.bad = e.message; toast(e.message, true, 6000); }
    $("#loading").textContent = ""; $("#loading").className = "";
  }
  rendering = false; updateStatus(); draw();
}
function layersFor(pose) {
  const hide = [...S.hide], L = [];
  if (S.ghostRig) L.push({ src: "saved", pose, hide, alpha: 0.4 });
  if (S.cmp.on && S.cmp.onion) L.push({ src: "working", pose: poseByRef(S.cmp[S.cmp.showing === "a" ? "b" : "a"]), hide, alpha: 0.35 });
  L.push({ src: "working", pose, hide, primary: true });
  return L;
}
const loadImg = (b64) => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = "data:image/png;base64," + b64; });
async function renderNow(q) {
  if (S.rigSync) {
    const snapRig = S.rig;
    await api("/api/rig/set", { rig: snapRig });
    if (snapRig === S.rig) S.rigSync = false;
  }
  const pose = displayPose(), final = q === "final", scale = final ? parseFloat($("#optQuality").value) : DRAFT, gs = S.gameH / S.rig.unit;
  const body = { scale, draft: !final, region: [-60, -60, 1144, 1144], layers: layersFor(pose) };
  if (final) body.game = { scale: gs, region: [S.rig.ground[0] - 360, S.rig.ground[1] - S.rig.unit * 1.12, 720, S.rig.unit * 1.2] };
  const res = await api("/api/render", body), img = await loadImg(res.png);
  S.render = res; S.img = img; S.renderQ = q;
  if (res.game_png) S.game = await loadImg(res.game_png);
  draw();
}
function updateStatus() {
  const r = S.render;
  $("#renderInfo").textContent = r ? `${S.renderQ === "final" ? "bản chuẩn" : "bản nháp"} ${r.size[0]}×${r.size[1]} · ${r.ms} ms` : "";
  const rd = rigDirty(), pd = poseDirty();
  $("#dirtyRig").textContent = rd ? "● rig chưa lưu" : "rig đã lưu"; $("#dirtyRig").className = rd ? "d" : "";
  $("#dirtyPose").textContent = pd ? `● pose ${S.poseId ? "đã sửa" : "chưa vào thư viện"}` : (S.poseId ? `pose: ${S.poseId}` : "pose: dáng gốc"); $("#dirtyPose").className = pd ? "d" : "";
  $("#btnUndo").disabled = !S.undo.length; $("#btnRedo").disabled = !S.redo.length;
}

// ---------------------------------------------------------------- viewport
const cv = $("#vp"), ctx = cv.getContext("2d");
const toScreen = (x, y) => [x * S.view.zoom + S.view.px, y * S.view.zoom + S.view.py];
const toRig = (sx, sy) => [(sx - S.view.px) / S.view.zoom, (sy - S.view.py) / S.view.zoom];
function resize() { const r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1; cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d); draw(); }
function fit(box = [60, 60, 900, 900]) {
  const r = cv.getBoundingClientRect(), z = Math.min(r.width / box[2], r.height / box[3]) * 0.92;
  S.view.zoom = z; S.view.px = r.width / 2 - (box[0] + box[2] / 2) * z; S.view.py = r.height / 2 - (box[1] + box[3] / 2) * z; draw();
}
function zoomAt(f, sx, sy) { const [rx, ry] = toRig(sx, sy); S.view.zoom = Math.max(0.05, Math.min(12, S.view.zoom * f)); S.view.px = sx - rx * S.view.zoom; S.view.py = sy - ry * S.view.zoom; draw(); }
function actualSize(h) { const r = cv.getBoundingClientRect(), z = h / S.rig.unit; S.view.zoom = z; S.view.px = r.width / 2 - S.rig.ground[0] * z; S.view.py = r.height / 2 - (S.rig.ground[1] - S.rig.unit / 2) * z; draw(); }
function poly(pts, close = true) { ctx.beginPath(); pts.forEach((p, i) => { const [x, y] = toScreen(p[0], p[1]); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); if (close) ctx.closePath(); }
const rect = (off, size) => [[off[0], off[1]], [off[0] + size[0], off[1]], [off[0] + size[0], off[1] + size[1]], [off[0], off[1] + size[1]]];
const posedPoly = (p) => p.select.poly.map((q) => mapPt(world(p.bone), q[0], q[1]));
function pointInPoly(x, y, pts) {
  let inside = false;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) if ((pts[i][1] > y) !== (pts[j][1] > y) && x < ((pts[j][0] - pts[i][0]) * (y - pts[i][1])) / (pts[j][1] - pts[i][1]) + pts[i][0]) inside = !inside;
  return inside;
}
function ring(x, y, r, col, w = 2, dash = []) { ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.setLineDash(dash); ctx.stroke(); ctx.setLineDash([]); }
function line(a, b, col, w, dash = []) { const [x0, y0] = toScreen(...a), [x1, y1] = toScreen(...b); ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.setLineDash(dash); ctx.stroke(); ctx.setLineDash([]); }

let drawQueued = false;
function draw() { if (drawQueued) return; drawQueued = true; requestAnimationFrame(() => { drawQueued = false; drawNow(); }); }
function drawNow() {
  if (!S.rig) return;
  const d = window.devicePixelRatio || 1, W = cv.width / d, H = cv.height / d;
  ctx.setTransform(d, 0, 0, d, 0, 0);
  ctx.fillStyle = { dark: "#262b33", light: "#d9dde3", green: "#2f8f4a", check: "#2a2f37" }[S.bg]; ctx.fillRect(0, 0, W, H);
  if (S.bg === "check") { ctx.fillStyle = "#353b45"; for (let y = 0; y < H; y += 24) for (let x = ((y / 24) % 2) * 24; x < W; x += 48) ctx.fillRect(x, y, 24, 24); }
  if (S.grid) {
    ctx.lineWidth = 1;
    const step = S.view.zoom > 0.9 ? 50 : 100, [x0, y0] = toRig(0, 0), [x1, y1] = toRig(W, H);
    for (let x = Math.floor(x0 / step) * step; x < x1; x += step) { const sx = toScreen(x, 0)[0]; ctx.strokeStyle = x % 500 === 0 ? "#ffffff30" : "#ffffff12"; ctx.beginPath(); ctx.moveTo(sx, 0); ctx.lineTo(sx, H); ctx.stroke(); }
    for (let y = Math.floor(y0 / step) * step; y < y1; y += step) { const sy = toScreen(0, y)[1]; ctx.strokeStyle = y % 500 === 0 ? "#ffffff30" : "#ffffff12"; ctx.beginPath(); ctx.moveTo(0, sy); ctx.lineTo(W, sy); ctx.stroke(); }
    const gy = toScreen(0, S.rig.ground[1])[1]; ctx.strokeStyle = "#4cd08a99"; ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke();
  }
  if (S.img && S.showChar && S.render) {
    const [x0, y0, w, h] = S.render.region, [sx, sy] = toScreen(x0, y0);
    ctx.imageSmoothingEnabled = S.view.zoom * S.render.scale < 1.5 || S.view.zoom > S.render.scale; ctx.imageSmoothingQuality = "high";
    ctx.drawImage(S.img, sx, sy, w * S.view.zoom, h * S.view.zoom);
  }
  drawOverlay(); drawGame();
}
function drawGame() {
  const g = $("#game"); if (!S.game) return;
  const k = S.gameH === 60 ? 3 : 2;
  g.width = S.game.width; g.height = S.game.height; g.style.width = g.width * k + "px"; g.style.height = g.height * k + "px";
  const c = g.getContext("2d"); c.imageSmoothingEnabled = false; c.fillStyle = "#3a414c"; c.fillRect(0, 0, g.width, g.height); c.drawImage(S.game, 0, 0);
  $("#gameCap").textContent = `Cỡ game: H=${S.gameH}px @${S.gameH === 60 ? "1x" : "2x"} (phóng ${k}×)`;
}

function skinJoints(p) {
  const sk = p.skin, js = [];
  for (let i = 1; i < sk.bones.length; i++) {
    const b = bone(sk.bones[i]), nxt = i + 1 < sk.bones.length ? bone(sk.bones[i + 1]).pivot : sk.tip;
    const dx = nxt[0] - b.pivot[0], dy = nxt[1] - b.pivot[1], L = Math.hypot(dx, dy) || 1;
    js.push({ bone: b.name, piv: b.pivot, axis: [dx / L, dy / L], blend: Array.isArray(sk.blend) ? sk.blend[i - 1] : sk.blend, idx: i - 1 });
  }
  return js;
}
function drawSkinBands(p) {
  for (const j of skinJoints(p)) {
    const m = world(j.bone), nx = -j.axis[1], ny = j.axis[0], hw = 90, bl = j.blend;
    const q = (a, s) => [j.piv[0] + j.axis[0] * a + nx * s, j.piv[1] + j.axis[1] * a + ny * s];
    poly([q(-bl, -hw), q(bl, -hw), q(bl, hw), q(-bl, hw)].map((c) => mapPt(m, c[0], c[1]))); ctx.fillStyle = "#ff6bd622"; ctx.fill(); ctx.strokeStyle = "#ff6bd6"; ctx.lineWidth = 1; ctx.stroke();
  }
}
function drawVertices() {
  const p = partOf(S.editPart); if (!p || !p.select.poly) return;
  posedPoly(p).forEach((q, i) => {
    const [x, y] = toScreen(q[0], q[1]), on = i === S.selVert;
    ctx.fillStyle = on ? "#ffd84a" : "#fff"; ctx.strokeStyle = "#000"; ctx.lineWidth = 1; ctx.fillRect(x - 5, y - 5, 10, 10); ctx.strokeRect(x - 5, y - 5, 10, 10);
    ctx.fillStyle = "#fff"; ctx.font = "9px monospace"; ctx.fillText(i, x + 7, y - 7);
  });
}
function boneShape(a, b, col, sel) {
  const [x0, y0] = toScreen(...a), [x1, y1] = toScreen(...b), dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L, w = Math.min(7, L * 0.14) + (sel ? 1.5 : 0);
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + dx * 0.15 + nx * w, y0 + dy * 0.15 + ny * w); ctx.lineTo(x1, y1); ctx.lineTo(x0 + dx * 0.15 - nx * w, y0 + dy * 0.15 - ny * w); ctx.closePath();
  ctx.fillStyle = col + (sel ? "cc" : "66"); ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = sel ? 2 : 1.2; ctx.stroke();
}
function desc(n) { const out = []; const walk = (x) => children(x).forEach((c) => { out.push(c.name); walk(c.name); }); walk(n); return out; }

function drawOverlay() {
  if (!S.render) return;
  const V = S.vis, selB = S.sel, sel = selB ? new Set([selB, ...desc(selB)]) : new Set();
  for (const p of S.rig.parts) {
    const isSkin = !!p.skin, show = (isSkin && V.skin) || (!isSkin && V.rigid) || V.polys || S.editPart === p.name;
    const infl = (V.influence && selB && (p.bone === selB || (p.skin && p.skin.bones.includes(selB)))) || S.selPart === p.name;
    if (V.bounds) { const m = S.parts.find((q) => q.name === p.name); if (m) { poly(rect(m.off, m.size).map((q) => mapPt(world(p.bone), q[0], q[1]))); ctx.strokeStyle = "#ffffff90"; ctx.setLineDash([4, 3]); ctx.lineWidth = 1; ctx.stroke(); ctx.setLineDash([]); } }
    if (!p.select.poly || !(show || infl)) continue;
    poly(posedPoly(p)); ctx.fillStyle = infl ? "#ffc83d40" : isSkin ? "#b57bff22" : "#3fd1c522"; ctx.fill();
    ctx.strokeStyle = S.editPart === p.name ? "#ff8ae6" : infl ? "#ffc83d" : isSkin ? "#c58bff" : "#4fd1c5"; ctx.lineWidth = S.editPart === p.name ? 3 : 1.2; ctx.stroke();
  }
  if (V.skin) for (const p of S.rig.parts) if (p.skin) drawSkinBands(p);
  if (V.influence && selB) for (const n of sel) if (n !== selB) { const e = boneEnd(n); if (e) line(posedPivot(n), e.pt, "#ffc83d66", 5); }
  if (V.links) drawLinks();
  if (V.skeleton) for (const b of S.rig.bones) {
    const P = posedPivot(b.name), isSel = b.name === selB;
    if (b.parent) { const pe = boneEnd(b.parent); if (!pe || Math.hypot(pe.pt[0] - P[0], pe.pt[1] - P[1]) > 1) line(posedPivot(b.parent), P, "#ffffff55", 1.5, [3, 3]); }
    const e = boneEnd(b.name); if (e) boneShape(P, e.pt, isSel ? "#ffd84a" : sideColor(b.name), isSel);
  }
  if (V.pivots || V.skeleton) for (const b of S.rig.bones) {
    const [x, y] = toScreen(...posedPivot(b.name)), isSel = b.name === selB;
    ctx.beginPath(); ctx.arc(x, y, isSel ? 7 : 4.5, 0, 7); ctx.fillStyle = isSel ? "#ffd84a" : "#101319"; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = isSel ? "#fff" : sideColor(b.name); ctx.stroke();
  }
  if (V.labels) { ctx.font = "11px system-ui"; ctx.textBaseline = "middle"; for (const b of S.rig.bones) { const [x, y] = toScreen(...posedPivot(b.name)), t = viName(b.name), w = ctx.measureText(t).width; ctx.fillStyle = "#000b"; ctx.fillRect(x + 8, y - 8, w + 6, 15); ctx.fillStyle = b.name === selB ? "#ffd84a" : "#fff"; ctx.fillText(t, x + 11, y); } }
  if (V.sockets) for (const [n, s] of Object.entries(S.rig.sockets || {})) { const [x, y] = toScreen(...mapPt(world(s.bone), s.pt[0], s.pt[1])); ctx.strokeStyle = "#7dff7d"; ctx.lineWidth = 2; ctx.strokeRect(x - 5, y - 5, 10, 10); ctx.fillStyle = "#7dff7d"; ctx.font = "10px system-ui"; ctx.fillText(n, x + 8, y + 12); }
  if (V.ik) for (const ik of S.rig.ik || []) {
    const [x, y] = toScreen(...ikTargetWorld(ik)), on = ikOn(ik);
    ctx.beginPath(); ctx.moveTo(x, y - 8); ctx.lineTo(x + 8, y); ctx.lineTo(x, y + 8); ctx.lineTo(x - 8, y); ctx.closePath(); ctx.strokeStyle = on ? "#ff5edb" : "#888"; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = ctx.strokeStyle; ctx.font = "10px system-ui"; ctx.fillText(`IK chân ${ik.upper.startsWith("near") ? "gần" : "xa"}${on ? "" : " (FK)"}`, x + 10, y - 10);
  }
  drawGizmos();
  if (S.editPart) drawVertices();
  if (drag && drag.type === "chain" && drag.target) {
    const [x, y] = toScreen(...drag.target); ctx.strokeStyle = drag.residual > 3 ? "#ff6b6b" : "#4cd08a"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, y, 9, 0, 7); ctx.moveTo(x - 14, y); ctx.lineTo(x + 14, y); ctx.moveTo(x, y - 14); ctx.lineTo(x, y + 14); ctx.stroke();
    ctx.fillStyle = ctx.strokeStyle; ctx.font = "11px system-ui"; ctx.fillText(drag.residual > 3 ? `ngoài tầm với ${Math.round(drag.residual)} px` : "chạm đích", x + 12, y - 12);
  }
  if (S.hitLimit && performance.now() - S.hitLimit.t < 900 && bone(S.hitLimit.bone)) {
    const [x, y] = toScreen(...posedPivot(S.hitLimit.bone)); ctx.fillStyle = "#ffb86b"; ctx.font = "bold 12px system-ui"; ctx.fillText("chạm giới hạn khớp", x + 12, y - 16);
  }
  drawPointer();
}
function drawLinks() {
  (S.rig.links || []).forEach((lk, i) => {
    const arm = bone(lk.arm); if (!arm) return;
    const on = i === S.selLink && S.rightTab === "links", sh = posedPivot(lk.arm);
    for (const a of lk.anchors || []) {
      const part = partOf(a.part); if (!part) continue;
      const P = mapPt(world(part.bone), a.pt[0], a.pt[1]), [x, y] = toScreen(...P);
      ctx.fillStyle = lk.mode === "stretch" ? (on ? "#ff8ae630" : "#ff8ae61a") : "#8888881a"; ctx.beginPath(); ctx.arc(x, y, a.radius * S.view.zoom, 0, 7); ctx.fill();
      ring(x, y, a.radius * S.view.zoom, on ? "#ff8ae6" : "#ff8ae688", on ? 2 : 1, [5, 4]);
      line(P, sh, on ? "#ff8ae6" : "#ff8ae666", on ? 2 : 1, [4, 3]);
      ctx.fillStyle = "#ff8ae6"; ctx.beginPath(); ctx.arc(x, y, 5, 0, 7); ctx.fill();
    }
    if (on) { const [sx, sy] = toScreen(...sh); ctx.fillStyle = "#ff8ae6"; ctx.font = "11px system-ui"; ctx.fillText(`${lk.name} (${lk.mode === "stretch" ? "dãn cơ" : "cả thân đi theo"})`, sx + 10, sy + 20); }
  });
}
function drawGizmos() {
  if (S.cmp.on) return;
  const pulse = 0.5 + 0.5 * Math.sin(performance.now() / 300);
  if (S.tool === "pose") {
    for (const b of S.rig.bones) {
      if (!isLeaf(b.name)) continue;
      const e = boneEnd(b.name); if (!e) continue;
      const [x, y] = toScreen(...e.pt), on = b.name === S.sel || (S.hover && S.hover.id === b.name);
      ring(x, y, on ? 14 : 11 + pulse * 2, on ? "#ffd84a" : "#ffffffcc", on ? 3 : 2);
    }
    for (const ik of S.rig.ik || []) {
      if (!footTarget(ik)) continue;
      const [x, y] = toScreen(...ikTargetWorld(ik)), on = ik.end_bone === S.sel || (S.hover && S.hover.id === ik.end_bone);
      ring(x, y, on ? 15 : 12 + pulse * 2, on ? "#ffd84a" : "#ff8ae6", on ? 3 : 2);
    }
  }
  if (S.sel && S.vis.limits && (S.tool === "rotate" || S.tool === "pose")) drawLimitArc(S.sel);
  if (S.sel && S.tool === "rotate") { const [x, y] = toScreen(...posedPivot(S.sel)); ring(x, y, 48, "#ffd84a", 2, [6, 5]); ctx.fillStyle = "#ffd84a"; ctx.font = "12px system-ui"; ctx.fillText(`${viName(S.sel)}: xoay ${fmt(chVal(S.sel, "rot"))}°`, x + 56, y - 4); }
  if (S.sel && S.tool === "move") { const [x, y] = toScreen(...posedPivot(S.sel)); ctx.strokeStyle = "#ffd84a"; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x - 30, y); ctx.lineTo(x + 30, y); ctx.moveTo(x, y - 30); ctx.lineTo(x, y + 30); ctx.stroke(); ctx.fillStyle = "#ffd84a"; ctx.font = "12px system-ui"; ctx.fillText(`ngang ${fmt(chVal(S.sel, "tx"))}  dọc ${fmt(chVal(S.sel, "ty"))}`, x + 34, y - 8); }
  if (S.hover && S.hover.kind === "bone") {
    const [x, y] = toScreen(...posedPivot(S.hover.id)); ring(x, y, 16, "#ffffff", 2);
    ctx.font = "12px system-ui"; const t = viName(S.hover.id), w = ctx.measureText(t).width; ctx.fillStyle = "#000d"; ctx.fillRect(x + 20, y - 26, w + 12, 20); ctx.fillStyle = "#fff"; ctx.fillText(t, x + 26, y - 12);
  }
}
function drawLimitArc(n) {
  const L = limitOf(n); if (!L) return;
  const b = bone(n), e = boneEndRest(n), par = b.parent ? world(b.parent) : [1, 0, 0, 1, 0, 0];
  const v = e ? [e.rest[0] - b.pivot[0], e.rest[1] - b.pivot[1]] : [0, -1], a0 = Math.atan2(par[1] * v[0] + par[3] * v[1], par[0] * v[0] + par[2] * v[1]);
  const [x, y] = toScreen(...posedPivot(n)), R = 62, rad = (d) => a0 + (d * Math.PI) / 180;
  ctx.beginPath(); ctx.arc(x, y, R, rad(L[0]), rad(L[1])); ctx.strokeStyle = "#ffb86b"; ctx.lineWidth = 6; ctx.globalAlpha = 0.5; ctx.stroke(); ctx.globalAlpha = 1;
  for (const d of L) { ctx.beginPath(); ctx.moveTo(x + Math.cos(rad(d)) * (R - 10), y + Math.sin(rad(d)) * (R - 10)); ctx.lineTo(x + Math.cos(rad(d)) * (R + 10), y + Math.sin(rad(d)) * (R + 10)); ctx.strokeStyle = "#ffb86b"; ctx.lineWidth = 3; ctx.stroke(); }
  const cur = chVal(n, "rot"); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(rad(cur)) * R, y + Math.sin(rad(cur)) * R); ctx.strokeStyle = "#ffd84a"; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = "#ffb86b"; ctx.font = "11px system-ui"; ctx.fillText(`giới hạn ${L[0]}°…${L[1]}°`, x - 40, y + R + 18);
}
function drawPointer() {
  if (!S.mouse) return;
  const [x, y] = S.mouse, hot = !!S.hover || (drag && drag.type !== "pan");
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 3, y + 17); ctx.lineTo(x + 7.5, y + 12.5); ctx.lineTo(x + 13, y + 12); ctx.closePath();
  ctx.fillStyle = hot ? "#ffd84a" : "#ffffff"; ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5; ctx.fill(); ctx.stroke();
}
setInterval(() => { if (S.tool === "pose") draw(); }, 140);

// ---------------------------------------------------------------- picking
const canvasXY = (e) => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
function pickVertex(sx, sy) {
  const p = S.editPart && partOf(S.editPart); if (!p || !p.select.poly) return null;
  let best = null, bd = 10;
  posedPoly(p).forEach((q, i) => { const [x, y] = toScreen(q[0], q[1]), d = Math.hypot(x - sx, y - sy); if (d < bd) { bd = d; best = i; } });
  return best;
}
function pickEdge(sx, sy) {
  const p = S.editPart && partOf(S.editPart); if (!p || !p.select.poly) return null;
  const pts = posedPoly(p).map((q) => toScreen(q[0], q[1]));
  let best = null, bd = 7;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i + 1) % pts.length], dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy || 1;
    const t = Math.max(0, Math.min(1, ((sx - a[0]) * dx + (sy - a[1]) * dy) / L2)), d = Math.hypot(a[0] + t * dx - sx, a[1] + t * dy - sy);
    if (d < bd) { bd = d; best = { i, t }; }
  }
  return best;
}
function pickEndHandle(sx, sy) {
  let best = null, bd = 20;
  for (const ik of S.rig.ik || []) { if (!footTarget(ik) || !ik.end_bone) continue; const [x, y] = toScreen(...ikTargetWorld(ik)), d = Math.hypot(x - sx, y - sy); if (d < bd) { bd = d; best = ik.end_bone; } }
  for (const b of S.rig.bones) { if (!isLeaf(b.name)) continue; const e = boneEnd(b.name); if (!e) continue; const [x, y] = toScreen(...e.pt), d = Math.hypot(x - sx, y - sy); if (d < bd) { bd = d; best = b.name; } }
  return best;
}
function pickBone(sx, sy) {
  let best = null, bd = 16;
  for (const b of S.rig.bones) { const [x, y] = toScreen(...posedPivot(b.name)), d = Math.hypot(x - sx, y - sy); if (d < bd) { bd = d; best = b.name; } }
  if (best) return best;
  bd = 11;
  for (const b of S.rig.bones) {
    const e = boneEnd(b.name); if (!e) continue;
    const a = toScreen(...posedPivot(b.name)), c = toScreen(...e.pt), dx = c[0] - a[0], dy = c[1] - a[1], L2 = dx * dx + dy * dy || 1;
    const t = Math.max(0, Math.min(1, ((sx - a[0]) * dx + (sy - a[1]) * dy) / L2)), d = Math.hypot(a[0] + t * dx - sx, a[1] + t * dy - sy);
    if (d < bd) { bd = d; best = b.name; }
  }
  return best;
}
// Pressing on a picture picks the bone that moves it; for a bent limb, the segment nearest the press.
function pickPartBone(sx, sy) {
  const [rx, ry] = toRig(sx, sy);
  for (let i = S.rig.parts.length - 1; i >= 0; i--) {
    const p = S.rig.parts[i]; if (S.hide.has(p.name) || !p.select.poly || !pointInPoly(rx, ry, posedPoly(p))) continue;
    if (!p.skin) return p.bone;
    const q = invPt(world(p.bone), rx, ry), names = p.skin.bones;
    let best = names[0], bd = 1e9;
    names.forEach((n, k) => {
      const a = bone(n).pivot, b = k + 1 < names.length ? bone(names[k + 1]).pivot : p.skin.tip, dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy || 1;
      const t = Math.max(0, Math.min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L2)), d = Math.hypot(a[0] + t * dx - q[0], a[1] + t * dy - q[1]);
      if (d < bd) { bd = d; best = n; }
    });
    return best;
  }
  return null;
}
const pickTarget = (sx, sy) => pickEndHandle(sx, sy) || pickBone(sx, sy) || pickPartBone(sx, sy);
function pickRigHandle(sx, sy) {
  for (const [n, s] of Object.entries(S.rig.sockets || {})) { const [x, y] = toScreen(...mapPt(world(s.bone), s.pt[0], s.pt[1])); if (Math.hypot(x - sx, y - sy) < 11) return { kind: "socket", id: n }; }
  for (let i = 0; i < (S.rig.ik || []).length; i++) { const [x, y] = toScreen(...ikTargetWorld(S.rig.ik[i])); if (Math.hypot(x - sx, y - sy) < 12) return { kind: "ik", id: i }; }
  const b = pickBone(sx, sy); return b ? { kind: "pivot", id: b } : null;
}

// ---------------------------------------------------------------- solvers (write only the existing rot / tx / ty / sy channels)
const amul = (A, B) => [A[0] * B[0] + A[2] * B[1], A[1] * B[0] + A[3] * B[1], A[0] * B[2] + A[2] * B[3], A[1] * B[2] + A[3] * B[3], A[0] * B[4] + A[2] * B[5] + A[4], A[1] * B[4] + A[3] * B[5] + A[5]];
function fkWorld(name, bones, memo = {}) {
  if (memo[name]) return memo[name];
  const b = bone(name), v = bones[name] || {}, g = (c) => v[c] ?? DEF[c], [px, py] = b.pivot, r = (g("rot") * Math.PI) / 180, c = Math.cos(r), sn = Math.sin(r);
  let L = amul([1, 0, 0, 1, px + g("tx"), py + g("ty")], [c, sn, -sn, c, 0, 0]);
  L = amul(L, [1, 0, -g("shx"), 1, 0, 0]); L = amul(L, [g("sx"), 0, 0, g("sy"), 0, 0]); L = amul(L, [1, 0, 0, 1, -px, -py]);
  return (memo[name] = b.parent ? amul(fkWorld(b.parent, bones, memo), L) : L);
}
const clampN = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
/** Drag the end of `name` to `target` (rig px). Arm joints turn (inside their limits); the body leans and shifts by chainOpt.follow;
 *  past the reach, a "stretch" link slides the shoulder out (the chest follows), a "carry" link or no link moves the body / stretches the limb. */
function chainSolve(start, name, target) {
  const bones = clone(start), end = (boneEndRest(name) || { rest: bone(name).pivot }).rest;
  const joints = [];
  for (let n = name; n && bone(n).parent; n = bone(n).parent) joints.push(n);
  const isBody = (n) => n === "hips" || n === "spine";
  const arm = joints.filter((n) => !isBody(n)), top = arm[arm.length - 1], link = top ? linkOf(top) : null, stretchLink = link && link.mode === "stretch";
  const F = chainOpt.follow * (stretchLink ? 0.25 : 1);
  const E = () => mapPt(fkWorld(name, bones), end[0], end[1]);
  const set = (n, ch, v) => { (bones[n] = bones[n] || {})[ch] = v; };
  const get = (n, ch) => (bones[n] || {})[ch] ?? DEF[ch];
  for (const n of arm) if (n.endsWith("forearm") && Math.abs(get(n, "rot")) < 3) set(n, "rot", -14);   // a dead-straight arm is a CCD dead end
  const E0 = E(), dx = target[0] - E0[0], dy = target[1] - E0[1];
  if (F > 0 && joints.includes("hips")) {
    const i = inv2(fkWorld(bone("hips").parent, bones)), bx = F * 0.4 * dx, by = F * 0.25 * dy;
    set("hips", "tx", clampN(get("hips", "tx") + i[0] * bx + i[2] * by, -140, 140)); set("hips", "ty", clampN(get("hips", "ty") + i[1] * bx + i[3] * by, 0, 90));
  }
  if (F > 0 && joints.includes("spine")) { const L = limitOf("spine") || [-14, 14]; set("spine", "rot", clampN(get("spine", "rot") + F * 0.06 * dx, Math.max(L[0], -14), Math.min(L[1], 14))); }
  let armLen = 0;
  if (top) { const seq = [...arm].reverse().map((n) => bone(n).pivot).concat([end]); for (let k = 1; k < seq.length; k++) armLen += Math.hypot(seq[k][0] - seq[k - 1][0], seq[k][1] - seq[k - 1][1]); }
  for (let it = 0; it < 25; it++) {
    for (const n of [...arm].reverse()) {                          // nearest the body first, so the shoulder takes the big turn
      const w = n === name && arm.length > 1 ? 0.35 : 1, P = mapPt(fkWorld(n, bones), ...bone(n).pivot), e = E();
      let d = ((Math.atan2(target[1] - P[1], target[0] - P[0]) - Math.atan2(e[1] - P[1], e[0] - P[0])) * 180) / Math.PI; d = ((d + 540) % 360) - 180;
      const [lo, hi] = limitOf(n) || [-180, 180]; set(n, "rot", clampN(get(n, "rot") + w * d * 0.8, lo, hi));
    }
    if (top && stretchLink) {                                     // shoulder slides toward the target by what the arm cannot reach
      const b2 = { ...bones, [top]: { ...(bones[top] || {}), tx: 0, ty: 0 } }, Sr = mapPt(fkWorld(top, b2), ...bone(top).pivot);
      const vx = target[0] - Sr[0], vy = target[1] - Sr[1], dist = Math.hypot(vx, vy) || 1, m = clampN(dist - 0.98 * armLen, 0, link.max_pull ?? 80);
      const i = inv2(fkWorld(bone(top).parent, bones));
      set(top, "tx", (i[0] * vx + i[2] * vy) / dist * m); set(top, "ty", (i[1] * vx + i[3] * vy) / dist * m);
    } else if (chainOpt.stretch && arm.length > 1) {
      const S0 = mapPt(fkWorld(top, bones), ...bone(top).pivot), e = E();
      const have = Math.hypot(e[0] - S0[0], e[1] - S0[1]), want = Math.hypot(target[0] - S0[0], target[1] - S0[1]), sy = get(top, "sy");
      if (want > have * 1.01) set(top, "sy", Math.min(chainOpt.maxStretch, sy * Math.min(want / have, 1.1)));
      else if (want < have * 0.99 && sy > 1) set(top, "sy", Math.max(1, sy * Math.max(want / have, 0.9)));
    }
    const e = E(); if (Math.hypot(target[0] - e[0], target[1] - e[1]) < 0.5) break;
  }
  const e = E();
  return { bones, residual: Math.hypot(target[0] - e[0], target[1] - e[1]) };
}
function applyChain(m) {
  beginEdit();
  drag.target = [drag.E0[0] + m[0] - drag.m0[0], drag.E0[1] + m[1] - drag.m0[1]];
  const r = chainSolve(drag.start, drag.bone, drag.target);
  S.pose.bones = {};
  for (const [n, v] of Object.entries(r.bones)) for (const [c, x] of Object.entries(v)) if (Math.abs(x - DEF[c]) > 1e-6) (S.pose.bones[n] = S.pose.bones[n] || {})[c] = x;
  drag.residual = r.residual; render("draft"); refreshValues(); draw();
}
function applyFoot(m) {
  beginEdit();
  const d = drag, ik = d.ik, up = bone(ik.upper), low = bone(ik.lower);
  let T = [d.E0[0] + m[0] - d.m0[0], d.E0[1] + m[1] - d.m0[1]];
  const len = Math.hypot(low.pivot[0] - up.pivot[0], low.pivot[1] - up.pivot[1]) + Math.hypot(ik.end[0] - low.pivot[0], ik.end[1] - low.pivot[1]);
  const base = clone(d.start); base.hips = { ...(base.hips || {}), ty: 0 };
  const s1 = mapPt(fkWorld(up.parent, base), up.pivot[0], up.pivot[1]), lim = len * 0.985, ox = clampN(T[0] - s1[0], -lim, lim);
  T = [s1[0] + ox, T[1]];
  const drop = Math.max(0, T[1] - s1[1] - Math.sqrt(lim * lim - ox * ox));     // a straight leg cannot spread: lower the hips just enough
  if (bone("hips")) setCh("hips", "ty", Math.round(Math.min(90, Math.max((d.start.hips || {}).ty ?? 0, drop)) * 10) / 10);
  const i = inv2(d.Wp), dx = T[0] - d.E0[0], dy = T[1] - d.E0[1];
  setCh(d.tb, "tx", Math.round((d.tx0 + i[0] * dx + i[2] * dy) * 10) / 10); setCh(d.tb, "ty", Math.round((d.ty0 + i[1] * dx + i[3] * dy) * 10) / 10);
  d.target = T; d.residual = 0; render("draft"); refreshValues(); draw();
}
function applyRotate(m, e) {
  beginEdit();
  const d = drag, a = Math.atan2(m[1] - d.P[1], m[0] - d.P[0]);
  let da = ((a - d.a0) * 180) / Math.PI; da = ((da + 540) % 360) - 180;
  setCh(d.bone, "rot", Math.round((d.rot0 + da) * (e && e.shiftKey ? 1 : 10)) / (e && e.shiftKey ? 1 : 10)); render("draft"); refreshValues();
}
function applyMove(m) {
  beginEdit();
  const d = drag, dw = [m[0] - d.m0[0], m[1] - d.m0[1]], i = inv2(d.Wp);
  setCh(d.bone, "tx", Math.round((d.tx0 + i[0] * dw[0] + i[2] * dw[1]) * 10) / 10); setCh(d.bone, "ty", Math.round((d.ty0 + i[1] * dw[0] + i[3] * dw[1]) * 10) / 10);
  render("draft"); refreshValues();
}
const mkRotate = (n, m) => { const P = posedPivot(n); return { type: "rotate", bone: n, P, a0: Math.atan2(m[1] - P[1], m[0] - P[0]), rot0: chVal(n, "rot") }; };
const mkMove = (n, m) => { const b = bone(n); return { type: "move", bone: n, Wp: b.parent ? clone(world(b.parent)) : [1, 0, 0, 1, 0, 0], m0: m, tx0: chVal(n, "tx"), ty0: chVal(n, "ty") }; };
function mkFoot(ik, m) {
  const tb = footTarget(ik);
  if (!tb) { toast("Rig này chưa có bone đích cho chân. Mở rig_studio_v01.json ở ô chọn rig.", true, 6000); return null; }
  return { type: "ikfoot", ik, tb, m0: m, E0: ikTargetWorld(ik), tx0: chVal(tb, "tx"), ty0: chVal(tb, "ty"), Wp: clone(world(bone(tb).parent)), start: clone(S.pose.bones), target: ikTargetWorld(ik) };
}
// What "press and drag" means depends on what was pressed: legs move their IK target, hips/root slide the body, limbs reach, the rest aim at the pointer.
function mkPoseDrag(n, m) {
  if (ikDriven(n)) return mkFoot(ikOf(n), m);
  if (n === "hips" || !bone(n).parent) return mkMove(n, m);
  const end = boneEndRest(n);
  if (!end) return mkRotate(n, m);
  const E0 = mapPt(world(n), end.rest[0], end.rest[1]);
  return { type: "chain", bone: n, m0: m, E0, start: clone(S.pose.bones), target: E0 };
}
function applyDrag(m, e) {
  const t = drag.type;
  if (t === "chain") applyChain(m); else if (t === "ikfoot") applyFoot(m); else if (t === "rotate") applyRotate(m, e); else if (t === "move") applyMove(m);
}

// ---------------------------------------------------------------- pointer: click = select, press + drag = move, click outside = deselect
let drag = null, press = null, spaceDown = false;
cv.addEventListener("pointerleave", () => { S.mouse = null; S.hover = null; draw(); });
cv.addEventListener("pointerdown", (e) => {
  cv.setPointerCapture(e.pointerId); hideMenu();
  const [sx, sy] = canvasXY(e); S.mouse = [sx, sy];
  if (e.button === 1 || spaceDown || e.altKey) { drag = { type: "pan", sx, sy, px: S.view.px, py: S.view.py }; return; }
  if (e.button !== 0) return;
  S.libFocus = false;
  const m = toRig(sx, sy);
  if (S.cmp.on) { S.sel = pickTarget(sx, sy); refreshPanels(); draw(); return; }
  if (S.tool === "anchor") { placeAnchor(m); return; }
  const v = pickVertex(sx, sy);
  if (v !== null) { S.selVert = v; beginEdit(); drag = { type: "vertex", i: v }; refreshPanels(); draw(); return; }
  if (S.tool === "pivot") {
    const h = pickRigHandle(sx, sy);
    if (h) { if (h.kind === "pivot") S.sel = h.id; beginEdit(); drag = { type: h.kind, id: h.id, w0: clone(S.render.world) }; }
    else S.sel = null;
    refreshPanels(); draw(); return;
  }
  let hit = pickTarget(sx, sy);
  if (!hit && S.sel && (S.tool === "rotate" || S.tool === "move")) { const P = toScreen(...posedPivot(S.sel)); if (Math.hypot(P[0] - sx, P[1] - sy) < 64) hit = S.sel; }
  press = { sx, sy, m, hit, moved: false };
  if (hit && hit !== S.sel) { S.sel = hit; S.selPart = null; refreshPanels(); draw(); }
});
cv.addEventListener("pointermove", (e) => {
  const [sx, sy] = canvasXY(e); S.mouse = [sx, sy];
  if (press && !drag && press.hit && Math.hypot(sx - press.sx, sy - press.sy) > DRAG_PX) {
    if (locked()) { blockedMsg(); press = null; return; }
    let d = null;
    if (S.tool === "pose") d = mkPoseDrag(press.hit, press.m);
    else if (S.tool === "rotate") d = ikDriven(press.hit) ? (toast(`${viName(press.hit)} do IK điều khiển: chuyển chân sang FK ở tab Khớp & giới hạn`), null) : mkRotate(press.hit, press.m);
    else if (S.tool === "move") d = mkMove(press.hit, press.m);
    if (d) { drag = d; press.moved = true; } else press = null;
  }
  if (!drag) {
    if (!press) {
      const v = pickVertex(sx, sy), eh = v === null && S.tool === "pose" ? pickEndHandle(sx, sy) : null;
      S.hover = v !== null ? { kind: "vertex", id: v } : eh ? { kind: "bone", id: eh } : (() => { const b = pickBone(sx, sy); return b ? { kind: "bone", id: b } : null; })();
      updateHint();
    }
    draw(); return;
  }
  const m = toRig(sx, sy);
  if (drag.type === "pan") { S.view.px = drag.px + sx - drag.sx; S.view.py = drag.py + sy - drag.sy; draw(); return; }
  const snap = (v) => (e.shiftKey ? Math.round(v) : r1(v));
  if (drag.type === "vertex") { const p = partOf(S.editPart), q = invPt(world(p.bone), m[0], m[1]); p.select.poly[drag.i] = [snap(q[0]), snap(q[1])]; S.rigSync = true; render("draft"); refreshValues(); }
  else if (drag.type === "pivot") { const b = bone(drag.id), Wp = b.parent ? drag.w0[b.parent] : [1, 0, 0, 1, 0, 0], q = invPt(Wp, m[0], m[1]); b.pivot = [snap(q[0] - chVal(b.name, "tx")), snap(q[1] - chVal(b.name, "ty"))]; S.rigSync = true; render("draft"); refreshValues(); }
  else if (drag.type === "ik") { const ik = S.rig.ik[drag.id], q = invPt(drag.w0[ik.target.bone], m[0], m[1]); ik.target.pt = [snap(q[0]), snap(q[1])]; S.rigSync = true; render("draft"); refreshValues(); }
  else if (drag.type === "socket") { const s = S.rig.sockets[drag.id], q = invPt(drag.w0[s.bone], m[0], m[1]); s.pt = [snap(q[0]), snap(q[1])]; S.rigSync = true; render("draft"); refreshValues(); }
  else applyDrag(m, e);
  draw();
});
cv.addEventListener("pointerup", async () => {
  const wasPress = press; press = null;
  if (!drag) { if (wasPress && !wasPress.hit && !wasPress.moved) { S.sel = null; S.selPart = null; refreshPanels(); draw(); } return; }
  const t = drag.type; drag = null;
  if (t === "pan") return;
  if (["vertex", "pivot", "ik", "socket"].includes(t)) {
    try { await api("/api/rig/set", { rig: S.rig }); S.rigSync = false; if (t === "vertex") S.cutRev++; }
    catch (err) { toast(`Bị từ chối: ${err.message}. Đã hoàn tác.`, true, 6000); const s = editSnap; editSnap = null; if (s) restore(s); return; }
  }
  commitEdit();
});
cv.addEventListener("wheel", (e) => { e.preventDefault(); const [sx, sy] = canvasXY(e); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, sx, sy); }, { passive: false });
cv.addEventListener("dblclick", (e) => { const [sx, sy] = canvasXY(e), ed = pickEdge(sx, sy); if (ed && pickVertex(sx, sy) === null) addVertexAt(ed.i, ed.t); });
cv.addEventListener("contextmenu", (e) => {
  e.preventDefault();
  const [sx, sy] = canvasXY(e), items = [], v = pickVertex(sx, sy), ed = pickEdge(sx, sy);
  if (v !== null) items.push(["Xóa đỉnh " + v, () => deleteVertex(v)]); else if (ed) items.push(["Thêm đỉnh trên cạnh này", () => addVertexAt(ed.i, ed.t)]);
  const b = pickTarget(sx, sy);
  if (b) {
    S.sel = b; refreshPanels(); draw();
    items.push([`Chọn khớp cha (${bone(b).parent ? viName(bone(b).parent) : "không có"})`, () => { const p = bone(b).parent; if (p) { S.sel = p; refreshPanels(); draw(); } }]);
    children(b).forEach((c) => items.push([`Chọn khớp con: ${viName(c.name)}`, () => { S.sel = c.name; refreshPanels(); draw(); }]));
    items.push(["Đưa khớp này về dáng gốc", () => resetBone(b)]);
    const ik = ikOf(b); if (ik) items.push([ikOn(ik) ? "Chuyển chân này sang FK" : "Chuyển chân này sang IK", () => toggleIk(ik)]);
    const part = S.rig.parts.find((p) => p.bone === b); if (part) items.push([`Sửa vùng cắt của layer ${part.name}`, () => { S.leftTab = "layers"; selectPart(part.name, true); }]);
  }
  if (items.length) showMenu(e.clientX, e.clientY, items);
});
function showMenu(x, y, items) { const m = $("#menu"); m.replaceChildren(...items.map(([t, f]) => el("div", { onclick: () => { hideMenu(); f(); } }, t))); m.style.left = Math.min(x, innerWidth - 220) + "px"; m.style.top = Math.min(y, innerHeight - 30 * items.length - 10) + "px"; m.hidden = false; }
const hideMenu = () => { $("#menu").hidden = true; };
document.addEventListener("pointerdown", (e) => { if (!e.target.closest("#menu")) hideMenu(); });

// ---------------------------------------------------------------- hints, banner, guide
const TOOL_HELP = {
  pose: "<b>Bấm</b> vào khớp hoặc hình để chọn · <b>giữ và kéo</b> để di chuyển (tay duỗi theo, chân dời bàn chân, hông trượt cả thân) · <b>bấm ra ngoài</b> để bỏ chọn.",
  rotate: "<b>Xoay</b>: bấm chọn khớp rồi kéo quanh khớp. Cung cam là giới hạn cho phép. Phím ←/→ xoay 1° (Shift = 5°).",
  move: "<b>Trượt</b>: bấm chọn khớp rồi giữ và kéo. Phím mũi tên = 1 px (Shift = 5 px).",
  pivot: "<b>SỬA RIG</b>: kéo tâm khớp, đích IK (hình thoi) hoặc socket (ô vuông). Bấm ra ngoài = bỏ chọn. Esc = thoát.",
  anchor: "<b>ĐIỂM BÁM</b>: bấm lên thân để đặt điểm bám cho cơ của liên kết đang chọn. Esc = thoát.",
};
function updateHint() {
  const sel = S.sel ? ` · đang chọn <b>${viName(S.sel)}</b>` : " · chưa chọn gì", hov = S.hover && S.hover.kind === "bone" && S.hover.id !== S.sel ? ` · trỏ vào ${viName(S.hover.id)}` : "";
  $("#hint").innerHTML = TOOL_HELP[S.tool] + sel + hov + "<br><small>Cuộn = zoom · Space + kéo = dời khung · F = vừa khung · Ctrl+Z = hoàn tác · Tab = khớp kế · H = hướng dẫn</small>";
  const b = $("#banner"), msg = S.tool === "pivot" ? "CHẾ ĐỘ SỬA RIG: thay đổi ghi vào rig (cần Lưu rig)" : S.tool === "anchor" ? "ĐẶT ĐIỂM BÁM: bấm lên thân · Esc để thoát" : S.cmp.on ? "SO SÁNH (chỉ xem)" : S.rest ? "ĐANG XEM DÁNG GỐC" : "";
  b.style.display = msg ? "block" : "none"; b.textContent = msg;
}
function showGuide() {
  const n = el("div", {}, el("p", {}, "Lion Studio: tạo dáng cho Lion, cấu hình khớp, giới hạn và cơ, rồi lưu pose."),
    el("ol", {},
      el("li", {}, el("b", {}, "Chọn:"), " bấm vào khớp (chấm tròn) hoặc thẳng lên hình (cánh tay, thân, đầu…). Khớp đang chọn sáng màu vàng. Bấm ra ngoài để bỏ chọn."),
      el("li", {}, el("b", {}, "Di chuyển:"), " giữ chuột ở khớp rồi kéo. Bàn tay: tay duỗi theo chuột, thân đi theo; bàn chân: dời đích IK; hông: trượt cả thân. Chỉnh tinh trong tab ", el("b", {}, "1 Tạo dáng"), "."),
      el("li", {}, el("b", {}, "Giới hạn khớp:"), " tab ", el("b", {}, "2 Khớp & giới hạn"), " cho đặt góc xoay tối thiểu/tối đa từng khớp (bàn chân không xoay được 360°). Cung cam trên màn hình là vùng cho phép."),
      el("li", {}, el("b", {}, "Cơ & dây chằng:"), " tab ", el("b", {}, "3"), ": chọn một cánh tay, bấm các điểm bám lên ngực. Khi tay vươn quá tầm, vai trượt ra và cơ quanh điểm bám dãn theo. Chọn 'cả thân đi theo' cho nhân vật không có cơ."),
      el("li", {}, el("b", {}, "Lưu:"), " dáng ưng ý → ", el("b", {}, "+ Lưu pose"), " (dưới cùng). Sửa rig (tab 4) cần ", el("b", {}, "Lưu rig"), " (có backup)."),
      el("li", {}, el("b", {}, "Phím:"), " V tạo dáng, E xoay, W trượt, P sửa rig, A điểm bám, Esc thoát chế độ/bỏ chọn, Tab khớp kế, mũi tên chỉnh nhẹ, F vừa khung.")),
    el("p", { class: "mut" }, "Khung nhỏ góc phải dưới là cỡ thật trong game (H=60px)."));
  return modal({ title: "Hướng dẫn nhanh", node: n, ok: "Đã hiểu", noCancel: true });
}

// ---------------------------------------------------------------- pose actions
function nudge(n, ch, d) {
  if (locked()) return blockedMsg();
  if (ikDriven(n)) return toast(`${viName(n)} do IK điều khiển: chuyển chân sang FK (tab Khớp & giới hạn) hoặc kéo bàn chân`);
  beginEdit(); setCh(n, ch, Math.round((chVal(n, ch) + d) * 100) / 100); commitEdit();
}
function resetBone(n) { if (locked()) return blockedMsg(); beginEdit(); delete S.pose.bones[n]; const ik = (S.rig.ik || []).find((i) => i.upper === n); if (ik) delete S.pose.ik[ik.upper]; commitEdit(); }
function resetPose() { if (locked()) return blockedMsg(); beginEdit(); S.pose = { bones: {}, ik: {} }; S.poseId = null; commitEdit(); }
function toggleIk(ik) { if (locked()) return blockedMsg(); beginEdit(); if (ikOn(ik)) S.pose.ik[ik.upper] = false; else delete S.pose.ik[ik.upper]; commitEdit(); }
function selectPart(n, edit = false) {
  if (edit) S.editPart = S.editPart === n ? null : n;
  S.selPart = n; S.sel = partOf(n).bone; S.selVert = null; refreshPanels(); draw();
}
function addVertexAt(i, t) {
  const p = partOf(S.editPart); if (!p) return;
  const a = p.select.poly[i], b = p.select.poly[(i + 1) % p.select.poly.length];
  beginEdit(); p.select.poly.splice(i + 1, 0, [r1(a[0] + (b[0] - a[0]) * t), r1(a[1] + (b[1] - a[1]) * t)]); S.selVert = i + 1; S.rigSync = true; applyRigEdit("Đã thêm đỉnh");
}
function deleteVertex(i) {
  const p = partOf(S.editPart); if (!p) return;
  if (p.select.poly.length <= 3) return toast("Vùng cắt cần ít nhất 3 đỉnh", true);
  beginEdit(); p.select.poly.splice(i, 1); S.selVert = null; S.rigSync = true; applyRigEdit("Đã xóa đỉnh");
}
async function applyRigEdit(okMsg) {
  try { await api("/api/rig/set", { rig: S.rig }); S.rigSync = false; S.cutRev++; commitEdit(); if (okMsg) toast(okMsg); }
  catch (err) { toast(`Bị từ chối: ${err.message}. Đã hoàn tác.`, true, 6000); const s = editSnap; editSnap = null; if (s) restore(s); }
}

// ---------------------------------------------------------------- panel building
let binders = [];
function bind(input, get) { binders.push(() => { if (document.activeElement !== input) input.value = fmt(get()); }); input.value = fmt(get()); return input; }
function refreshValues() { binders.forEach((f) => f()); updateStatus(); }
function numField(get, set, step = 1, width = null) {
  const nm = el("input", { type: "number", step, style: width ? `width:${width}px` : null }); bind(nm, get);
  nm.addEventListener("change", () => { const v = parseFloat(nm.value); if (!Number.isFinite(v)) return refreshValues(); beginEdit(); set(v); commitEdit(); });
  return nm;
}
function slider({ label, min, max, step, get, set, reset, tip }) {
  const rg = el("input", { type: "range", min, max, step }), nm = el("input", { type: "number", step });
  const sync = () => { rg.value = get(); };
  binders.push(() => { if (document.activeElement !== nm) nm.value = fmt(get()); if (document.activeElement !== rg) sync(); });
  nm.value = fmt(get()); sync();
  rg.addEventListener("input", () => { beginEdit(); set(parseFloat(rg.value)); nm.value = fmt(get()); sync(); render("draft"); updateStatus(); draw(); });
  rg.addEventListener("change", commitEdit);
  nm.addEventListener("change", () => { const v = parseFloat(nm.value); if (!Number.isFinite(v)) return refreshValues(); beginEdit(); set(v); commitEdit(); });
  return el("div", { class: "sl", title: tip || "" }, el("span", {}, label), rg, nm, el("button", { class: "rs", title: "Đặt lại", onclick: () => { beginEdit(); reset(); commitEdit(); } }, "↺"));
}
const purpose = (t, rig = false) => el("div", { class: "purpose" + (rig ? " rig" : "") }, t);
const section = (title, ...kids) => el("section", {}, el("h3", {}, title), ...kids);
const boneLink = (n) => el("a", { class: "lnk", onclick: () => { S.sel = n; refreshPanels(); draw(); } }, `${viName(n)} (${n})`);

function refreshPanels() {
  binders = [];
  $$("#leftTabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === S.leftTab));
  $$("#rightTabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === S.rightTab));
  $$("#tools button").forEach((b) => b.classList.toggle("on", b.dataset.tool === S.tool));
  const keep = [$("#leftBody").scrollTop, $("#rightBody").scrollTop];
  (S.leftTab === "layers" ? buildLayers : buildBones)();
  ({ pose: tabPose, joints: tabJoints, links: tabLinks, rig: tabRig, test: tabTest })[S.rightTab]();
  $("#leftBody").scrollTop = keep[0]; $("#rightBody").scrollTop = keep[1];
  buildLibrary(); updateStatus(); updateHint();
}

// --- left: layers and bones
function buildLayers() {
  const b = $("#leftBody"); b.replaceChildren(purpose("Các layer (hình) tạo nên nhân vật. Bấm một layer để chọn khớp điều khiển nó. 'Sửa vùng cắt' cho chỉnh đa giác cắt layer."));
  for (const p of S.rig.parts) {
    const eye = el("input", { type: "checkbox", title: "Hiện / ẩn layer", onclick: (e) => { e.stopPropagation(); if (e.target.checked) S.hide.delete(p.name); else S.hide.add(p.name); render("final"); } });
    eye.checked = !S.hide.has(p.name);
    const joints = p.skin ? p.skin.bones.slice(1).map((n, i) => `${viName(n)} (mềm ${Array.isArray(p.skin.blend) ? p.skin.blend[i] : p.skin.blend})`).join(" · ") : "";
    b.append(el("div", { class: "layer" + (S.selPart === p.name ? " on" : "") + (S.editPart === p.name ? " edit" : ""), onclick: () => selectPart(p.name) },
      eye, el("img", { src: `/api/part/${p.name}.png?r=${S.cutRev}&f=${encodeURIComponent(S.rigFile)}`, alt: p.name }),
      el("div", {}, el("div", { class: "nm" }, p.name, " ", el("span", { class: "tag " + (p.skin ? "skin" : "rigid") }, p.skin ? "uốn được" : "cứng")),
        el("div", { class: "sub" }, `gắn vào: ${viName(p.bone)}`), joints ? el("div", { class: "sub" }, `khớp uốn: ${joints}`) : null,
        el("div", { class: "acts" },
          p.select.poly ? el("button", { onclick: (e) => { e.stopPropagation(); selectPart(p.name, true); S.rightTab = "rig"; refreshPanels(); } }, S.editPart === p.name ? "Tắt sửa vùng cắt" : "Sửa vùng cắt") : null,
          el("button", { onclick: (e) => { e.stopPropagation(); const only = S.rig.parts.every((q) => q.name === p.name || S.hide.has(q.name)); S.hide = new Set(only ? [] : S.rig.parts.filter((q) => q.name !== p.name).map((q) => q.name)); render("final"); refreshPanels(); } }, "Chỉ xem lớp này")))));
  }
  b.append(el("div", { class: "row" }, el("button", { onclick: () => { S.hide.clear(); render("final"); refreshPanels(); } }, "Hiện tất cả layer")));
}
function buildBones() {
  const b = $("#leftBody"); b.replaceChildren(purpose("Cây khớp: khớp con xoay theo khớp cha. Bấm một dòng để chọn."));
  const t = el("div", { class: "list" });
  const walk = (n, depth) => {
    const posed = S.pose.bones[n.name], L = limitOf(n.name);
    t.append(el("div", { class: n.name === S.sel ? "on" : "", style: `padding-left:${6 + depth * 14}px`, onclick: () => { S.sel = n.name; S.libFocus = false; refreshPanels(); draw(); } },
      el("span", { class: "dot", style: `background:${sideColor(n.name)}` }), viName(n.name), el("small", {}, n.name), posed ? el("span", { class: "tag" }, "đã chỉnh") : null, ikOf(n.name) ? el("span", { class: "tag" }, "IK") : null, L ? el("span", { class: "tag lim" }, `${L[0]}…${L[1]}`) : null));
    children(n.name).forEach((c) => walk(c, depth + 1));
  };
  S.rig.bones.filter((x) => !x.parent).forEach((r) => walk(r, 0));
  b.append(t);
  const ik = section("IK chân (bàn chân bám đích)");
  for (const k of S.rig.ik || []) {
    const cb = el("input", { type: "checkbox", onchange: () => toggleIk(k) }); cb.checked = ikOn(k);
    ik.append(el("div", { class: "row" }, el("label", {}, cb, ` chân ${k.upper.startsWith("near") ? "gần" : "xa"}: IK `), el("small", {}, ikOn(k) ? "bật: bàn chân bám đích" : "tắt: xoay đùi/cẳng chân bằng tay (FK)")));
  }
  b.append(ik);
  b.append(section("Socket (điểm gắn vũ khí/hiệu ứng)", el("div", { class: "list" }, Object.entries(S.rig.sockets || {}).map(([n, s]) => el("div", { onclick: () => { S.sel = s.bone; refreshPanels(); draw(); } }, el("span", { class: "dot", style: "background:#7dff7d" }), n, el("small", {}, `${viName(s.bone)}`))))));
}

// --- right: tab 1, pose
function tabPose() {
  const b = $("#rightBody"); b.replaceChildren(purpose("Tạo dáng cho nhân vật. Bấm vào khớp hoặc hình để chọn, giữ và kéo để di chuyển. Muốn chính xác thì dùng thanh trượt ở đây."));
  const n = S.sel, sec = section("Khớp đang chọn");
  if (!n) sec.append(el("div", { class: "mut" }, "Chưa chọn khớp nào. Bấm vào một khớp (chấm tròn) hoặc vào hình cánh tay, thân, đầu… trên màn hình."));
  else {
    sec.append(el("div", { class: "row" }, el("b", {}, viName(n)), el("small", {}, n), el("span", { class: "sp", style: "flex:1" }), el("button", { onclick: () => { S.sel = null; refreshPanels(); draw(); } }, "Bỏ chọn")));
    if (ikDriven(n)) sec.append(el("div", { class: "err" }, "Khớp này do IK điều khiển: các kênh bên dưới bị bỏ qua. Kéo bàn chân để dời, hoặc tắt IK ở tab 2."));
    const L = limitOf(n);
    const lim = { rot: L || [-180, 180], tx: [-300, 300], ty: [-300, 300], sx: [0.3, 2], sy: [0.3, 2], shx: [-0.6, 0.6] }, stp = { rot: 0.5, tx: 1, ty: 1, sx: 0.01, sy: 0.01, shx: 0.01 };
    for (const ch of CH) sec.append(slider({ label: el("span", {}, CH_VN[ch], " ", el("small", {}, ch), ch === "rot" && L ? el("small", {}, ` (${L[0]}…${L[1]}°)`) : null), min: lim[ch][0], max: lim[ch][1], step: stp[ch], get: () => chVal(n, ch), set: (v) => { if (!locked()) setCh(n, ch, v); }, reset: () => setCh(n, ch, DEF[ch]) }));
    sec.append(el("div", { class: "nudge", title: "Xoay nhẹ (độ)" }, [-5, -1, 1, 5].map((d) => el("button", { onclick: () => nudge(n, "rot", d) }, (d > 0 ? "+" : "") + d + "°"))));
    sec.append(el("div", { class: "row" }, el("button", { onclick: () => resetBone(n) }, "Đưa khớp này về gốc"), el("small", {}, "đã chỉnh: " + (Object.keys(S.pose.bones[n] || {}).join(", ") || "chưa có"))));
  }
  b.append(sec);
  b.append(section("Dáng mẫu (ghi lên dáng hiện tại)", el("div", { class: "presets" }, PRESETS.map(([t, ch]) => el("button", { onclick: () => applyPreset(ch) }, t)), el("button", { onclick: resetPose }, "Về dáng gốc"))));
  const lk = (S.rig.links || []).map((l) => `${l.name}: ${l.mode === "stretch" ? "dãn cơ" : "cả thân đi theo"}`).join(" · ") || "chưa có liên kết cơ";
  b.append(section("Khi kéo tay (thân đi theo thế nào)",
    el("div", { class: "mut" }, "Kéo bàn tay quá tầm: " + lk + ". Chỉnh ở tab 3."),
    slider({ label: el("span", {}, "Thân đi theo ", el("small", {}, "0–1")), min: 0, max: 1, step: 0.05, tip: "0 = thân đứng yên, 1 = thân nghiêng và dịch hết cỡ", get: () => chainOpt.follow, set: (v) => { chainOpt.follow = v; }, reset: () => { chainOpt.follow = 0.6; } }),
    el("div", { class: "row" }, el("label", {}, (() => { const c = el("input", { type: "checkbox", onchange: (e) => { chainOpt.stretch = e.target.checked; } }); c.checked = chainOpt.stretch; return c; })(), " Cho dãn xương tay khi không có liên kết cơ"))));
  const q = el("details", {}, el("summary", {}, "Chỉnh nhanh cả cơ thể bằng thanh trượt"));
  const sl = (label, nm, ch, min, max, sign = 1, tip) => slider({ label, min, max, step: 1, tip, get: () => sign * chVal(nm, ch), set: (v) => { if (!locked()) setCh(nm, ch, sign * v); }, reset: () => setCh(nm, ch, DEF[ch]) });
  q.append(sl("Ngồi xuống", "hips", "ty", 0, 100, 1, "hạ hông (px), gối tự gập"), sl("Nghiêng tới trước", "spine", "rot", -20, 35), sl("Cúi/ngẩng đầu", "head", "rot", -40, 40, -1, "dương = ngẩng lên"));
  for (const [side, nm] of [["near", "Tay gần"], ["far", "Tay xa"]]) q.append(sl(`${nm}: giơ ra trước`, `${side}_upper_arm`, "rot", -30, 140, -1, "0 = buông thõng, 90 = ngang vai"), sl(`${nm}: gập khuỷu`, `${side}_forearm`, "rot", -20, 150, -1), sl(`${nm}: cổ tay`, `${side}_hand`, "rot", -60, 60, -1));
  if (bone("near_foot_target")) for (const [side, nm] of [["near", "Chân gần"], ["far", "Chân xa"]]) q.append(sl(`${nm}: sang ngang`, `${side}_foot_target`, "tx", -200, 200), sl(`${nm}: nhấc lên`, `${side}_foot_target`, "ty", 0, 150, -1), sl(`${nm}: xoay bàn chân`, `${side}_foot`, "rot", -30, 30));
  q.append(sl("Vẫy đuôi", "tail", "rot", -70, 70));
  b.append(q);
}
const PRESETS = [
  ["Nhóm người", { hips: { ty: 70, tx: -15 }, spine: { rot: 18 }, head: { rot: -14 }, tail: { rot: -10 } }],
  ["Cào tới trước (tay gần)", { near_upper_arm: { rot: -78 }, near_forearm: { rot: -12 }, near_hand: { rot: -8 }, spine: { rot: 16 }, hips: { tx: 35 } }],
  ["Cào tới trước (tay xa)", { far_upper_arm: { rot: -78 }, far_forearm: { rot: -12 }, far_hand: { rot: -8 }, spine: { rot: 16 }, hips: { tx: 35 } }],
  ["Đứng rộng chân", { near_foot_target: { tx: -70 }, far_foot_target: { tx: 70 }, hips: { ty: 25 } }],
  ["Hai tay vươn ra trước", { near_upper_arm: { rot: -70 }, near_forearm: { rot: -15 }, far_upper_arm: { rot: -70 }, far_forearm: { rot: -15 }, spine: { rot: 10 } }],
];
function applyPreset(ch) {
  if (locked()) return blockedMsg();
  beginEdit(); for (const [n, v] of Object.entries(ch)) if (bone(n)) for (const [c, x] of Object.entries(v)) setCh(n, c, x); S.poseId = null; commitEdit();
}

// --- right: tab 2, joints and limits
function tabJoints() {
  const b = $("#rightBody"); b.replaceChildren(purpose("Cấu hình từng khớp: khớp cha (nối với đâu), tâm xoay, và giới hạn góc xoay để khớp không xoay quá mức (bàn chân không xoay 360°). Ghi vào rig, cần Lưu rig.", true));
  const n = S.sel;
  if (!n) { b.append(section("Khớp đang chọn", el("div", { class: "mut" }, "Chọn một khớp ở màn hình hoặc cây khớp bên trái. Bảng giới hạn của tất cả khớp ở dưới."))); }
  else {
    const bn = bone(n), sv = S.saved.bones.find((x) => x.name === n), banned = new Set([n, ...desc(n)]);
    const sel = el("select", { onchange: () => { beginEdit(); bn.parent = sel.value || null; S.rigSync = true; applyRigEdit(`Đã nối ${viName(n)} vào ${sel.value ? viName(sel.value) : "gốc"}`); } },
      el("option", { value: "" }, "(không có cha: gốc)"), S.rig.bones.filter((x) => !banned.has(x.name)).map((x) => el("option", { value: x.name, selected: x.name === bn.parent ? "" : null }, `${viName(x.name)} (${x.name})`)));
    sel.value = bn.parent || "";
    const ch = children(n);
    b.append(section(`Nối khớp: ${viName(n)}`,
      el("div", { class: "kv" }, el("span", {}, "Khớp cha ", el("span", { class: "chip stored" }, "lưu")), sel),
      el("div", { class: "kv" }, el("span", {}, "Khớp con ", el("span", { class: "chip stored" }, "lưu")), el("span", {}, ch.length ? ch.map((c, i) => [i ? ", " : "", boneLink(c.name)]) : "— (đầu mút)")),
      el("div", { class: "kv" }, el("span", {}, "Tâm xoay x, y ", el("span", { class: "chip stored" }, "lưu")), el("span", {}, numField(() => bn.pivot[0], (v) => { bn.pivot[0] = v; S.rigSync = true; }, 0.5), " ", numField(() => bn.pivot[1], (v) => { bn.pivot[1] = v; S.rigSync = true; }, 0.5), " ", el("button", { class: "rs", title: "Đưa tâm về bản đã lưu", onclick: () => { beginEdit(); bn.pivot = [...sv.pivot]; S.rigSync = true; commitEdit(); } }, "↺"))),
      el("div", { class: "mut" }, "Đổi khớp cha không làm hình đổi ở dáng gốc; nó đổi khớp nào kéo theo khớp nào khi xoay. Vòng lặp cha-con bị từ chối.")));
    const L = limitOf(n), explicit = bn.limit && "rot" in bn.limit;
    const free = el("input", { type: "checkbox", onchange: () => { beginEdit(); bn.limit = { rot: free.checked ? null : (DEFAULT_LIMITS[Object.keys(DEFAULT_LIMITS).find((k) => n === k || n.endsWith("_" + k))] || [-90, 90]) }; S.rigSync = true; commitEdit(); } });
    free.checked = !L;
    const lim = section("Giới hạn góc xoay (rot)", el("div", { class: "row" }, el("label", {}, free, " Không giới hạn (xoay tự do)"), explicit ? null : el("small", {}, "đang dùng mặc định của Studio")));
    if (L) {
      const setLim = (i, v) => { bn.limit = { ...(bn.limit || {}), rot: [...limitOf(n)] }; bn.limit.rot[i] = v; if (bn.limit.rot[0] >= bn.limit.rot[1]) bn.limit.rot[i === 0 ? 0 : 1] = i === 0 ? bn.limit.rot[1] - 1 : bn.limit.rot[0] + 1; S.rigSync = true; };
      lim.append(slider({ label: "Nhỏ nhất", min: -180, max: 0, step: 1, get: () => limitOf(n)[0], set: (v) => setLim(0, v), reset: () => { const d = DEFAULT_LIMITS[Object.keys(DEFAULT_LIMITS).find((k) => n === k || n.endsWith("_" + k))]; if (d) setLim(0, d[0]); } }),
        slider({ label: "Lớn nhất", min: 0, max: 180, step: 1, get: () => limitOf(n)[1], set: (v) => setLim(1, v), reset: () => { const d = DEFAULT_LIMITS[Object.keys(DEFAULT_LIMITS).find((k) => n === k || n.endsWith("_" + k))]; if (d) setLim(1, d[1]); } }),
        el("div", { class: "mut" }, `Góc hiện tại: ${fmt(chVal(n, "rot"))}°. Dương = xoay cùng chiều kim đồng hồ. Cung cam trên màn hình là vùng cho phép. Kéo, thanh trượt, phím và solver đều bị chặn trong khoảng này; mở pose đã lưu thì giữ nguyên giá trị.`));
    }
    b.append(lim);
    const ik = ikOf(n);
    if (ik) b.append(section("IK của chân này", el("div", { class: "row" }, el("label", {}, (() => { const c = el("input", { type: "checkbox", onchange: () => toggleIk(ik) }); c.checked = ikOn(ik); return c; })(), " Bàn chân bám đích (IK)")), el("div", { class: "mut" }, `Đùi → cẳng chân → bàn chân: ${ik.upper} → ${ik.lower} → ${ik.end_bone}. Đích: bone ${ik.target.bone}${footTarget(ik) ? " (kéo bàn chân để dời)" : " (cố định, không dời được)"}.`)));
  }
  const tb = el("table", { class: "tbl" }, el("tr", {}, el("th", {}, "Khớp"), el("th", {}, "Nhỏ nhất"), el("th", {}, "Lớn nhất")));
  for (const x of S.rig.bones) {
    const L = limitOf(x.name);
    tb.append(el("tr", { class: x.name === S.sel ? "on" : "", onclick: (e) => { if (e.target.tagName !== "INPUT") { S.sel = x.name; refreshPanels(); draw(); } } },
      el("td", {}, viName(x.name)), L ? el("td", {}, numField(() => limitOf(x.name)[0], (v) => { x.limit = { rot: [v, limitOf(x.name)[1]] }; if (x.limit.rot[0] >= x.limit.rot[1]) x.limit.rot[0] = x.limit.rot[1] - 1; S.rigSync = true; })) : el("td", { colspan: 2, class: "mut" }, "tự do"),
      L ? el("td", {}, numField(() => limitOf(x.name)[1], (v) => { x.limit = { rot: [limitOf(x.name)[0], v] }; if (x.limit.rot[0] >= x.limit.rot[1]) x.limit.rot[1] = x.limit.rot[0] + 1; S.rigSync = true; })) : null));
  }
  b.append(section("Giới hạn của tất cả khớp", tb, el("div", { class: "row" }, el("button", { onclick: () => { beginEdit(); for (const x of S.rig.bones) { const L = limitOf(x.name); if (L && !(x.limit && "rot" in x.limit)) x.limit = { rot: [...L] }; } S.rigSync = true; commitEdit(); toast("Đã ghi giới hạn mặc định vào rig (nhớ Lưu rig)"); } }, "Ghi giới hạn mặc định vào rig"))));
}

// --- right: tab 3, muscle links
function curLink() { return (S.rig.links || [])[S.selLink] || null; }
function tabLinks() {
  const b = $("#rightBody"); b.replaceChildren(purpose("Cơ & dây chằng: khi tay vươn quá tầm, cơ ngực dãn theo (đúng giải phẫu). Chọn một cánh tay, đặt vài điểm bám trên thân: chỉ vùng quanh các điểm đó dãn, không phải cả thân. Nhân vật không có cơ thì chọn 'cả thân đi theo'.", true));
  const links = S.rig.links || [];
  const list = el("div", { class: "list" }, links.map((l, i) => el("div", { class: i === S.selLink ? "on" : "", onclick: () => { S.selLink = i; if (bone(l.arm)) S.sel = l.arm; refreshPanels(); draw(); } }, el("span", { class: "dot", style: "background:#ff8ae6" }), l.name, el("small", {}, `${viName(l.arm)} · ${l.mode === "stretch" ? "dãn cơ" : "cả thân"} · ${(l.anchors || []).length} điểm bám`))));
  const arms = S.rig.bones.filter((x) => x.name.endsWith("upper_arm") && !linkOf(x.name));
  const add = el("select", {}, arms.map((x) => el("option", { value: x.name }, `${viName(x.name)} (${x.name})`)));
  b.append(section("Các liên kết cơ", links.length ? list : el("div", { class: "mut" }, "Chưa có liên kết nào."),
    arms.length ? el("div", { class: "row" }, add, el("button", { onclick: () => { beginEdit(); S.rig.links = S.rig.links || []; const side = add.value.split("_")[0]; S.rig.links.push({ name: `${side}_chest`, arm: add.value, mode: "stretch", max_pull: 90, anchors: [] }); S.selLink = S.rig.links.length - 1; S.rigSync = true; commitEdit(); } }, "+ Thêm liên kết")) : el("div", { class: "mut" }, "Mọi cánh tay đã có liên kết.")));
  const lk = curLink();
  if (!lk) return;
  const nm = el("input", { type: "text", value: lk.name, onchange: () => { beginEdit(); lk.name = nm.value.trim() || lk.name; commitEdit(); } });
  const mode = (v, title, desc) => el("label", { class: v === lk.mode ? "on" : "" }, (() => { const r = el("input", { type: "radio", name: "lkmode", onchange: () => { beginEdit(); lk.mode = v; S.rigSync = true; commitEdit(); } }); r.checked = lk.mode === v; return r; })(), el("span", {}, el("b", {}, title), el("br"), el("small", {}, desc)));
  b.append(section(`Liên kết: ${lk.name}`,
    el("div", { class: "kv" }, el("span", {}, "Tên"), nm), el("div", { class: "kv" }, el("span", {}, "Cánh tay"), boneLink(lk.arm)),
    el("div", { class: "modes" }, mode("stretch", "Dãn cơ (nhân vật có cơ)", "Vai trượt ra theo tay; chỉ vùng quanh các điểm bám bị kéo dãn. Thân vẫn ở yên."), mode("carry", "Cả thân đi theo (nhân vật không có cơ, ví dụ người đá)", "Không dãn gì cả: toàn bộ thân dịch và nghiêng theo tay.")),
    lk.mode === "stretch" ? slider({ label: "Vai trượt tối đa (px)", min: 0, max: 200, step: 1, tip: "bao xa vai được kéo ra khỏi thân", get: () => lk.max_pull ?? 80, set: (v) => { lk.max_pull = v; S.rigSync = true; }, reset: () => { lk.max_pull = 90; S.rigSync = true; } }) : null,
    el("div", { class: "row" }, el("button", { onclick: () => { beginEdit(); S.rig.links.splice(S.selLink, 1); S.selLink = 0; S.rigSync = true; commitEdit(); } }, "Xóa liên kết này"))));
  if (lk.mode !== "stretch") return;
  const an = section("Điểm bám trên thân");
  (lk.anchors || []).forEach((a, i) => {
    an.append(el("div", { style: "border-top:1px solid var(--line);padding-top:4px;margin-top:4px" }, el("div", { class: "row" }, el("b", {}, `Điểm ${i + 1}`), el("small", {}, `layer ${a.part}`), numField(() => a.pt[0], (v) => { a.pt[0] = v; S.rigSync = true; }, 1, 54), numField(() => a.pt[1], (v) => { a.pt[1] = v; S.rigSync = true; }, 1, 54), el("button", { onclick: () => { beginEdit(); lk.anchors.splice(i, 1); S.rigSync = true; commitEdit(); } }, "Xóa")),
      slider({ label: "Bán kính (px)", min: 20, max: 320, step: 1, tip: "vùng quanh điểm bám bị kéo", get: () => a.radius, set: (v) => { a.radius = Math.max(1, v); S.rigSync = true; }, reset: () => { a.radius = 140; S.rigSync = true; } }),
      slider({ label: "Độ mạnh", min: 0, max: 2, step: 0.05, tip: "1 = hình bám theo vai hoàn toàn ở tâm điểm bám", get: () => a.gain ?? 1, set: (v) => { a.gain = v; S.rigSync = true; }, reset: () => { a.gain = 1; S.rigSync = true; } })));
  });
  an.append(el("div", { class: "row" }, el("button", { class: S.tool === "anchor" ? "on rigmode" : "rigmode", onclick: () => { S.tool = S.tool === "anchor" ? "pose" : "anchor"; refreshPanels(); draw(); } }, S.tool === "anchor" ? "Đang đặt: bấm lên thân (Esc để thoát)" : "+ Đặt điểm bám bằng cách bấm lên hình")));
  b.append(an);
  const arm = lk.arm;
  b.append(section("Thử ngay: kéo vai ra",
    el("div", { class: "mut" }, "Trượt để xem cơ dãn theo (đây là dáng, không ghi vào rig)."),
    slider({ label: "Vai ra ngang (tx)", min: -150, max: 150, step: 1, get: () => chVal(arm, "tx"), set: (v) => { if (!locked()) setCh(arm, "tx", v); }, reset: () => setCh(arm, "tx", 0) }),
    slider({ label: "Vai lên/xuống (ty)", min: -150, max: 150, step: 1, get: () => chVal(arm, "ty"), set: (v) => { if (!locked()) setCh(arm, "ty", v); }, reset: () => setCh(arm, "ty", 0) })));
}
function placeAnchor(m) {
  const lk = curLink(); if (!lk) { toast("Chọn hoặc thêm một liên kết cơ ở tab 3 trước", true); return; }
  const part = S.rig.parts.find((p) => p.name === "torso") || S.rig.parts.find((p) => p.skin);
  if (!part) return;
  const q = invPt(world(part.bone), m[0], m[1]);
  beginEdit(); lk.anchors = lk.anchors || []; lk.anchors.push({ part: part.name, pt: [Math.round(q[0]), Math.round(q[1])], radius: 140, gain: 1 }); S.rigSync = true; commitEdit(); toast(`Đã đặt điểm bám ${lk.anchors.length} trên ${part.name}`);
}

// --- right: tab 4, rig editing
function tabRig() {
  const b = $("#rightBody"); b.replaceChildren(purpose("Sửa rig: vùng cắt (đa giác) của layer, độ mềm khớp uốn, đích IK và socket. Mọi thay đổi ghi vào rig, cần Lưu rig. Tâm khớp và giới hạn nằm ở tab 2.", true));
  b.append(section("Lưu rig", el("div", { class: "row" }, el("button", { class: rigDirty() ? "primary" : "", onclick: () => saveRig("overwrite") }, "Lưu rig (có backup)"), el("button", { onclick: () => saveRig("new") }, "Lưu thành bản mới")), el("div", { class: "mut" }, rigDirty() ? "Có thay đổi chưa lưu." : "Không có thay đổi chưa lưu.")));
  const p = S.editPart && partOf(S.editPart);
  const ps = section(`Vùng cắt: ${p ? p.name : "chưa chọn layer"}`);
  if (!p) ps.append(el("div", { class: "mut" }, "Ở tab Layer bên trái bấm 'Sửa vùng cắt' của một layer. Sau đó kéo các ô vuông trắng trên màn hình."));
  else if (!p.select.poly) ps.append(el("div", { class: "mut" }, "Layer này không cắt bằng đa giác."));
  else {
    const sv = S.saved.parts.find((q) => q.name === p.name);
    ps.append(el("div", { class: "mut" }, `${p.select.poly.length} đỉnh · kéo đỉnh trên màn hình · bấm đúp lên cạnh để thêm · Del để xóa đỉnh đang chọn. Vùng cắt tự cắt nhau bị từ chối.`));
    const list = el("div", { class: "list", style: "max-height:170px" });
    p.select.poly.forEach((q, i) => list.append(el("div", { class: i === S.selVert ? "on" : "", onclick: (e) => { if (e.target.tagName !== "INPUT") { S.selVert = i; refreshPanels(); draw(); } } }, el("span", { style: "width:18px" }, i), ...[0, 1].map((k) => { const nm = el("input", { type: "number", step: 1, style: "width:58px" }); bind(nm, () => partOf(p.name).select.poly[i][k]); nm.addEventListener("change", () => { const v = parseFloat(nm.value); if (!Number.isFinite(v)) return refreshValues(); beginEdit(); partOf(p.name).select.poly[i][k] = v; S.rigSync = true; applyRigEdit(); }); return nm; }))));
    ps.append(list, el("div", { class: "row" }, el("button", { onclick: () => addVertexAt(S.selVert ?? p.select.poly.length - 1, 0.5) }, "Thêm đỉnh"), el("button", { onclick: () => S.selVert !== null && deleteVertex(S.selVert), disabled: S.selVert === null ? "" : null }, "Xóa đỉnh"), el("button", { onclick: () => { beginEdit(); p.select.poly = clone(sv.select.poly); S.rigSync = true; applyRigEdit("Đã đưa vùng cắt về bản đã lưu"); } }, "Về bản đã lưu")));
  }
  b.append(ps);
  const js = section("Độ mềm khớp uốn (blend)", el("div", { class: "mut" }, "Dải điểm ảnh quanh khớp được uốn cong liền (2 × blend px). Càng lớn càng cong mượt, nhưng dễ méo. Không phải trọng số skin."));
  for (const q of S.rig.parts.filter((x) => x.skin).sort((a, c) => (c.skin.bones.includes(S.sel) ? 1 : 0) - (a.skin.bones.includes(S.sel) ? 1 : 0))) {
    const sv = S.saved.parts.find((x) => x.name === q.name);
    js.append(el("div", { style: "margin-top:6px;font-weight:600" }, q.name, el("small", {}, ` ${q.skin.bones.map(viName).join(" › ")}`)));
    for (const j of skinJoints(q)) {
      const svBl = sv ? (Array.isArray(sv.skin.blend) ? sv.skin.blend[j.idx] : sv.skin.blend) : null;
      const setBl = (v) => { const sk = partOf(q.name).skin; v = Math.max(1, v); if (!Array.isArray(sk.blend)) sk.blend = skinJoints(partOf(q.name)).map(() => sk.blend); sk.blend[j.idx] = v; S.rigSync = true; };
      const row = slider({ label: viName(j.bone), min: 1, max: 120, step: 1, tip: `đã lưu: ${svBl}`, get: () => skinJoints(partOf(q.name))[j.idx].blend, set: setBl, reset: () => setBl(svBl) });
      if (j.bone === S.sel) row.style.background = "var(--accbg)";
      js.append(row);
    }
  }
  js.append(el("div", { class: "row" }, el("button", { onclick: () => { beginEdit(); S.rig.parts.forEach((q) => { const s = S.saved.parts.find((x) => x.name === q.name); if (q.skin && s) q.skin = clone(s.skin); }); S.rigSync = true; applyRigEdit("Đã đưa độ mềm về bản đã lưu"); } }, "Đưa tất cả về bản đã lưu")));
  b.append(js);
  const ik = section("Đích IK và socket (số)");
  for (const k of S.rig.ik || []) ik.append(el("div", { class: "kv" }, el("span", {}, `Đích chân ${k.upper.startsWith("near") ? "gần" : "xa"}`), el("span", {}, numField(() => k.target.pt[0], (v) => { k.target.pt[0] = v; S.rigSync = true; }, 1, 58), " ", numField(() => k.target.pt[1], (v) => { k.target.pt[1] = v; S.rigSync = true; }, 1, 58))));
  for (const [n, s] of Object.entries(S.rig.sockets || {})) ik.append(el("div", { class: "kv" }, el("span", {}, `Socket ${n}`), el("span", {}, numField(() => s.pt[0], (v) => { s.pt[0] = v; S.rigSync = true; }, 1, 58), " ", numField(() => s.pt[1], (v) => { s.pt[1] = v; S.rigSync = true; }, 1, 58))));
  b.append(ik);
}

// --- right: tab 5, joint bend tester
const JOINTS = [
  { id: "near_elbow", label: "Khuỷu tay gần", bone: "near_forearm", flex: -1 }, { id: "far_elbow", label: "Khuỷu tay xa", bone: "far_forearm", flex: -1 },
  { id: "near_knee", label: "Gối gần", bone: "near_shin", flex: 1, fk: "near_thigh" }, { id: "far_knee", label: "Gối xa", bone: "far_shin", flex: 1, fk: "far_thigh" },
  { id: "near_shoulder", label: "Vai gần", bone: "near_upper_arm", flex: -1 }, { id: "far_shoulder", label: "Vai xa", bone: "far_upper_arm", flex: -1 },
  { id: "near_hip", label: "Hông (đùi gần)", bone: "near_thigh", flex: -1, fk: "near_thigh" }, { id: "far_hip", label: "Hông (đùi xa)", bone: "far_thigh", flex: -1, fk: "far_thigh" },
  { id: "neck", label: "Cổ / đầu", bone: "head", flex: -1 }, { id: "waist", label: "Eo (thân trên)", bone: "spine", flex: -1 },
  { id: "tail", label: "Đuôi", bone: "tail", flex: 1 }, { id: "near_foot", label: "Bàn chân gần", bone: "near_foot", flex: 1 }, { id: "far_foot", label: "Bàn chân xa", bone: "far_foot", flex: 1 },
];
const KNOWN = [["Gối rách: hạ hông 30 px", { "hips.ty": 30 }], ["Khuỷu gãy quanh -135°", { "near_forearm.rot": -135 }], ["Vai cắt phẳng quanh 80°", { "near_upper_arm.rot": 80 }], ["Cổ hở khe quanh -28°", { "head.rot": -28 }], ["Đuôi không uốn", { "tail.rot": 45 }], ["Bàn chân cứng", { "near_foot.rot": 35, "far_foot.rot": 35 }]];
const bend = { joint: "near_elbow", dir: 1, angle: 0 };
const bendJoint = () => JOINTS.find((j) => j.id === bend.joint && bone(j.bone)) || JOINTS.find((j) => bone(j.bone));
function withFree(fn) { freeLimits = true; try { fn(); } finally { freeLimits = false; } }
function applyBend(angle) {
  if (locked()) return blockedMsg();
  const j = bendJoint(); beginEdit();
  withFree(() => { if (j.fk && ikOf(j.bone)) S.pose.ik[ikOf(j.bone).upper] = false; setCh(j.bone, "rot", angle * j.flex * bend.dir); });
  S.sel = j.bone; bend.angle = angle; commitEdit();
}
function tabTest() {
  const b = $("#rightBody"); b.replaceChildren(purpose("Kiểm tra độ uốn của khớp (khuỷu, gối, vai…) ở nhiều góc để tìm chỗ hình bị rách, hở hay méo. Phần này bỏ qua giới hạn khớp để thử cả góc cực đoan."));
  const j = bendJoint(), sel = el("select", { onchange: () => { bend.joint = sel.value; refreshPanels(); } }, JOINTS.filter((x) => bone(x.bone)).map((x) => el("option", { value: x.id }, x.label)));
  sel.value = j.id;
  const signed = chVal(j.bone, "rot") * j.flex * bend.dir, sec = section("Chọn khớp và góc");
  sec.append(el("div", { class: "row" }, sel, el("button", { onclick: () => { bend.dir *= -1; refreshPanels(); }, title: "Uốn chiều ngược lại" }, "đổi chiều uốn")));
  sec.append(el("div", { class: "row" }, [0, 30, 45, 60, 90, 120].map((a) => el("button", { class: Math.abs(signed - a) < 0.5 ? "on" : "", onclick: () => applyBend(a) }, a + "°"))));
  sec.append(slider({ label: "Góc uốn", min: -150, max: 150, step: 1, get: () => chVal(j.bone, "rot") * j.flex * bend.dir, set: (v) => { if (locked()) return; withFree(() => { if (j.fk && ikOf(j.bone)) S.pose.ik[ikOf(j.bone).upper] = false; setCh(j.bone, "rot", v * j.flex * bend.dir); }); }, reset: () => withFree(() => setCh(j.bone, "rot", 0)) }));
  sec.append(el("div", { class: "mut" }, `điều khiển ${j.bone}.rot${j.fk ? " (chân được chuyển sang FK, vì IK sẽ che chỗ gập)" : ""}`));
  const rel = S.rig.parts.filter((p) => p.skin && p.skin.bones.includes(j.bone));
  sec.append(el("div", { class: "kv" }, el("span", {}, "Độ mềm (blend)"), el("span", {}, rel.length ? rel.map((p) => `${p.name}: ${skinJoints(p).filter((x) => x.bone === j.bone).map((x) => x.blend).join("")}`).join(" · ") : "layer cứng: không có độ mềm nên không uốn")));
  sec.append(el("div", { class: "row" }, el("button", { onclick: () => stripRender(j) }, "Xem trước 0 · 30 · 45 · 60 · 90 · 120°"), el("span", { id: "stripInfo", class: "mut" })), el("div", { id: "strip" }));
  b.append(sec);
  const kn = section("Lỗi đã biết: nạp dáng để tái hiện");
  for (const [t, ch] of KNOWN) kn.append(el("div", { class: "row" }, el("button", { onclick: () => loadTest(ch) }, "Nạp"), el("span", {}, t)));
  b.append(kn);
}
function loadTest(ch) {
  if (locked()) return blockedMsg();
  beginEdit(); S.pose = { bones: {}, ik: {} };
  withFree(() => { for (const [k, v] of Object.entries(ch)) { const [n, c] = k.split("."); setCh(n, c, v); } });
  S.poseId = null; commitEdit();
}
async function stripRender(j) {
  const box = $("#strip"), info = $("#stripInfo"); box.replaceChildren(); info.textContent = "đang vẽ…";
  try {
    if (S.rigSync) { await api("/api/rig/set", { rig: S.rig }); S.rigSync = false; }
    const piv = bone(j.bone).pivot, region = [piv[0] - 230, piv[1] - 150, 460, 460], t0 = performance.now(), base = clone(displayPose());
    for (const a of [0, 30, 45, 60, 90, 120]) {
      const pose = { bones: clone(base.bones || {}), ik: clone(base.ik || {}) };
      if (j.fk && ikOf(j.bone)) pose.ik[ikOf(j.bone).upper] = false;
      pose.bones[j.bone] = { ...(pose.bones[j.bone] || {}), rot: a * j.flex * bend.dir };
      const r = await api("/api/render", { scale: 0.5, region, layers: [{ src: "working", pose, hide: [...S.hide], primary: true }] });
      box.append(el("div", {}, el("img", { src: "data:image/png;base64," + r.png }), `${a}° · ${r.ms} ms`));
    }
    info.textContent = `${Math.round(performance.now() - t0)} ms`;
  } catch (e) { info.textContent = e.message; info.className = "err"; }
}

// ---------------------------------------------------------------- rig save / open
async function saveRig(mode) {
  if (S.bad) return toast("Sửa lỗi trước: " + S.bad, true);
  if (!rigDirty() && mode === "overwrite") return toast("Không có thay đổi rig để lưu");
  const msg = mode === "overwrite" ? `Ghi đè ${S.rigFile}? Bản sao lưu được đặt ở source/rig/backup/ trước.` : "Ghi rig thành file mới rig_studio_vNN.json (file cũ giữ nguyên)?";
  if (!(await modal({ title: mode === "overwrite" ? "Lưu rig" : "Lưu thành bản mới", text: msg, ok: "Lưu" }))) return;
  try {
    await api("/api/rig/set", { rig: S.rig });
    const r = await api("/api/rig/save", { rig: S.rig, mode });
    S.saved = clone(S.rig); S.rigFile = r.file; await loadState(false);
    toast(`Đã lưu ${r.file}${r.backup ? " · backup " + r.backup : ""}`);
  } catch (e) { toast(e.message, true, 6000); }
}
async function openRig(name, force) {
  if (!force && rigDirty() && !(await modal({ title: "Có thay đổi rig chưa lưu", text: "Bỏ các thay đổi chưa lưu và nạp lại từ đĩa?", ok: "Bỏ thay đổi" }))) { $("#rigFile").value = S.rigFile; return; }
  try {
    const r = await api("/api/open?file=" + encodeURIComponent(name));
    S.rig = r.rig; S.saved = clone(r.rig); S.parts = r.parts; S.rigFile = r.rig_file; S.topology = r.topology; S.rigSync = false; S.undo = []; S.redo = []; S.editPart = null; S.selVert = null; S.selLink = 0; S.cutRev++;
    buildRigSelect(); refreshPanels(); render("final"); toast(`Đã nạp ${name}`);
  } catch (e) { toast(e.message, true); }
}
function buildRigSelect() { const s = $("#rigFile"); s.replaceChildren(...S.rigFiles.map((f) => el("option", { value: f }, f))); s.value = S.rigFile; }

// ---------------------------------------------------------------- pose library
const labelOf = (ref) => (ref === "working" ? "Dáng đang làm" : ref === "rest" ? "Dáng gốc" : (S.poses.find((p) => p.id === ref) || {}).name || ref);
function buildLibrary() {
  const c = $("#cards"); c.replaceChildren();
  if (!S.poses.length) c.append(el("div", { class: "mut" }, "Chưa có pose nào. Tạo dáng cho Lion rồi bấm + Lưu pose."));
  for (const p of S.poses) {
    const stale = p.rig && p.rig.topology !== S.topology;
    c.append(el("div", { class: "card" + (S.libSel === p.id ? " on" : ""), title: `${p.name}\n${p.description || ""}\nid ${p.id}\ntạo ${p.created}\nsửa ${p.updated}${stale ? "\n⚠ lưu với cấu trúc rig khác" : ""}`, onclick: () => { S.libSel = p.id; S.libFocus = true; buildLibrary(); }, ondblclick: () => loadPose(p.id) },
      el("img", { src: `/poses/${p.id}.png?t=${encodeURIComponent(p.updated)}`, alt: p.name }), el("div", { class: "n" }, p.name + (S.poseId === p.id ? (poseDirty() ? " ●" : " ✓") : "")), el("div", { class: "m" }, p.id + (stale ? " ⚠" : "")), el("div", { class: "m" }, p.updated.replace("T", " ").slice(0, 16))));
  }
  for (const id of ["cmpA", "cmpB"]) { const s = $("#" + id); s.replaceChildren(el("option", { value: "working" }, "Dáng đang làm"), el("option", { value: "rest" }, "Dáng gốc"), ...S.poses.map((p) => el("option", { value: p.id }, p.name))); s.value = S.cmp[id === "cmpA" ? "a" : "b"]; }
  const has = !!S.libSel && S.poses.some((p) => p.id === S.libSel);
  ["pLoad", "pUpdate", "pDup", "pRename", "pDelete", "pExport"].forEach((i) => ($("#" + i).disabled = !has));
}
async function reloadPoses() { S.poses = (await api("/api/state")).poses; if (S.libSel && !S.poses.some((p) => p.id === S.libSel)) S.libSel = null; buildLibrary(); }
function loadPose(id) {
  const p = S.poses.find((q) => q.id === id); if (!p) return;
  if (S.cmp.on) exitCompare();
  beginEdit(); S.pose = { bones: clone(p.bones || {}), ik: clone(p.ik || {}) }; S.poseId = id; S.poseBase = cleanPose(); S.rest = false; $("#optRest").checked = false;   // loads restore the saved values exactly: no limit clamping
  const miss = Object.keys(p.bones || {}).filter((n) => !bone(n)); commitEdit();
  if (miss.length) toast(`Pose có khớp không có trong rig này (bị bỏ qua): ${miss.join(", ")}`, true, 6000);
  if (p.rig && p.rig.topology !== S.topology) toast("Pose này lưu với cấu trúc rig khác", true, 6000);
}
async function poseOp(body, msg) { try { const r = await api("/api/pose", body); await reloadPoses(); if (msg) toast(msg); return r; } catch (e) { toast(e.message, true, 6000); } }
$("#pNew").onclick = async () => {
  const f = await modal({ title: "Lưu pose mới", fields: [{ label: "Tên", value: "" }, { label: "Mô tả", value: "", area: true }], ok: "Lưu" });
  if (!f || !f[0].trim()) return;
  const r = await poseOp({ op: "save", name: f[0], description: f[1], pose: { bones: S.pose.bones, ik: S.pose.ik } }, `Đã lưu pose "${f[0]}"`);
  if (r) { S.libSel = r.id; S.poseId = r.id; S.poseBase = cleanPose(); buildLibrary(); updateStatus(); }
};
$("#pLoad").onclick = () => loadPose(S.libSel);
$("#pUpdate").onclick = async () => {
  const p = S.poses.find((q) => q.id === S.libSel);
  if (!(await modal({ title: "Cập nhật pose", text: `Ghi đè "${p.name}" bằng dáng đang làm?`, ok: "Cập nhật" }))) return;
  if (await poseOp({ op: "update", id: S.libSel, pose: { bones: S.pose.bones, ik: S.pose.ik } }, "Đã cập nhật pose")) { S.poseId = S.libSel; S.poseBase = cleanPose(); buildLibrary(); updateStatus(); }
};
$("#pDup").onclick = async () => { const r = await poseOp({ op: "duplicate", id: S.libSel }, "Đã nhân đôi pose"); if (r) { S.libSel = r.id; buildLibrary(); } };
$("#pRename").onclick = async () => {
  const p = S.poses.find((q) => q.id === S.libSel);
  const f = await modal({ title: "Đổi tên pose", fields: [{ label: "Tên", value: p.name }, { label: "Mô tả", value: p.description || "", area: true }], ok: "Đổi tên" });
  if (f && f[0].trim()) poseOp({ op: "rename", id: p.id, name: f[0], description: f[1] }, "Đã đổi tên pose");
};
async function deletePose() {
  const p = S.poses.find((q) => q.id === S.libSel); if (!p) return;
  if (!(await modal({ title: "Xóa pose", text: `Xóa "${p.name}"? File được chuyển vào poses/.trash/.`, ok: "Xóa" }))) return;
  if (await poseOp({ op: "delete", id: p.id }, "Đã xóa pose")) { if (S.poseId === p.id) S.poseId = null; S.libSel = null; buildLibrary(); updateStatus(); }
}
$("#pDelete").onclick = deletePose;
$("#pExport").onclick = () => { const a = el("a", { href: `/poses/${S.libSel}.json`, download: `${S.libSel}.json` }); document.body.append(a); a.click(); a.remove(); };
$("#pImport").onclick = () => $("#pFile").click();
$("#pFile").onchange = async (e) => {
  const f = e.target.files[0]; e.target.value = ""; if (!f) return;
  try {
    const d = JSON.parse(await f.text());
    if (typeof d.bones !== "object" || d.bones === null) throw new Error("Không phải file pose: thiếu mục bones");
    const r = await poseOp({ op: "import", name: d.name || f.name.replace(/\.json$/, ""), description: d.description || "", pose: d }, "Đã nhập pose");
    if (r) { S.libSel = r.id; buildLibrary(); }
  } catch (err) { toast(err.message, true); }
};
$("#pResetAll").onclick = resetPose;
function exitCompare() { S.cmp.on = false; render("final"); draw(); updateHint(); }
$("#cmpA").onchange = (e) => { S.cmp.a = e.target.value; S.cmp.on = true; S.cmp.showing = "a"; render("final"); updateHint(); };
$("#cmpB").onchange = (e) => { S.cmp.b = e.target.value; S.cmp.on = true; S.cmp.showing = "b"; render("final"); updateHint(); };
$("#cmpFlip").onclick = () => { S.cmp.showing = S.cmp.on && S.cmp.showing === "a" ? "b" : "a"; S.cmp.on = true; render("final"); updateHint(); };
$("#cmpOnion").checked = true; $("#cmpOnion").onchange = (e) => { S.cmp.onion = e.target.checked; render("final"); };
$("#cmpOff").onclick = exitCompare;

// ---------------------------------------------------------------- toolbar, keys, panels
$$("#tools button").forEach((b) => (b.onclick = () => { S.tool = b.dataset.tool; if (S.tool === "anchor") S.rightTab = "links"; refreshPanels(); draw(); }));
$$("#leftTabs button").forEach((b) => (b.onclick = () => { S.leftTab = b.dataset.tab; refreshPanels(); }));
$$("#rightTabs button").forEach((b) => (b.onclick = () => { S.rightTab = b.dataset.tab; if (S.tool === "anchor" && S.rightTab !== "links") S.tool = "pose"; refreshPanels(); draw(); }));
$("#btnUndo").onclick = undo; $("#btnRedo").onclick = redo;
$("#btnSave").onclick = () => saveRig("overwrite"); $("#btnSaveNew").onclick = () => saveRig("new");
$("#btnReload").onclick = () => openRig(S.rigFile);
$("#rigFile").onchange = (e) => openRig(e.target.value);
$("#optRest").onchange = (e) => { S.rest = e.target.checked; render("final"); updateHint(); };
$("#optQuality").onchange = () => render("final");
$("#btnZoomIn").onclick = () => { const r = cv.getBoundingClientRect(); zoomAt(1.25, r.width / 2, r.height / 2); };
$("#btnZoomOut").onclick = () => { const r = cv.getBoundingClientRect(); zoomAt(0.8, r.width / 2, r.height / 2); };
$("#btnFit").onclick = () => fit();
$("#btnActual1").onclick = () => { S.gameH = 60; actualSize(60); render("final"); };
$("#btnActual2").onclick = () => { S.gameH = 120; actualSize(120); render("final"); };
$("#btnHelp").onclick = showGuide;
$("#optBg").onchange = (e) => { S.bg = e.target.value; draw(); };
$("#optGrid").onchange = (e) => { S.grid = e.target.checked; draw(); };
$("#optChar").onchange = (e) => { S.showChar = e.target.checked; draw(); };
$("#optGhostRig").onchange = (e) => { S.ghostRig = e.target.checked; render("final"); };
$$("[data-vis]").forEach((c) => (c.onchange = () => { S.vis[c.dataset.vis] = c.checked; draw(); }));

document.addEventListener("keydown", (e) => {
  const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) && !["range", "checkbox", "radio"].includes(document.activeElement.type);
  const mod = e.ctrlKey || e.metaKey, k = e.key.toLowerCase();
  if (e.code === "Space" && !typing) { spaceDown = true; e.preventDefault(); }
  if (!$("#modal").hidden) return;
  if (mod && k === "s") { e.preventDefault(); saveRig("overwrite"); return; }
  if (typing) return;
  if (mod && k === "z") { e.preventDefault(); e.shiftKey ? redo() : undo(); return; }
  if (mod && k === "y") { e.preventDefault(); redo(); return; }
  if (mod) return;
  if (k === "v") S.tool = "pose"; else if (k === "e") S.tool = "rotate"; else if (k === "w") S.tool = "move"; else if (k === "p") S.tool = "pivot"; else if (k === "a") { S.tool = "anchor"; S.rightTab = "links"; }
  else if (k === "f") fit();
  else if (k === "h") { showGuide(); return; }
  else if (e.key === "Escape") { if (S.tool !== "pose") S.tool = "pose"; else if (S.editPart) { S.editPart = null; S.selVert = null; } else { S.sel = null; S.selPart = null; } }
  else if (e.key === "Tab") { e.preventDefault(); const names = S.rig.bones.map((b) => b.name), i = names.indexOf(S.sel); S.sel = names[(i + (e.shiftKey ? -1 : 1) + names.length) % names.length]; }
  else if (e.key.startsWith("Arrow") && S.sel) {
    e.preventDefault(); const st = e.shiftKey ? 5 : 1;
    if (S.tool === "move") { if (e.key === "ArrowLeft") nudge(S.sel, "tx", -st); else if (e.key === "ArrowRight") nudge(S.sel, "tx", st); else if (e.key === "ArrowUp") nudge(S.sel, "ty", -st); else nudge(S.sel, "ty", st); }
    else if (e.key === "ArrowLeft") nudge(S.sel, "rot", -st); else if (e.key === "ArrowRight") nudge(S.sel, "rot", st);
    return;
  } else if (e.key === "Delete" || e.key === "Backspace") {
    if (S.editPart && S.selVert !== null) deleteVertex(S.selVert); else if (S.libFocus && S.libSel) deletePose(); else if (S.sel) resetBone(S.sel);
  } else return;
  refreshPanels(); draw();
});
document.addEventListener("keyup", (e) => { if (e.code === "Space") spaceDown = false; });
window.addEventListener("beforeunload", (e) => { if (rigDirty() || poseDirty()) { e.preventDefault(); e.returnValue = ""; } });
window.addEventListener("resize", resize);

function splitter(id, axis, target, min, max, invert) {
  const s = $(id); let st = null;
  s.addEventListener("pointerdown", (e) => { s.setPointerCapture(e.pointerId); const r = target().getBoundingClientRect(); st = { x: e.clientX, y: e.clientY, w: r.width, h: r.height }; });
  s.addEventListener("pointermove", (e) => { if (!st) return; const d = axis === "x" ? e.clientX - st.x : e.clientY - st.y, v = Math.max(min, Math.min(max, (axis === "x" ? st.w : st.h) + (invert ? -d : d))); target().style[axis === "x" ? "width" : "height"] = v + "px"; resize(); });
  s.addEventListener("pointerup", () => (st = null));
}
splitter("#splitL", "x", () => $("#left"), 220, 620, false);
splitter("#splitR", "x", () => $("#right"), 280, 700, true);
splitter("#splitB", "y", () => $("#library"), 80, 500, true);

// ---------------------------------------------------------------- boot
async function loadState(first) {
  const st = await api("/api/state");
  S.rig = st.rig; S.saved = clone(st.rig); S.parts = st.parts; S.rigFile = st.rig_file; S.rigFiles = st.rig_files; S.topology = st.topology; S.poses = st.poses;
  S.rigSync = false; S.undo = []; S.redo = []; S.cutRev++;
  buildRigSelect();
  if (first) {
    const a = st.autosave;
    if (a && a.rig_file === st.rig_file && (JSON.stringify(a.rig) !== JSON.stringify(st.rig) || Object.keys((a.pose || {}).bones || {}).length)) {
      const yes = await modal({ title: "Khôi phục bản tự lưu?", text: `Có bản làm dở lúc ${a.time.replace("T", " ").slice(0, 19)} (sửa rig: ${a.rig_dirty ? "có" : "không"}, số khớp đã chỉnh: ${Object.keys(a.pose.bones || {}).length}).`, ok: "Khôi phục" });
      if (yes) { S.rig = a.rig; S.pose = { bones: a.pose.bones || {}, ik: a.pose.ik || {} }; S.rigSync = true; } else api("/api/autosave/clear", {});
    }
  }
  refreshPanels();
}
(async () => {
  resize();
  try {
    await loadState(true); fit(); render("final");
    let seen = false; try { seen = localStorage.getItem("studioGuideSeen2") === "1"; localStorage.setItem("studioGuideSeen2", "1"); } catch (e) { /* storage blocked: show the guide each time */ }
    if (!seen) showGuide();
  } catch (e) { toast("Không kết nối được server Studio: " + e.message, true, 20000); }
})();
