"use strict";
// Lion Rig & Pose Studio client. Pixels come from the Puppet Kit (server /api/render); this file only draws overlays and edits data.

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else if (v !== null && v !== undefined) e.setAttribute(k, v);
  }
  for (const c of kids.flat(Infinity)) if (c !== null && c !== undefined) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
};
const clone = (o) => JSON.parse(JSON.stringify(o));
const r1 = (v) => Math.round(v * 10) / 10;
const DEF = { rot: 0, tx: 0, ty: 0, sx: 1, sy: 1, shx: 0 };
const CH = Object.keys(DEF);
const DRAFT = 0.3;

const S = {
  rig: null, saved: null, parts: [], rigFile: "rig.json", rigFiles: [], topology: "",
  pose: { bones: {}, ik: {} }, poseBase: "{\"bones\":{},\"ik\":{}}", poseId: null,
  tool: "chain", reach: "near_hand", sel: null, hover: null, mouse: null, editPart: null, selVert: null, libSel: null, libFocus: false,
  vis: { skeleton: true, labels: true, pivots: true, bounds: false, polys: false, skin: false, rigid: false, sockets: true, ik: true, influence: true },
  hide: new Set(), rest: false, bg: "dark", grid: true, showChar: true, ghostRig: false,
  view: { zoom: 0.6, px: 0, py: 0 }, poses: [], rigSync: true,
  render: null, img: null, game: null, gameH: 60, bad: null,
  cmp: { on: false, a: "working", b: "rest", showing: "a", onion: true },
  undo: [], redo: [],
};

// ---------------------------------------------------------------- api
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
function invPt(m, x, y) {
  const i = inv2(m), dx = x - m[4], dy = y - m[5];
  return [i[0] * dx + i[2] * dy, i[1] * dx + i[3] * dy];
}
const posedPivot = (n) => { const b = bone(n); return mapPt(world(n), b.pivot[0], b.pivot[1]); };
function boneEnd(n) {
  const c = children(n)[0];
  if (c) return { pt: posedPivot(c.name), from: `child ${c.name}` };
  for (const p of S.rig.parts) {
    const sk = p.skin;
    if (sk && sk.bones[sk.bones.length - 1] === n) return { pt: mapPt(world(n), sk.tip[0], sk.tip[1]), from: `skin tip of ${p.name}`, rest: sk.tip };
  }
  return null;
}
function boneEndRest(n) {
  const c = children(n)[0];
  if (c) return { rest: c.pivot, from: `child ${c.name}` };
  for (const p of S.rig.parts) if (p.skin && p.skin.bones[p.skin.bones.length - 1] === n) return { rest: p.skin.tip, from: `skin tip of ${p.name}` };
  return null;
}
const chVal = (n, ch) => ((S.pose.bones[n] || {})[ch] ?? DEF[ch]);
function setCh(n, ch, v) {
  const o = (S.pose.bones[n] = S.pose.bones[n] || {});
  if (Math.abs(v - DEF[ch]) < 1e-9) delete o[ch]; else o[ch] = v;
  if (!Object.keys(o).length) delete S.pose.bones[n];
}
const ikOf = (n) => (S.rig.ik || []).find((i) => i.upper === n || i.lower === n);
const ikOn = (ik) => S.pose.ik[ik.upper] !== false;
const ikDriven = (n) => { const i = ikOf(n); return !!i && ikOn(i); };
const rigDirty = () => JSON.stringify(S.rig) !== JSON.stringify(S.saved);
const cleanPose = () => JSON.stringify({ bones: S.pose.bones, ik: S.pose.ik });
const poseDirty = () => cleanPose() !== S.poseBase;
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
    if (q === "final" && drag && drag.type !== "pan") { finalTimer = setTimeout(() => render("final"), 450); continue; }
    $("#loading").textContent = "rendering…"; $("#loading").className = "busy";
    try { await renderNow(q); S.bad = null; } catch (e) { S.bad = e.message; toast(e.message, true, 6000); }
    $("#loading").textContent = ""; $("#loading").className = "";
  }
  rendering = false; updateStatus(); draw();
}
function layersFor(pose) {
  const hide = [...S.hide];
  const L = [];
  if (S.ghostRig) L.push({ src: "saved", pose, hide, alpha: 0.4 });
  if (S.cmp.on && S.cmp.onion) {
    const other = poseByRef(S.cmp[S.cmp.showing === "a" ? "b" : "a"]);
    L.push({ src: "working", pose: other, hide, alpha: 0.35 });
  }
  L.push({ src: "working", pose, hide, primary: true });
  return L;
}
const loadImg = (b64) => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = "data:image/png;base64," + b64; });
async function renderNow(q) {
  if (S.rigSync) {
    const snapshotRig = S.rig;
    const r = await api("/api/rig/set", { rig: snapshotRig });
    if (snapshotRig === S.rig) S.rigSync = false;
    if (r.rebuilt) $("#renderInfo").dataset.rebuilt = r.ms;
  }
  const pose = displayPose();
  const final = q === "final", scale = final ? parseFloat($("#optQuality").value) : DRAFT;
  const gs = S.gameH / S.rig.unit;
  const body = { scale, draft: !final, region: [-60, -60, 1144, 1144], layers: layersFor(pose) };
  if (final) body.game = { scale: gs, region: [S.rig.ground[0] - 360, S.rig.ground[1] - S.rig.unit * 1.12, 720, S.rig.unit * 1.2] };
  const res = await api("/api/render", body);
  const img = await loadImg(res.png);
  S.render = res; S.img = img; S.renderQ = q;
  if (res.game_png) S.game = await loadImg(res.game_png);
  draw();
}
function updateStatus() {
  const r = S.render;
  $("#renderInfo").textContent = r ? `${S.renderQ === "final" ? "final" : "draft"} ${r.size[0]}×${r.size[1]} · ${r.ms} ms` : "";
  const rd = rigDirty(), pd = poseDirty();
  $("#dirtyRig").textContent = rd ? "● rig unsaved" : "rig saved"; $("#dirtyRig").className = rd ? "d" : "";
  $("#dirtyPose").textContent = pd ? `● pose ${S.poseId ? "modified" : "not in library"}` : (S.poseId ? `pose: ${S.poseId}` : "pose: rest"); $("#dirtyPose").className = pd ? "d" : "";
  $("#btnUndo").disabled = !S.undo.length; $("#btnRedo").disabled = !S.redo.length;
}

// ---------------------------------------------------------------- viewport
const cv = $("#vp"), ctx = cv.getContext("2d");
const toScreen = (x, y) => [x * S.view.zoom + S.view.px, y * S.view.zoom + S.view.py];
const toRig = (sx, sy) => [(sx - S.view.px) / S.view.zoom, (sy - S.view.py) / S.view.zoom];
function resize() {
  const r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1;
  cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d); draw();
}
function fit(box = [60, 60, 900, 900]) {
  const r = cv.getBoundingClientRect(), z = Math.min(r.width / box[2], r.height / box[3]) * 0.92;
  S.view.zoom = z; S.view.px = r.width / 2 - (box[0] + box[2] / 2) * z; S.view.py = r.height / 2 - (box[1] + box[3] / 2) * z; draw();
}
function zoomAt(f, sx, sy) {
  const [rx, ry] = toRig(sx, sy);
  S.view.zoom = Math.max(0.05, Math.min(12, S.view.zoom * f));
  S.view.px = sx - rx * S.view.zoom; S.view.py = sy - ry * S.view.zoom; draw();
}
function actualSize(h) {
  const r = cv.getBoundingClientRect(), z = h / S.rig.unit;
  S.view.zoom = z; S.view.px = r.width / 2 - S.rig.ground[0] * z; S.view.py = r.height / 2 - (S.rig.ground[1] - S.rig.unit / 2) * z; draw();
}

function poly(pts, close = true) {
  ctx.beginPath();
  pts.forEach((p, i) => { const [x, y] = toScreen(p[0], p[1]); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
  if (close) ctx.closePath();
}
const rect = (off, size) => [[off[0], off[1]], [off[0] + size[0], off[1]], [off[0] + size[0], off[1] + size[1]], [off[0], off[1] + size[1]]];
const partTransform = (p) => world(p.bone);
const posedPoly = (p) => p.select.poly.map((q) => mapPt(partTransform(p), q[0], q[1]));

let drawQueued = false;
function draw() {
  if (drawQueued) return;
  drawQueued = true;
  requestAnimationFrame(() => { drawQueued = false; drawNow(); });
}
function drawNow() {
  if (!S.rig) return;
  const d = window.devicePixelRatio || 1, W = cv.width / d, H = cv.height / d;
  ctx.setTransform(d, 0, 0, d, 0, 0);
  const bgc = { dark: "#262b33", light: "#d9dde3", green: "#2f8f4a", check: "#2a2f37" }[S.bg];
  ctx.fillStyle = bgc; ctx.fillRect(0, 0, W, H);
  if (S.bg === "check") {
    ctx.fillStyle = "#353b45";
    for (let y = 0; y < H; y += 24) for (let x = ((y / 24) % 2) * 24; x < W; x += 48) ctx.fillRect(x, y, 24, 24);
  }
  if (S.grid) {
    ctx.lineWidth = 1; ctx.font = "10px monospace";
    const step = S.view.zoom > 0.9 ? 50 : 100;
    const [x0, y0] = toRig(0, 0), [x1, y1] = toRig(W, H);
    for (let x = Math.floor(x0 / step) * step; x < x1; x += step) { const sx = toScreen(x, 0)[0]; ctx.strokeStyle = x % 500 === 0 ? "#ffffff30" : "#ffffff12"; ctx.beginPath(); ctx.moveTo(sx, 0); ctx.lineTo(sx, H); ctx.stroke(); }
    for (let y = Math.floor(y0 / step) * step; y < y1; y += step) { const sy = toScreen(0, y)[1]; ctx.strokeStyle = y % 500 === 0 ? "#ffffff30" : "#ffffff12"; ctx.beginPath(); ctx.moveTo(0, sy); ctx.lineTo(W, sy); ctx.stroke(); }
    const gy = toScreen(0, S.rig.ground[1])[1];
    ctx.strokeStyle = "#4cd08a99"; ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke();
  }
  if (S.img && S.showChar && S.render) {
    const [x0, y0, w, h] = S.render.region, [sx, sy] = toScreen(x0, y0);
    ctx.imageSmoothingEnabled = S.view.zoom * S.render.scale < 1.5 || S.view.zoom > S.render.scale; ctx.imageSmoothingQuality = "high";
    ctx.drawImage(S.img, sx, sy, w * S.view.zoom, h * S.view.zoom);
  }
  drawOverlay();
  drawGame();
}

function drawGame() {
  const g = $("#game");
  if (!S.game) return;
  const k = S.gameH === 60 ? 3 : 2;
  g.width = S.game.width; g.height = S.game.height; g.style.width = g.width * k + "px"; g.style.height = g.height * k + "px";
  const c = g.getContext("2d"); c.imageSmoothingEnabled = false; c.fillStyle = "#3a414c"; c.fillRect(0, 0, g.width, g.height); c.drawImage(S.game, 0, 0);
  $("#gameCap").textContent = `Game size: H=${S.gameH}px @${S.gameH === 60 ? "1x" : "2x"} (shown ${k}×, ${g.width}×${g.height}px)`;
}

function drawOverlay() {
  if (!S.render) return;
  const V = S.vis, selB = S.sel;
  const sel = selB ? new Set([selB, ...desc(selB)]) : new Set();
  // layers: polygons (posed by the bone's rigid transform: exact at rest, approximate where a skin bends)
  for (const p of S.rig.parts) {
    const isSkin = !!p.skin, show = (isSkin && V.skin) || (!isSkin && V.rigid) || V.polys || S.editPart === p.name;
    const infl = V.influence && selB && (p.bone === selB || (p.skin && p.skin.bones.includes(selB)));
    if (V.bounds) {
      const m = S.parts.find((q) => q.name === p.name);
      if (m) { const pts = rect(m.off, m.size).map((q) => mapPt(partTransform(p), q[0], q[1])); poly(pts); ctx.strokeStyle = "#ffffff90"; ctx.setLineDash([4, 3]); ctx.lineWidth = 1; ctx.stroke(); ctx.setLineDash([]); }
    }
    if (!p.select.poly || !(show || infl)) continue;
    poly(posedPoly(p));
    ctx.fillStyle = infl ? "#ffc83d40" : isSkin ? "#b57bff22" : "#3fd1c522"; ctx.fill();
    ctx.strokeStyle = S.editPart === p.name ? "#fff" : infl ? "#ffc83d" : isSkin ? "#c58bff" : "#4fd1c5"; ctx.lineWidth = S.editPart === p.name ? 2 : 1.2; ctx.stroke();
  }
  if (V.skin) for (const p of S.rig.parts) if (p.skin) drawSkinBands(p);
  if (V.influence && selB) {
    for (const n of sel) if (n !== selB) { const e = boneEnd(n); if (e) { line(posedPivot(n), e.pt, "#ffc83d66", 5); } }
  }
  if (V.skeleton) {
    for (const b of S.rig.bones) {
      const P = posedPivot(b.name), isSel = b.name === selB;
      if (b.parent) { const Q = posedPivot(b.parent); const pe = boneEnd(b.parent); if (!pe || Math.hypot(pe.pt[0] - P[0], pe.pt[1] - P[1]) > 1) line(Q, P, "#ffffff55", 1.5, [3, 3]); }
      const e = boneEnd(b.name);
      if (e) boneShape(P, e.pt, isSel ? "#ffd84a" : sideColor(b.name), isSel);
    }
  }
  if (V.pivots || V.skeleton) {
    for (const b of S.rig.bones) {
      const [x, y] = toScreen(...posedPivot(b.name)), isSel = b.name === selB;
      ctx.beginPath(); ctx.arc(x, y, isSel ? 7 : 4.5, 0, 7); ctx.fillStyle = isSel ? "#ffd84a" : "#101319"; ctx.fill();
      ctx.lineWidth = 2; ctx.strokeStyle = isSel ? "#fff" : sideColor(b.name); ctx.stroke();
    }
  }
  if (V.labels) {
    ctx.font = "11px system-ui"; ctx.textBaseline = "middle";
    for (const b of S.rig.bones) {
      const [x, y] = toScreen(...posedPivot(b.name));
      ctx.fillStyle = "#000b"; const w = ctx.measureText(b.name).width; ctx.fillRect(x + 8, y - 8, w + 6, 15);
      ctx.fillStyle = b.name === selB ? "#ffd84a" : "#fff"; ctx.fillText(b.name, x + 11, y);
    }
  }
  if (V.sockets) for (const [n, s] of Object.entries(S.rig.sockets || {})) {
    const [x, y] = toScreen(...mapPt(world(s.bone), s.pt[0], s.pt[1]));
    ctx.strokeStyle = "#7dff7d"; ctx.lineWidth = 2; ctx.strokeRect(x - 5, y - 5, 10, 10);
    ctx.fillStyle = "#7dff7d"; ctx.font = "10px system-ui"; ctx.fillText(n, x + 8, y + 12);
  }
  if (V.ik) for (const ik of S.rig.ik || []) {
    const [x, y] = toScreen(...mapPt(world(ik.target.bone), ik.target.pt[0], ik.target.pt[1])), on = ikOn(ik);
    ctx.beginPath(); ctx.moveTo(x, y - 8); ctx.lineTo(x + 8, y); ctx.lineTo(x, y + 8); ctx.lineTo(x - 8, y); ctx.closePath();
    ctx.strokeStyle = on ? "#ff5edb" : "#888"; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = ctx.strokeStyle; ctx.font = "10px system-ui"; ctx.fillText(`IK ${ik.upper.split("_")[0]}${on ? "" : " (FK)"}`, x + 10, y - 10);
  }
  if (drag && drag.type === "chain" && drag.target) {
    const [x, y] = toScreen(...drag.target); ctx.strokeStyle = drag.residual > 3 ? "#ff6b6b" : "#4cd08a"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, y, 9, 0, 7); ctx.moveTo(x - 14, y); ctx.lineTo(x + 14, y); ctx.moveTo(x, y - 14); ctx.lineTo(x, y + 14); ctx.stroke();
    ctx.fillStyle = ctx.strokeStyle; ctx.font = "11px system-ui"; ctx.fillText(drag.residual > 3 ? `out of reach by ${Math.round(drag.residual)} px` : "reached", x + 12, y - 12);
  }
  drawGizmos();
  if (S.editPart) drawVertices();
  drawPointer();
  if (S.cmp.on) { ctx.fillStyle = "#000b"; ctx.fillRect(8, 8, 220, 22); ctx.fillStyle = "#ffd84a"; ctx.font = "12px system-ui"; ctx.fillText(`COMPARE (view only): ${labelOf(S.cmp[S.cmp.showing])}`, 14, 19); }
}
function ring(x, y, r, col, w = 2, dash = []) { ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.setLineDash(dash); ctx.stroke(); ctx.setLineDash([]); }
function drawGizmos() {
  if (S.cmp.on) return;
  const pulse = 0.5 + 0.5 * Math.sin(performance.now() / 300);
  if (S.reach && S.tool === "chain" && S.mouse) {
    const e = boneEnd(S.reach);
    if (e) { const [x, y] = toScreen(...e.pt); ctx.strokeStyle = "#4cd08a"; ctx.lineWidth = 2; ctx.setLineDash([6, 5]); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(S.mouse[0], S.mouse[1]); ctx.stroke(); ctx.setLineDash([]); ring(x, y, 13, "#4cd08a", 3); ring(S.mouse[0], S.mouse[1], 10, "#4cd08a", 2); }
  }
  if (S.tool === "chain" || S.tool === "select") {                 // grab points: the tips of the limbs
    for (const b of S.rig.bones) {
      if (!isLeaf(b.name)) continue;
      const e = boneEnd(b.name); if (!e) continue;
      const [x, y] = toScreen(...e.pt), on = b.name === S.sel || (S.hover && S.hover.id === b.name);
      ring(x, y, on ? 14 : 11 + pulse * 2, on ? "#ffd84a" : "#ffffffcc", on ? 3 : 2);
      ctx.fillStyle = on ? "#ffd84a" : "#ffffff55"; ctx.beginPath(); ctx.arc(x, y, 4, 0, 7); ctx.fill();
    }
  }
  if (S.tool === "chain" || S.tool === "select") for (const ik of S.rig.ik || []) {
    if (!footTarget(ik)) continue;
    const [x, y] = toScreen(...ikTargetWorld(ik)), on = ik.end_bone === S.sel || (S.hover && S.hover.id === ik.end_bone);
    ring(x, y, on ? 15 : 12 + pulse * 2, on ? "#ffd84a" : "#ff8ae6", on ? 3 : 2);
  }
  if (S.sel && S.tool === "rotate") { const [x, y] = toScreen(...posedPivot(S.sel)); ring(x, y, 48, "#ffd84a", 2, [6, 5]); ring(x, y, 52, "#ffd84a55", 6); ctx.fillStyle = "#ffd84a"; ctx.font = "12px system-ui"; ctx.fillText(`${S.sel} rot ${fmt(chVal(S.sel, "rot"))}°`, x + 56, y - 4); }
  if (S.sel && S.tool === "move") { const [x, y] = toScreen(...posedPivot(S.sel)); ctx.strokeStyle = "#ffd84a"; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x - 30, y); ctx.lineTo(x + 30, y); ctx.moveTo(x, y - 30); ctx.lineTo(x, y + 30); ctx.stroke(); ctx.fillStyle = "#ffd84a"; ctx.font = "12px system-ui"; ctx.fillText(`tx ${fmt(chVal(S.sel, "tx"))}  ty ${fmt(chVal(S.sel, "ty"))}`, x + 34, y - 8); }
  if (S.hover && S.hover.kind === "bone") {
    const [x, y] = toScreen(...posedPivot(S.hover.id)); ring(x, y, 16, "#ffffff", 2);
    ctx.font = "12px system-ui"; const w = ctx.measureText(S.hover.id).width; ctx.fillStyle = "#000d"; ctx.fillRect(x + 20, y - 26, w + 12, 20); ctx.fillStyle = "#fff"; ctx.fillText(S.hover.id, x + 26, y - 12);
  }
}
function drawPointer() {
  if (!S.mouse) return;
  const [x, y] = S.mouse, hot = !!S.hover || (drag && drag.type !== "pan");
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 3, y + 17); ctx.lineTo(x + 7.5, y + 12.5); ctx.lineTo(x + 13, y + 12); ctx.closePath();
  ctx.fillStyle = hot ? "#ffd84a" : "#ffffff"; ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5; ctx.fill(); ctx.stroke();
}
function line(a, b, col, w, dash = []) {
  const [x0, y0] = toScreen(...a), [x1, y1] = toScreen(...b);
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.strokeStyle = col; ctx.lineWidth = w; ctx.setLineDash(dash); ctx.stroke(); ctx.setLineDash([]);
}
function boneShape(a, b, col, sel) {
  const [x0, y0] = toScreen(...a), [x1, y1] = toScreen(...b), dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1;
  const nx = -dy / L, ny = dx / L, w = Math.min(7, L * 0.14) + (sel ? 1.5 : 0);
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + dx * 0.15 + nx * w, y0 + dy * 0.15 + ny * w); ctx.lineTo(x1, y1); ctx.lineTo(x0 + dx * 0.15 - nx * w, y0 + dy * 0.15 - ny * w); ctx.closePath();
  ctx.fillStyle = col + (sel ? "cc" : "66"); ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = sel ? 2 : 1.2; ctx.stroke();
}
function desc(n) { const out = []; const walk = (x) => children(x).forEach((c) => { out.push(c.name); walk(c.name); }); walk(n); return out; }

function skinJoints(p) {
  const sk = p.skin, js = [];
  for (let i = 1; i < sk.bones.length; i++) {
    const b = bone(sk.bones[i]), nxt = i + 1 < sk.bones.length ? bone(sk.bones[i + 1]).pivot : sk.tip;
    const dx = nxt[0] - b.pivot[0], dy = nxt[1] - b.pivot[1], L = Math.hypot(dx, dy) || 1;
    const bl = Array.isArray(sk.blend) ? sk.blend[i - 1] : sk.blend;
    js.push({ bone: b.name, piv: b.pivot, axis: [dx / L, dy / L], blend: bl, idx: i - 1 });
  }
  return js;
}
function drawSkinBands(p) {
  for (const j of skinJoints(p)) {
    const m = world(j.bone), nx = -j.axis[1], ny = j.axis[0], hw = 90, bl = j.blend;
    const q = (a, s) => [j.piv[0] + j.axis[0] * a + nx * s, j.piv[1] + j.axis[1] * a + ny * s];
    const band = [q(-bl, -hw), q(bl, -hw), q(bl, hw), q(-bl, hw)].map((c) => mapPt(m, c[0], c[1]));
    poly(band); ctx.fillStyle = "#ff6bd622"; ctx.fill(); ctx.strokeStyle = "#ff6bd6"; ctx.lineWidth = 1; ctx.stroke();
    const c0 = mapPt(m, ...q(0, -hw)), c1 = mapPt(m, ...q(0, hw)); line(c0, c1, "#ff6bd688", 1, [3, 3]);
  }
}
function drawVertices() {
  const p = partOf(S.editPart); if (!p || !p.select.poly) return;
  const pts = posedPoly(p);
  pts.forEach((q, i) => {
    const [x, y] = toScreen(q[0], q[1]), on = i === S.selVert;
    ctx.fillStyle = on ? "#ffd84a" : "#fff"; ctx.strokeStyle = "#000"; ctx.lineWidth = 1;
    ctx.fillRect(x - 4, y - 4, 8, 8); ctx.strokeRect(x - 4, y - 4, 8, 8);
    ctx.fillStyle = "#fff"; ctx.font = "9px monospace"; ctx.fillText(i, x + 6, y - 6);
  });
}

// ---------------------------------------------------------------- pointer interaction
let drag = null, spaceDown = false;
const canvasXY = (e) => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };

function pickVertex(sx, sy) {
  if (!S.editPart) return null;
  const p = partOf(S.editPart); if (!p || !p.select.poly) return null;
  let best = null, bd = 9;
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
const isLeaf = (n) => !children(n).length;
function pickEndHandle(sx, sy) {
  let best = null, bd = 20;
  for (const ik of S.rig.ik || []) {
    if (!footTarget(ik) || !ik.end_bone) continue;
    const [x, y] = toScreen(...ikTargetWorld(ik)), d = Math.hypot(x - sx, y - sy);
    if (d < bd) { bd = d; best = ik.end_bone; }
  }
  for (const b of S.rig.bones) {
    if (!isLeaf(b.name)) continue;
    const e = boneEnd(b.name); if (!e) continue;
    const [x, y] = toScreen(...e.pt), d = Math.hypot(x - sx, y - sy);
    if (d < bd) { bd = d; best = b.name; }
  }
  return best;
}
function pickRigHandle(sx, sy) {
  for (const [n, s] of Object.entries(S.rig.sockets || {})) { const [x, y] = toScreen(...mapPt(world(s.bone), s.pt[0], s.pt[1])); if (Math.hypot(x - sx, y - sy) < 10) return { kind: "socket", id: n }; }
  for (let i = 0; i < (S.rig.ik || []).length; i++) { const t = S.rig.ik[i].target, [x, y] = toScreen(...mapPt(world(t.bone), t.pt[0], t.pt[1])); if (Math.hypot(x - sx, y - sy) < 11) return { kind: "ik", id: i }; }
  const b = pickBone(sx, sy); return b ? { kind: "pivot", id: b } : null;
}
const locked = () => S.cmp.on || S.rest;
function blockedMsg() { toast(S.cmp.on ? "Exit compare mode to edit" : "Turn off 'Rest pose' to edit the working pose"); }

cv.addEventListener("pointerdown", (e) => {
  cv.setPointerCapture(e.pointerId); hideMenu();
  const [sx, sy] = canvasXY(e);
  if (e.button === 1 || e.button === 2 || spaceDown || e.altKey) { if (e.button === 2) return; drag = { type: "pan", sx, sy, px: S.view.px, py: S.view.py }; return; }
  if (e.button !== 0) return;
  S.libFocus = false;
  if (S.cmp.on) { const b = pickBone(sx, sy); if (b) { S.sel = b; refreshPanels(); draw(); } return; }
  if (S.reach && S.tool === "chain") { if (S.rest) { blockedMsg(); return; } startReach(sx, sy); return; }
  const v = pickVertex(sx, sy);
  if (v !== null) { S.selVert = v; beginEdit(); drag = { type: "vertex", i: v }; refreshPanels(); draw(); return; }
  if (S.tool === "pivot") {
    const h = pickRigHandle(sx, sy);
    if (h) {
      if (h.kind === "pivot") S.sel = h.id;
      beginEdit(); drag = { type: h.kind, id: h.id, w0: clone(S.render.world) }; refreshPanels(); draw(); return;
    }
  }
  const hit = (S.tool === "chain" || S.tool === "select") && pickEndHandle(sx, sy) || pickBone(sx, sy);
  if (hit) { S.sel = hit; S.selVert = null; refreshPanels(); draw(); }
  if (!S.sel) { return; }
  if (S.tool === "chain") {
    if (S.rest) { blockedMsg(); return; }
    if (ikDriven(S.sel)) { startFoot(ikOf(S.sel), toRig(sx, sy), false); return; }
    const m = toRig(sx, sy), end = (boneEndRest(S.sel) || { rest: bone(S.sel).pivot }).rest, E0 = mapPt(world(S.sel), end[0], end[1]);
    drag = { type: "chain", bone: S.sel, m0: m, E0, start: clone(S.pose.bones), target: E0 };
    return;
  }
  if (S.tool === "move" || S.tool === "rotate") {
    if (S.rest) { blockedMsg(); return; }
    const b = bone(S.sel), Wp = b.parent ? clone(S.render.world[b.parent]) : [1, 0, 0, 1, 0, 0];
    const P = posedPivot(S.sel), m = toRig(sx, sy);
    drag = { type: S.tool, Wp, P, m0: m, a0: Math.atan2(m[1] - P[1], m[0] - P[0]), rot0: chVal(S.sel, "rot"), tx0: chVal(S.sel, "tx"), ty0: chVal(S.sel, "ty"), moved: false };
    if (S.tool === "rotate" && ikDriven(S.sel)) { toast(`${S.sel} is driven by IK: switch the leg to FK in the IK panel to rotate it`); drag = null; }
  }
});
cv.addEventListener("pointerleave", () => { S.mouse = null; S.hover = null; draw(); });
cv.addEventListener("pointermove", (e) => {
  const [sx, sy] = canvasXY(e);
  S.mouse = [sx, sy];
  if (!drag) {
    const v = pickVertex(sx, sy), eh = !v && v !== 0 && (S.tool === "chain" || S.tool === "select") ? pickEndHandle(sx, sy) : null;
    S.hover = v !== null ? { kind: "vertex", id: v } : eh ? { kind: "bone", id: eh } : (() => { const b = pickBone(sx, sy); return b ? { kind: "bone", id: b } : null; })();
    updateHint(); draw(); return;
  }
  draw();
  const m = toRig(sx, sy);
  if (drag.type === "pan") { S.view.px = drag.px + sx - drag.sx; S.view.py = drag.py + sy - drag.sy; draw(); return; }
  const snap = (v) => (e.shiftKey ? Math.round(v) : r1(v));
  if (drag.type === "vertex") {
    const p = partOf(S.editPart), q = invPt(partTransform(p), m[0], m[1]);
    p.select.poly[drag.i] = [snap(q[0]), snap(q[1])]; S.rigSync = true; render("draft"); refreshValues();
  } else if (drag.type === "pivot") {
    const b = bone(drag.id), Wp = b.parent ? drag.w0[b.parent] : [1, 0, 0, 1, 0, 0], q = invPt(Wp, m[0], m[1]);
    b.pivot = [snap(q[0] - chVal(b.name, "tx")), snap(q[1] - chVal(b.name, "ty"))]; S.rigSync = true; render("draft"); refreshValues();
  } else if (drag.type === "ik") {
    const ik = S.rig.ik[drag.id], q = invPt(drag.w0[ik.target.bone], m[0], m[1]); ik.target.pt = [snap(q[0]), snap(q[1])]; S.rigSync = true; render("draft"); refreshValues();
  } else if (drag.type === "socket") {
    const s = S.rig.sockets[drag.id], q = invPt(drag.w0[s.bone], m[0], m[1]); s.pt = [snap(q[0]), snap(q[1])]; S.rigSync = true; render("draft"); refreshValues();
  } else if (drag.type === "chain") {
    applyChain(m);
  } else if (drag.type === "ikfoot") {
    applyFoot(m);
  } else if (drag.type === "rotate") {
    beginEdit();
    const a = Math.atan2(m[1] - drag.P[1], m[0] - drag.P[0]);
    let d = ((a - drag.a0) * 180) / Math.PI; d = ((d + 540) % 360) - 180;
    setCh(S.sel, "rot", Math.round((drag.rot0 + d) * (e.shiftKey ? 1 : 10)) / (e.shiftKey ? 1 : 10)); render("draft"); refreshValues();
  } else if (drag.type === "move") {
    beginEdit();
    const dw = [m[0] - drag.m0[0], m[1] - drag.m0[1]], i = inv2(drag.Wp);
    setCh(S.sel, "tx", Math.round((drag.tx0 + i[0] * dw[0] + i[2] * dw[1]) * 10) / 10); setCh(S.sel, "ty", Math.round((drag.ty0 + i[1] * dw[0] + i[3] * dw[1]) * 10) / 10);
    render("draft"); refreshValues();
  }
});
cv.addEventListener("pointerup", async () => {
  if (!drag) return;
  const t = drag.type; drag = null;
  if (t === "pan") return;
  if (["vertex", "pivot", "ik", "socket"].includes(t)) {
    try { await api("/api/rig/set", { rig: S.rig }); S.rigSync = false; }
    catch (err) { toast(`Rejected: ${err.message}. Edit reverted.`, true, 6000); const s = editSnap; editSnap = null; if (s) restore(s); return; }
  }
  commitEdit();
});
cv.addEventListener("wheel", (e) => { e.preventDefault(); const [sx, sy] = canvasXY(e); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, sx, sy); }, { passive: false });
cv.addEventListener("dblclick", (e) => {
  const [sx, sy] = canvasXY(e), ed = pickEdge(sx, sy);
  if (ed && pickVertex(sx, sy) === null) addVertexAt(ed.i, ed.t);
});
cv.addEventListener("contextmenu", (e) => {
  e.preventDefault();
  const [sx, sy] = canvasXY(e), items = [], v = pickVertex(sx, sy), ed = pickEdge(sx, sy);
  if (v !== null) { items.push(["Delete vertex " + v, () => deleteVertex(v)]); }
  else if (ed) items.push(["Add vertex on this edge", () => addVertexAt(ed.i, ed.t)]);
  const b = pickBone(sx, sy);
  if (b) {
    S.sel = b; refreshPanels(); draw();
    items.push([`Select parent (${bone(b).parent || "none"})`, () => { const p = bone(b).parent; if (p) { S.sel = p; refreshPanels(); draw(); } }]);
    children(b).forEach((c) => items.push([`Select child ${c.name}`, () => { S.sel = c.name; refreshPanels(); draw(); }]));
    items.push(["Reset this bone's pose", () => resetBone(b)]);
    const ik = ikOf(b); if (ik) items.push([ikOn(ik) ? `Switch ${ik.upper.split("_")[0]} leg to FK` : `Switch ${ik.upper.split("_")[0]} leg to IK`, () => toggleIk(ik)]);
    const part = S.rig.parts.find((p) => p.bone === b);
    if (part) items.push([`Edit polygon of ${part.name}`, () => selectPart(part.name)]);
  }
  if (!items.length) return;
  showMenu(e.clientX, e.clientY, items);
});
function showMenu(x, y, items) {
  const m = $("#menu"); m.replaceChildren(...items.map(([t, f]) => el("div", { onclick: () => { hideMenu(); f(); } }, t)));
  m.style.left = Math.min(x, innerWidth - 200) + "px"; m.style.top = Math.min(y, innerHeight - 30 * items.length - 10) + "px"; m.hidden = false;
}
const hideMenu = () => { $("#menu").hidden = true; };
setInterval(() => { if (S.tool === "chain" || S.tool === "select") draw(); }, 140);
document.addEventListener("pointerdown", (e) => { if (!e.target.closest("#menu")) hideMenu(); });


// ---------------------------------------------------------------- chain drag (FK solver that writes the existing rot / tx / ty / sy channels)
const chainOpt = { follow: 0.6, stretch: true, maxStretch: 1.35 };
const amul = (A, B) => [A[0] * B[0] + A[2] * B[1], A[1] * B[0] + A[3] * B[1], A[0] * B[2] + A[2] * B[3], A[1] * B[2] + A[3] * B[3], A[0] * B[4] + A[2] * B[5] + A[4], A[1] * B[4] + A[3] * B[5] + A[5]];
function fkWorld(name, bones, memo = {}) {
  if (memo[name]) return memo[name];
  const b = bone(name), v = bones[name] || {}, g = (c) => v[c] ?? DEF[c], [px, py] = b.pivot, r = (g("rot") * Math.PI) / 180, c = Math.cos(r), sn = Math.sin(r);
  let L = amul([1, 0, 0, 1, px + g("tx"), py + g("ty")], [c, sn, -sn, c, 0, 0]);
  L = amul(L, [1, 0, -g("shx"), 1, 0, 0]); L = amul(L, [g("sx"), 0, 0, g("sy"), 0, 0]); L = amul(L, [1, 0, 0, 1, -px, -py]);
  return (memo[name] = b.parent ? amul(fkWorld(b.parent, bones, memo), L) : L);
}
const LIMITS = { forearm: [-160, 80], hand: [-70, 70], shin: [0, 150], spine: [-14, 14] };
const limitOf = (n) => { for (const [k, v] of Object.entries(LIMITS)) if (n.endsWith(k)) return v; return [-180, 180]; };
/** Drag the end of `name` to `target` (rig px). Arm-type joints take the rotation; `spine` leans and `hips` shifts by chainOpt.follow. */
function chainSolve(start, name, target) {
  const bones = clone(start), end = (boneEndRest(name) || { rest: bone(name).pivot }).rest;
  const joints = [];
  for (let n = name; n && bone(n).parent; n = bone(n).parent) joints.push(n);
  const arm = joints.filter((n) => n !== "hips" && n !== "spine"), F = chainOpt.follow;
  const E = () => mapPt(fkWorld(name, bones), end[0], end[1]);
  const set = (n, ch, v) => { (bones[n] = bones[n] || {})[ch] = v; };
  const get = (n, ch) => (bones[n] || {})[ch] ?? DEF[ch];
  for (const n of arm) if (n.endsWith("forearm") && Math.abs(get(n, "rot")) < 3) set(n, "rot", -14);   // a dead-straight arm is a CCD dead end: start with a slight bend
  const E0 = E(), dx = target[0] - E0[0], dy = target[1] - E0[1];
  if (F > 0 && joints.includes("hips")) {                         // the body takes a share of the pull first, then the arm covers the rest
    const i = inv2(fkWorld(bone("hips").parent, bones)), bx = F * 0.4 * dx, by = F * 0.25 * dy;
    set("hips", "tx", Math.max(-140, Math.min(140, get("hips", "tx") + i[0] * bx + i[2] * by)));
    set("hips", "ty", Math.max(0, Math.min(90, get("hips", "ty") + i[1] * bx + i[3] * by)));
  }
  if (F > 0 && joints.includes("spine")) set("spine", "rot", Math.max(-14, Math.min(14, get("spine", "rot") + F * 0.06 * dx)));
  for (let it = 0; it < 25; it++) {
    for (const n of [...arm].reverse()) {                          // nearest the body first, so the shoulder takes the big turn
      const w = n === name && arm.length > 1 ? 0.35 : 1;
      const P = mapPt(fkWorld(n, bones), ...bone(n).pivot), e = E();
      const a1 = Math.atan2(e[1] - P[1], e[0] - P[0]), a2 = Math.atan2(target[1] - P[1], target[0] - P[0]);
      let d = ((a2 - a1) * 180) / Math.PI; d = ((d + 540) % 360) - 180;
      const [lo, hi] = limitOf(n); set(n, "rot", Math.max(lo, Math.min(hi, get(n, "rot") + w * d * 0.8)));
    }
    if (chainOpt.stretch && arm.length > 1) {
      const top = arm[arm.length - 1], S0 = mapPt(fkWorld(top, bones), ...bone(top).pivot), e = E();
      const have = Math.hypot(e[0] - S0[0], e[1] - S0[1]), want = Math.hypot(target[0] - S0[0], target[1] - S0[1]), sy = get(top, "sy");
      if (want > have * 1.01) set(top, "sy", Math.min(chainOpt.maxStretch, sy * Math.min(want / have, 1.1)));
      else if (want < have * 0.99 && sy > 1) set(top, "sy", Math.max(1, sy * Math.max(want / have, 0.9)));
    }
    const e = E(); if (Math.hypot(target[0] - e[0], target[1] - e[1]) < 0.5) break;
  }
  const e = E();
  return { bones, residual: Math.hypot(target[0] - e[0], target[1] - e[1]) };
}

// ---------------------------------------------------------------- hints and guide
const TOOL_HELP = {
  get chain() { return S.reach ? "<b>Tay " + (S.reach === "near_hand" ? "gần" : "xa") + " đang bật</b>: kéo hoặc bấm ở <b>bất cứ đâu</b> trên màn hình, bàn tay chạy theo con trỏ và thân đi theo. Muốn chọn khớp thì bấm nút <b>Tắt</b> ở khung Tạo dáng nhanh." : "<b>Grab</b>: bấm giữ vào <b>bàn tay</b> (vòng tròn nhấp nháy) hoặc một khớp rồi kéo. Tay tự duỗi theo, thân nghiêng và dịch theo (chỉnh mức ở ô <b>Chain drag</b>). Thả chuột = chốt."; },
  select: "<b>Select</b>: bấm vào khớp để chọn, rồi chỉnh số ở cột bên phải.",
  rotate: "<b>Rotate</b>: chọn khớp, rồi kéo quanh vòng vàng. Phím mũi tên trái/phải = xoay 1° (giữ Shift = 5°).",
  move: "<b>Move</b>: chọn khớp rồi kéo để trượt. Phím mũi tên = 1 px (giữ Shift = 5 px).",
  pivot: "<b>Pivot</b>: kéo tâm khớp, IK target (hình thoi) hoặc socket (ô vuông). Cái này sửa <b>rig</b>, không phải pose.",
};
function updateHint() {
  const h = $("#hint");
  const sel = S.sel ? ` · đang chọn <b>${S.sel}</b>` : "";
  h.innerHTML = (TOOL_HELP[S.tool] || "") + sel + (S.hover && S.hover.kind === "bone" ? ` · trỏ vào <b>${S.hover.id}</b>` : "") + "<br><small>Cuộn = zoom · Space + kéo = di chuyển khung · F = vừa khung · Ctrl+Z = hoàn tác · H = hướng dẫn</small>";
}
function showGuide() {
  const n = el("div", {}, el("p", {}, "Lion Rig & Pose Studio: tạo dáng cho Lion và lưu thành pose."),
    el("ol", {},
      el("li", {}, "Chọn công cụ ", el("b", {}, "Grab"), ". Bấm giữ vào bàn tay (vòng tròn nhấp nháy) và kéo ra trước: tay duỗi, thân nghiêng và dịch theo. Ô ", el("b", {}, "Chain drag"), " ở bên phải chỉnh mức thân đi theo (0 = thân đứng yên)."),
      el("li", {}, "Muốn chỉnh chính xác: chọn khớp (bấm vào nó hoặc phím Tab), rồi dùng thanh trượt, ô số hoặc các nút -5 -1 +1 +5 ở khung ", el("b", {}, "Bone"), ". Phím mũi tên cũng xoay nhẹ khớp đang chọn."),
      el("li", {}, "Sai thì ", el("b", {}, "Ctrl+Z"), ". Muốn về dáng gốc bấm ", el("b", {}, "Reset pose"), " (dưới cùng)."),
      el("li", {}, "Dáng ưng ý: bấm ", el("b", {}, "+ Save"), " ở khung Pose Library, đặt tên. Bấm đúp vào ảnh nhỏ để mở lại."),
      el("li", {}, "Kiểm tra khớp bị rách: khung ", el("b", {}, "Joint bend tester"), " có nút 0–120° và ảnh xem trước."),
      el("li", {}, "Sửa rig (tâm khớp, vùng cắt, độ mềm khớp): công cụ ", el("b", {}, "Pivot"), " hoặc bấm tên layer ở bên trái. Cái này ghi vào rig, lưu bằng ", el("b", {}, "Save rig"), " (có backup).")),
    el("p", { class: "mut" }, "Bản xem H=60px ở góc phải dưới là cỡ thật trong game. Q W E C P đổi công cụ."));
  return modal({ title: "Hướng dẫn nhanh", node: n, ok: "Đã hiểu", noCancel: true });
}
$("#btnHelp").onclick = showGuide;

function applyChain(m) {
  beginEdit();
  drag.target = [drag.E0[0] + m[0] - drag.m0[0], drag.E0[1] + m[1] - drag.m0[1]];
  const r = chainSolve(drag.start, drag.bone, drag.target);
  S.pose.bones = {};
  for (const [n, v] of Object.entries(r.bones)) for (const [c, x] of Object.entries(v)) if (Math.abs(x - DEF[c]) > 1e-6) (S.pose.bones[n] = S.pose.bones[n] || {})[c] = x;
  drag.residual = r.residual; render("draft"); refreshValues(); draw();
}
const footTarget = (ik) => (ik && ik.target.bone !== "root" ? ik.target.bone : null);
const ikTargetWorld = (ik) => mapPt(world(ik.target.bone), ik.target.pt[0], ik.target.pt[1]);
function startFoot(ik, m, absolute) {
  const tb = footTarget(ik);
  if (!tb) return toast("Rig này chưa có bone đích cho chân. Mở rig_studio_v01.json (ô chọn rig ở thanh trên).", true, 6000);
  const E0 = ikTargetWorld(ik), pb = bone(tb);
  drag = { type: "ikfoot", ik, tb, m0: m, E0, absolute, tx0: chVal(tb, "tx"), ty0: chVal(tb, "ty"), Wp: clone(world(pb.parent)), start: clone(S.pose.bones), target: E0 };
  if (absolute) applyFoot(m);
}
function applyFoot(m) {
  beginEdit();
  const d = drag, ik = d.ik;
  let T = d.absolute ? m : [d.E0[0] + m[0] - d.m0[0], d.E0[1] + m[1] - d.m0[1]];
  const up = bone(ik.upper), low = bone(ik.lower);
  const len = Math.hypot(low.pivot[0] - up.pivot[0], low.pivot[1] - up.pivot[1]) + Math.hypot(ik.end[0] - low.pivot[0], ik.end[1] - low.pivot[1]);
  const base = clone(d.start); base.hips = { ...(base.hips || {}), ty: 0 };                       // hips with no drop: where the leg starts
  const s1 = mapPt(fkWorld(up.parent, base), up.pivot[0], up.pivot[1]), lim = len * 0.985;
  const ox = Math.max(-lim, Math.min(lim, T[0] - s1[0]));
  T = [s1[0] + ox, T[1]];
  const drop = Math.max(0, T[1] - s1[1] - Math.sqrt(lim * lim - ox * ox));                          // a straight leg cannot spread: lower the hips just enough
  const hipsTy0 = (d.start.hips || {}).ty ?? 0;
  if (bone("hips")) setCh("hips", "ty", Math.round(Math.min(90, Math.max(hipsTy0, drop)) * 10) / 10);
  const i = inv2(d.Wp), dx = T[0] - d.E0[0], dy = T[1] - d.E0[1];
  setCh(d.tb, "tx", Math.round((d.tx0 + i[0] * dx + i[2] * dy) * 10) / 10); setCh(d.tb, "ty", Math.round((d.ty0 + i[1] * dx + i[3] * dy) * 10) / 10);
  d.target = T; d.residual = 0; render("draft"); refreshValues(); draw();
}
// Armed hand: the tip follows the pointer from the first press, so nothing has to be aimed at.
function startReach(sx, sy) {
  const m = toRig(sx, sy);
  if (S.reach.endsWith("_foot")) return startFoot((S.rig.ik || []).find((i) => i.end_bone === S.reach), m, true);
  drag = { type: "chain", bone: S.reach, m0: m, E0: m, start: clone(S.pose.bones), target: m };
  applyChain(m);
}
function setReach(n) { S.reach = n; if (n) S.tool = "chain"; refreshPanels(); draw(); }

// ---------------------------------------------------------------- quick pose panel
const PRESETS = [
  ["Nhóm người", { hips: { ty: 70, tx: -15 }, spine: { rot: 18 }, head: { rot: -14 }, tail: { rot: -10 } }],
  ["Cào tới trước (tay gần)", { near_upper_arm: { rot: -78 }, near_forearm: { rot: -12 }, near_hand: { rot: -8 }, spine: { rot: 16 }, hips: { tx: 35 } }],
  ["Cào tới trước (tay xa)", { far_upper_arm: { rot: -78 }, far_forearm: { rot: -12 }, far_hand: { rot: -8 }, spine: { rot: 16 }, hips: { tx: 35 } }],
  ["Đứng rộng chân", { near_foot_target: { tx: -70 }, far_foot_target: { tx: 70 }, hips: { ty: 25 } }],
  ["Hai tay vươn ra trước", { near_upper_arm: { rot: -70 }, near_forearm: { rot: -15 }, far_upper_arm: { rot: -70 }, far_forearm: { rot: -15 }, spine: { rot: 10 } }],
];
function applyPreset(ch) {
  if (locked()) return blockedMsg();
  beginEdit(); for (const [n, v] of Object.entries(ch)) for (const [c, x] of Object.entries(v)) setCh(n, c, x); S.poseId = null; commitEdit();
}
function buildQuick() {
  const b = $("#quickBody"); b.replaceChildren();
  const btn = (label, n) => el("button", { class: S.reach === n ? "on" : "", onclick: () => setReach(S.reach === n ? null : n) }, label);
  b.append(el("div", { class: "mut" }, "Bật một tay rồi kéo hoặc bấm ở BẤT CỨ ĐÂU trên màn hình: bàn tay chạy theo con trỏ, thân đi theo."),
    el("div", { class: "big" }, btn("Tay gần", "near_hand"), btn("Tay xa", "far_hand"), el("button", { class: S.reach ? "" : "on", onclick: () => setReach(null) }, "Tắt")),
    el("div", { class: "big" }, btn("Chân gần", "near_foot"), btn("Chân xa", "far_foot")),
    slider({ label: "Thân đi theo", min: 0, max: 1, step: 0.05, tip: "0 = thân đứng yên, 1 = thân nghiêng và dịch hết cỡ", get: () => chainOpt.follow, set: (v) => { chainOpt.follow = v; }, reset: () => { chainOpt.follow = 0.6; } }));
  b.append(el("div", { class: "presets" }, PRESETS.map(([t, ch]) => el("button", { onclick: () => applyPreset(ch) }, t)), el("button", { onclick: resetPose }, "Về dáng gốc")));
  const sl = (label, n, ch, min, max, sign = 1, tip) => slider({ label, min, max, step: 1, tip, get: () => sign * chVal(n, ch), set: (v) => { if (!locked()) setCh(n, ch, sign * v); }, reset: () => setCh(n, ch, DEF[ch]) });
  b.append(el("h4", {}, "Thân"), sl("Ngồi xuống", "hips", "ty", 0, 100, 1, "hạ hông (px), gối tự gập"), sl("Nghiêng tới trước", "spine", "rot", -15, 35), sl("Cúi/ngẩng đầu", "head", "rot", -40, 40, -1, "dương = ngẩng lên"));
  for (const [side, nm] of [["near", "Tay gần"], ["far", "Tay xa"]]) {
    b.append(el("h4", {}, nm), sl("Giơ ra trước", `${side}_upper_arm`, "rot", -30, 140, -1, "0 = buông thõng, 90 = ngang vai"), sl("Gập khuỷu", `${side}_forearm`, "rot", -20, 150, -1, "0 = duỗi thẳng"), sl("Cổ tay", `${side}_hand`, "rot", -60, 60, -1));
  }
  if (bone("near_foot_target")) for (const [side, nm] of [["near", "Chân gần"], ["far", "Chân xa"]])
    b.append(el("h4", {}, nm), sl("Sang ngang", `${side}_foot_target`, "tx", -200, 200, 1, "âm = ra sau, dương = ra trước"), sl("Nhấc lên", `${side}_foot_target`, "ty", 0, 150, -1), sl("Xoay bàn chân", `${side}_foot`, "rot", -45, 45));
  b.append(el("h4", {}, "Đuôi"), sl("Vẫy đuôi", "tail", "rot", -60, 60));
}

// ---------------------------------------------------------------- pose actions
function nudge(n, ch, d) {
  if (locked()) return blockedMsg();
  if (ikDriven(n) && ch === "rot") return toast(`${n} do IK điều khiển: dùng Grab/Pivot hoặc chuyển chân sang FK`);
  beginEdit(); setCh(n, ch, Math.round((chVal(n, ch) + d) * 100) / 100); commitEdit();
}
function resetBone(n) { if (locked()) return blockedMsg(); beginEdit(); delete S.pose.bones[n]; const ik = (S.rig.ik || []).find((i) => i.upper === n); if (ik) delete S.pose.ik[ik.upper]; commitEdit(); }
function resetPose() { if (locked()) return blockedMsg(); beginEdit(); S.pose = { bones: {}, ik: {} }; S.poseId = null; commitEdit(); }
function toggleIk(ik) { if (locked()) return blockedMsg(); beginEdit(); if (ikOn(ik)) S.pose.ik[ik.upper] = false; else delete S.pose.ik[ik.upper]; commitEdit(); }
function selectPart(n) { S.editPart = S.editPart === n ? null : n; S.selVert = null; refreshPanels(); draw(); }

// ---------------------------------------------------------------- polygon editing
function addVertexAt(i, t) {
  const p = partOf(S.editPart); if (!p) return;
  const a = p.select.poly[i], b = p.select.poly[(i + 1) % p.select.poly.length];
  beginEdit(); p.select.poly.splice(i + 1, 0, [r1(a[0] + (b[0] - a[0]) * t), r1(a[1] + (b[1] - a[1]) * t)]);
  S.selVert = i + 1; S.rigSync = true; applyRigEdit("Vertex added");
}
function deleteVertex(i) {
  const p = partOf(S.editPart); if (!p) return;
  if (p.select.poly.length <= 3) return toast("A polygon needs at least 3 vertices", true);
  beginEdit(); p.select.poly.splice(i, 1); S.selVert = null; S.rigSync = true; applyRigEdit("Vertex deleted");
}
async function applyRigEdit(okMsg) {
  try { await api("/api/rig/set", { rig: S.rig }); S.rigSync = false; commitEdit(); if (okMsg) toast(okMsg); }
  catch (err) { toast(`Rejected: ${err.message}. Edit reverted.`, true, 6000); const s = editSnap; editSnap = null; if (s) restore(s); }
}

// ---------------------------------------------------------------- panels
let binders = [];
function bind(input, get) { binders.push(() => { if (document.activeElement !== input) input.value = fmt(get()); }); input.value = fmt(get()); return input; }
const fmt = (v) => (Number.isInteger(v) ? String(v) : String(Math.round(v * 10) / 10));
function refreshValues() { binders.forEach((f) => f()); updateStatus(); }

function slider({ label, min, max, step, get, set, reset, tip }) {
  const rg = el("input", { type: "range", min, max, step }), nm = el("input", { type: "number", step });
  const sync = () => { rg.value = get(); };
  binders.push(() => { if (document.activeElement !== nm) nm.value = fmt(get()); if (document.activeElement !== rg) sync(); });
  nm.value = fmt(get()); sync();
  rg.addEventListener("input", () => { beginEdit(); set(parseFloat(rg.value)); nm.value = fmt(get()); render("draft"); updateStatus(); });
  rg.addEventListener("change", commitEdit);
  nm.addEventListener("change", () => { const v = parseFloat(nm.value); if (!Number.isFinite(v)) return refreshValues(); beginEdit(); set(v); commitEdit(); });
  const rs = el("button", { class: "rs", title: "Reset", onclick: () => { beginEdit(); reset(); commitEdit(); } }, "↺");
  return el("div", { class: "sl", title: tip || "" }, el("span", {}, label), rg, nm, rs);
}

function refreshPanels() {
  binders = [];
  buildTree(); buildLayers(); buildIk(); buildSockets(); buildBone(); buildRig(); buildJoint(); buildPoly(); buildBend(); buildChain(); buildQuick(); buildLibrary();
  $$("#tools button").forEach((b) => b.classList.toggle("on", b.dataset.tool === S.tool));
  updateStatus(); updateHint();
}
function buildTree() {
  const t = $("#tree"); t.replaceChildren();
  const walk = (n, depth) => {
    const posed = S.pose.bones[n.name];
    t.append(el("div", { class: n.name === S.sel ? "on" : "", style: `padding-left:${6 + depth * 12}px`, onclick: () => { S.sel = n.name; S.libFocus = false; refreshPanels(); draw(); } },
      el("span", { class: "dot", style: `background:${sideColor(n.name)}` }), n.name, posed ? el("span", { class: "tag" }, "posed") : null, ikOf(n.name) ? el("span", { class: "tag" }, "IK") : null));
    children(n.name).forEach((c) => walk(c, depth + 1));
  };
  S.rig.bones.filter((b) => !b.parent).forEach((r) => walk(r, 0));
  $("#left h3 small").textContent = `${S.rig.bones.length} bones`;
}
function buildLayers() {
  const t = $("#layers"); t.replaceChildren();
  for (const p of S.rig.parts) {
    const eye = el("input", { type: "checkbox", title: "Visible", onclick: (e) => { e.stopPropagation(); if (e.target.checked) S.hide.delete(p.name); else S.hide.add(p.name); render("final"); } });
    eye.checked = !S.hide.has(p.name);
    t.append(el("div", { class: S.editPart === p.name ? "on" : "", onclick: () => selectPart(p.name), title: `bone ${p.bone}, source ${p.source}${p.select.poly ? "" : " (no polygon: cut by " + Object.keys(p.select)[0] + ")"}` },
      eye, p.name, el("span", { class: "tag " + (p.skin ? "skin" : "rigid") }, p.skin ? "skin" : "rigid")));
  }
  $("#left section:nth-child(2) h3").innerHTML = `Layers <small>${S.rig.parts.length} · click = edit polygon</small>`;
}
function buildIk() {
  const t = $("#iklist"); t.replaceChildren();
  for (const ik of S.rig.ik || []) {
    const cb = el("input", { type: "checkbox", onchange: () => toggleIk(ik) }); cb.checked = ikOn(ik);
    t.append(el("div", { class: "row" }, el("label", {}, cb, ` ${ik.upper.split("_")[0]} leg IK `), el("small", {}, `${ik.upper} → ${ik.lower} → ${ik.end_bone || "end"}`)),
      el("div", { class: "kv" }, el("span", {}, "target (root)"), el("span", {}, `${fmt(ik.target.pt[0])}, ${fmt(ik.target.pt[1])}`)));
  }
  t.append(el("div", { class: "mut" }, "IK off = FK: the thigh and shin rot channels apply."));
}
function buildSockets() {
  const t = $("#sockets"); t.replaceChildren();
  for (const [n, s] of Object.entries(S.rig.sockets || {})) t.append(el("div", { onclick: () => { S.sel = s.bone; refreshPanels(); draw(); } }, el("span", { class: "dot", style: "background:#7dff7d" }), n, el("small", {}, `${s.bone} ${fmt(s.pt[0])},${fmt(s.pt[1])}`)));
}

function buildBone() {
  const b = $("#boneBody"); b.replaceChildren();
  $("#boneName").textContent = S.sel || "none";
  if (!S.sel) { b.append(el("div", { class: "mut" }, "Click a bone in the viewport or the hierarchy.")); return; }
  const n = S.sel;
  if (ikDriven(n)) b.append(el("div", { class: "err" }, "IK drives this bone: rot/tx/ty/sx/sy/shx are ignored until the leg is set to FK."));
  const lim = { rot: [-180, 180, 0.5], tx: [-300, 300, 1], ty: [-300, 300, 1], sx: [0.3, 2, 0.01], sy: [0.3, 2, 0.01], shx: [-0.6, 0.6, 0.01] };
  const tips = { rot: "degrees, + = clockwise on screen", tx: "px in the parent's frame", ty: "px in the parent's frame", sx: "scale", sy: "scale", shx: "horizontal shear: + leans the top right" };
  for (const ch of CH) b.append(slider({ label: ch, min: lim[ch][0], max: lim[ch][1], step: lim[ch][2], tip: tips[ch], get: () => chVal(n, ch), set: (v) => { if (locked()) return; setCh(n, ch, v); }, reset: () => setCh(n, ch, DEF[ch]) }));
  b.append(el("div", { class: "nudge", title: "Xoay nhẹ khớp đang chọn (độ)" }, [-5, -1, 1, 5].map((d) => el("button", { onclick: () => nudge(n, "rot", d) }, (d > 0 ? "+" : "") + d + "°"))));
  b.append(el("div", { class: "row" }, el("button", { onclick: () => resetBone(n) }, "Reset bone"), el("span", { class: "mut" }, "stored in pose: " + (Object.keys(S.pose.bones[n] || {}).join(", ") || "nothing"))));
}
function link(n) { return el("a", { class: "lnk", onclick: () => { S.sel = n; refreshPanels(); draw(); } }, n); }
function buildRig() {
  const b = $("#rigBody"); b.replaceChildren();
  if (!S.sel) { b.append(el("div", { class: "mut" }, "Select a bone.")); return; }
  const bn = bone(S.sel), sv = S.saved.bones.find((x) => x.name === S.sel);
  const chip = (t) => el("span", { class: "chip " + t }, t);
  b.append(el("div", { class: "kv" }, el("span", {}, "parent", chip("stored")), el("span", {}, bn.parent ? link(bn.parent) : "— (root)")));
  const ch = children(S.sel);
  b.append(el("div", { class: "kv" }, el("span", {}, "children", chip("stored")), el("span", {}, ch.length ? ch.map((c, i) => [i ? ", " : "", link(c.name)]) : "—")));
  const piv = (i) => { const nm = el("input", { type: "number", step: 0.5 }); bind(nm, () => bone(S.sel).pivot[i]); nm.addEventListener("change", () => { const v = parseFloat(nm.value); if (!Number.isFinite(v)) return refreshValues(); beginEdit(); bone(S.sel).pivot[i] = v; S.rigSync = true; applyRigEdit(); }); return nm; };
  b.append(el("div", { class: "kv" }, el("span", {}, "pivot x, y", chip("stored")), el("span", {}, piv(0), " ", piv(1), " ", el("button", { class: "rs", title: "Reset pivot to the saved rig", onclick: () => { beginEdit(); bn.pivot = [...sv.pivot]; S.rigSync = true; applyRigEdit(); } }, "↺"))));
  b.append(el("div", { class: "kv" }, el("span", {}, "saved pivot"), el("span", { class: "mut" }, `${sv.pivot[0]}, ${sv.pivot[1]}${JSON.stringify(sv.pivot) !== JSON.stringify(bn.pivot) ? "  (changed)" : ""}`)));
  const e = boneEndRest(S.sel);
  b.append(el("div", { class: "kv" }, el("span", {}, "length / dir", chip("derived")), el("span", {}, e ? `${Math.round(Math.hypot(e.rest[0] - bn.pivot[0], e.rest[1] - bn.pivot[1]))} px, ${Math.round((Math.atan2(e.rest[1] - bn.pivot[1], e.rest[0] - bn.pivot[0]) * 180) / Math.PI)}° (${e.from})` : "none: the rig stores no length for this bone")));
  const parts = S.rig.parts.filter((p) => p.bone === S.sel || (p.skin && p.skin.bones.includes(S.sel)));
  b.append(el("div", { class: "kv" }, el("span", {}, "layers", chip("stored")), el("span", {}, parts.length ? parts.map((p, i) => [i ? ", " : "", el("a", { class: "lnk", onclick: () => selectPart(p.name) }, p.name + (p.bone === S.sel ? "" : " (joint)"))]) : "—")));
  const ik = ikOf(S.sel); if (ik) b.append(el("div", { class: "kv" }, el("span", {}, "IK"), el("span", {}, `${ik.upper.split("_")[0]} leg, ${ikOn(ik) ? "IK on" : "FK"}`)));
  const so = Object.entries(S.rig.sockets || {}).filter(([, s]) => s.bone === S.sel); if (so.length) b.append(el("div", { class: "kv" }, el("span", {}, "sockets"), el("span", {}, so.map(([k]) => k).join(", "))));
  b.append(el("div", { class: "mut" }, "Pivot tool (P) drags pivots, IK targets and sockets: these edit the rig, not the pose."));
}

function buildJoint() {
  const b = $("#jointBody"); b.replaceChildren();
  const skins = S.rig.parts.filter((p) => p.skin);
  const rel = (p) => S.sel && p.skin.bones.includes(S.sel);
  for (const p of skins.sort((a, c) => rel(c) - rel(a))) {
    const sv = S.saved.parts.find((q) => q.name === p.name);
    b.append(el("div", { style: "margin-top:6px;font-weight:600" }, p.name, el("small", {}, ` bones ${p.skin.bones.join(" › ")}`)));
    for (const j of skinJoints(p)) {
      const svBl = sv ? (Array.isArray(sv.skin.blend) ? sv.skin.blend[j.idx] : sv.skin.blend) : null;
      const setBl = (v) => { const sk = partOf(p.name).skin; v = Math.max(1, v); if (!Array.isArray(sk.blend)) sk.blend = skinJoints(partOf(p.name)).map(() => sk.blend); sk.blend[j.idx] = v; S.rigSync = true; };
      const row = slider({ label: j.bone.replace(/^(near|far)_/, "$1 "), min: 1, max: 120, step: 1, tip: `joint ${j.bone}: the pixels turn over a band of 2 × blend px centred on the pivot (saved ${svBl})`, get: () => skinJoints(partOf(p.name))[j.idx].blend, set: setBl, reset: () => setBl(svBl) });
      if (j.bone === S.sel) row.style.background = "var(--accbg)";
      b.append(row);
      if (svBl !== skinJoints(partOf(p.name))[j.idx].blend) b.append(el("div", { class: "mut" }, `  before: ${svBl} → after: ${skinJoints(partOf(p.name))[j.idx].blend}`));
    }
    const tipRow = el("div", { class: "kv" }, el("span", {}, "tip x, y"));
    const tipIn = (i) => { const nm = el("input", { type: "number", step: 1 }); bind(nm, () => partOf(p.name).skin.tip[i]); nm.addEventListener("change", () => { const v = parseFloat(nm.value); if (!Number.isFinite(v)) return refreshValues(); beginEdit(); partOf(p.name).skin.tip[i] = v; S.rigSync = true; applyRigEdit(); }); return nm; };
    tipRow.append(el("span", {}, tipIn(0), " ", tipIn(1), el("small", {}, " axis of the last joint"))); b.append(tipRow);
  }
  b.append(el("div", { class: "row" }, el("button", { onclick: () => { beginEdit(); S.rig.parts.forEach((p) => { const s = S.saved.parts.find((q) => q.name === p.name); if (p.skin && s) p.skin = clone(s.skin); }); S.rigSync = true; applyRigEdit("Blend values reset to the saved rig"); } }, "Reset all blends"), el("small", {}, "Blend is a band width, not a skin weight.")));
}

function buildPoly() {
  const b = $("#polyBody"); b.replaceChildren();
  const p = S.editPart && partOf(S.editPart);
  $("#polyName").textContent = p ? p.name : "no layer";
  if (!p) { b.append(el("div", { class: "mut" }, "Click a layer in the Layers list to edit its cut polygon.")); return; }
  if (!p.select.poly) { b.append(el("div", { class: "mut" }, "This layer is not cut by a polygon.")); return; }
  const sv = S.saved.parts.find((q) => q.name === p.name);
  b.append(el("div", { class: "mut" }, `${p.select.poly.length} vertices · drag in the viewport · double-click an edge adds, Del removes the selected vertex. Invalid polygons are refused.`));
  const list = el("div", { class: "list", style: "max-height:170px" });
  p.select.poly.forEach((q, i) => {
    const num = (k) => { const nm = el("input", { type: "number", step: 1, style: "width:58px" }); bind(nm, () => partOf(p.name).select.poly[i][k]); nm.addEventListener("change", () => { const v = parseFloat(nm.value); if (!Number.isFinite(v)) return refreshValues(); beginEdit(); partOf(p.name).select.poly[i][k] = v; S.rigSync = true; applyRigEdit(); }); return nm; };
    list.append(el("div", { class: i === S.selVert ? "on" : "", onclick: (e) => { if (e.target.tagName !== "INPUT") { S.selVert = i; refreshPanels(); draw(); } } }, el("span", { style: "width:18px" }, i), num(0), num(1)));
  });
  b.append(list, el("div", { class: "row" },
    el("button", { onclick: () => { const i = S.selVert ?? p.select.poly.length - 1; addVertexAt(i, 0.5); } }, "Add vertex"),
    el("button", { onclick: () => S.selVert !== null && deleteVertex(S.selVert), disabled: S.selVert === null ? "" : null }, "Delete vertex"),
    el("button", { onclick: () => { beginEdit(); p.select.poly = clone(sv.select.poly); S.rigSync = true; applyRigEdit("Polygon reset to the saved rig"); } }, "Reset polygon")));
}

function buildChain() {
  const b = $("#chainBody"); b.replaceChildren();
  const dflt = { follow: 0.6, maxStretch: 1.35 };
  const mk = (label, key, min, max, step, tip) => slider({ label, min, max, step, tip, get: () => chainOpt[key], set: (v) => { chainOpt[key] = v; }, reset: () => { chainOpt[key] = dflt[key]; } });
  const cb = el("input", { type: "checkbox", onchange: () => { chainOpt.stretch = cb.checked; } }); cb.checked = chainOpt.stretch;
  b.append(el("div", { class: "mut" }, "Chain tool (C): drag a bone end such as the hand. Its parents turn to follow; the body leans and shifts by the amount below. Writes only rot, tx, ty, sy."),
    mk("body", "follow", 0, 1, 0.05, "0 = body stays put, 1 = spine leans and hips shift fully to help"), mk("max x", "maxStretch", 1, 1.6, 0.05, "longest the top limb bone may stretch (sy)"),
    el("div", { class: "row" }, el("label", {}, cb, " Stretch the limb when out of reach")));
}

// ---------------------------------------------------------------- joint bend tester
const JOINTS = [
  { id: "near_elbow", label: "Elbow (near)", bone: "near_forearm", flex: -1 }, { id: "far_elbow", label: "Elbow (far)", bone: "far_forearm", flex: -1 },
  { id: "near_knee", label: "Knee (near)", bone: "near_shin", flex: 1, fk: "near_thigh" }, { id: "far_knee", label: "Knee (far)", bone: "far_shin", flex: 1, fk: "far_thigh" },
  { id: "near_shoulder", label: "Shoulder (near)", bone: "near_upper_arm", flex: -1 }, { id: "far_shoulder", label: "Shoulder (far)", bone: "far_upper_arm", flex: -1 },
  { id: "near_hip", label: "Hip (near)", bone: "near_thigh", flex: -1, fk: "near_thigh" }, { id: "far_hip", label: "Hip (far)", bone: "far_thigh", flex: -1, fk: "far_thigh" },
  { id: "neck", label: "Neck / head", bone: "head", flex: -1 }, { id: "waist", label: "Waist (spine)", bone: "spine", flex: -1 },
  { id: "tail", label: "Tail", bone: "tail", flex: 1 }, { id: "near_foot", label: "Foot (near)", bone: "near_foot", flex: 1 }, { id: "far_foot", label: "Foot (far)", bone: "far_foot", flex: 1 },
];
const KNOWN = [
  ["Knee tears: hips down 30 px", { "hips.ty": 30 }], ["Elbow breaks near -135°", { "near_forearm.rot": -135 }], ["Shoulder cut flat near 80°", { "near_upper_arm.rot": 80 }],
  ["Neck gap near -28°", { "head.rot": -28 }], ["Tail does not bend", { "tail.rot": 45 }], ["Feet are rigid", { "near_foot.rot": 35, "far_foot.rot": 35 }],
];
const bend = { joint: "near_elbow", dir: 1, angle: 0 };
function bendJoint() { return JOINTS.find((j) => j.id === bend.joint && bone(j.bone)) || JOINTS.find((j) => bone(j.bone)); }
function applyBend(angle) {
  if (locked()) return blockedMsg();
  const j = bendJoint(); beginEdit();
  if (j.fk && ikOf(j.bone)) S.pose.ik[ikOf(j.bone).upper] = false;
  setCh(j.bone, "rot", angle * j.flex * bend.dir); S.sel = j.bone; bend.angle = angle; commitEdit();
}
function buildBend() {
  const b = $("#bendBody"); b.replaceChildren();
  const j = bendJoint();
  const sel = el("select", { onchange: () => { bend.joint = sel.value; buildBend(); } }, JOINTS.filter((x) => bone(x.bone)).map((x) => el("option", { value: x.id }, x.label)));
  sel.value = j.id;
  const cur = Math.abs(chVal(j.bone, "rot")), signed = chVal(j.bone, "rot") * j.flex * bend.dir;
  b.append(el("div", { class: "row" }, sel, el("button", { onclick: () => { bend.dir *= -1; buildBend(); }, title: "Bend the other way" }, bend.dir > 0 ? "flex ↔ extend" : "extend ↔ flex")));
  b.append(el("div", { class: "angles" }, [0, 30, 45, 60, 90, 120].map((a) => el("button", { class: Math.abs(signed - a) < 0.5 ? "on" : "", onclick: () => applyBend(a) }, a + "°"))));
  b.append(slider({ label: "angle", min: -150, max: 150, step: 1, get: () => chVal(j.bone, "rot") * j.flex * bend.dir, set: (v) => { if (locked()) return; if (j.fk && ikOf(j.bone)) S.pose.ik[ikOf(j.bone).upper] = false; setCh(j.bone, "rot", v * j.flex * bend.dir); }, reset: () => setCh(j.bone, "rot", 0) }));
  b.append(el("div", { class: "mut" }, `drives ${j.bone}.rot${j.fk ? " (leg switched to FK: IK would hide the bend)" : ""}`));
  const rel = S.rig.parts.filter((p) => p.skin && p.skin.bones.includes(j.bone));
  b.append(el("div", { class: "kv" }, el("span", {}, "blend"), el("span", {}, rel.length ? rel.map((p) => `${p.name}: ${skinJoints(p).filter((x) => x.bone === j.bone).map((x) => x.blend).join("")}`).join(" · ") : "rigid layer: no blend, no bend")));
  b.append(el("div", { class: "row" }, el("button", { onclick: () => stripRender(j) }, "Preview 0 · 30 · 45 · 60 · 90 · 120°"), el("span", { id: "stripInfo", class: "mut" })));
  b.append(el("div", { id: "strip" }));
  b.append(el("div", { style: "margin-top:8px;font-weight:600" }, "Known issues: load a test pose"));
  for (const [t, ch] of KNOWN) b.append(el("div", { class: "row" }, el("button", { onclick: () => loadTest(ch) }, "Load"), el("span", {}, t)));
}
function loadTest(ch) {
  if (locked()) return blockedMsg();
  beginEdit(); S.pose = { bones: {}, ik: {} };
  for (const [k, v] of Object.entries(ch)) { const [n, c] = k.split("."); setCh(n, c, v); }
  S.poseId = null; commitEdit();
}
async function stripRender(j) {
  const box = $("#strip"), info = $("#stripInfo"); box.replaceChildren(); info.textContent = "rendering…";
  try {
    if (S.rigSync) { await api("/api/rig/set", { rig: S.rig }); S.rigSync = false; }
    const piv = bone(j.bone).pivot, region = [piv[0] - 230, piv[1] - 150, 460, 460], t0 = performance.now();
    for (const a of [0, 30, 45, 60, 90, 120]) {
      const pose = clone(displayPose().bones ? displayPose() : { bones: {}, ik: {} }); pose.bones = pose.bones || {}; pose.ik = pose.ik || {};
      if (j.fk && ikOf(j.bone)) pose.ik[ikOf(j.bone).upper] = false;
      pose.bones[j.bone] = { ...(pose.bones[j.bone] || {}), rot: a * j.flex * bend.dir };
      const r = await api("/api/render", { scale: 0.5, region, layers: [{ src: "working", pose, hide: [...S.hide], primary: true }] });
      box.append(el("div", {}, el("img", { src: "data:image/png;base64," + r.png }), `${a}° · ${r.ms} ms`));
    }
    info.textContent = `${Math.round(performance.now() - t0)} ms total`;
  } catch (e) { info.textContent = e.message; info.className = "err"; }
}

// ---------------------------------------------------------------- rig save / open
async function saveRig(mode) {
  if (S.bad) return toast("Fix the invalid edit first: " + S.bad, true);
  if (!rigDirty() && mode === "overwrite") return toast("No rig changes to save");
  const msg = mode === "overwrite" ? `Overwrite ${S.rigFile}? A backup copy goes to source/rig/backup/ first.` : "Write the rig as a new file rig_studio_vNN.json (the original stays untouched)?";
  const ok = await modal({ title: mode === "overwrite" ? "Save rig" : "Save as new version", text: msg, ok: "Save" });
  if (!ok) return;
  try {
    await api("/api/rig/set", { rig: S.rig });
    const r = await api("/api/rig/save", { rig: S.rig, mode });
    S.saved = clone(S.rig); S.rigFile = r.file; await loadState(false);
    toast(`Saved ${r.file}${r.backup ? " · backup " + r.backup : ""}`);
  } catch (e) { toast(e.message, true, 6000); }
}
async function openRig(name, force) {
  if (!force && rigDirty() && !(await modal({ title: "Unsaved rig changes", text: "Discard the unsaved rig edits and load from disk?", ok: "Discard" }))) { $("#rigFile").value = S.rigFile; return; }
  try {
    const r = await api("/api/open?file=" + encodeURIComponent(name));
    S.rig = r.rig; S.saved = clone(r.rig); S.parts = r.parts; S.rigFile = r.rig_file; S.topology = r.topology; S.rigSync = false; S.undo = []; S.redo = []; S.editPart = null; S.selVert = null;
    buildRigSelect(); refreshPanels(); render("final"); toast(`Loaded ${name}`);
  } catch (e) { toast(e.message, true); }
}
function buildRigSelect() { const s = $("#rigFile"); s.replaceChildren(...S.rigFiles.map((f) => el("option", { value: f }, f))); s.value = S.rigFile; }

// ---------------------------------------------------------------- pose library
const labelOf = (ref) => (ref === "working" ? "Working pose" : ref === "rest" ? "Rest pose" : (S.poses.find((p) => p.id === ref) || {}).name || ref);
function buildLibrary() {
  const c = $("#cards"); c.replaceChildren();
  if (!S.poses.length) c.append(el("div", { class: "mut" }, "No poses yet. Pose the Lion, then press + Save."));
  for (const p of S.poses) {
    const stale = p.rig && p.rig.topology !== S.topology;
    c.append(el("div", { class: "card" + (S.libSel === p.id ? " on" : ""), title: `${p.name}\n${p.description || ""}\nid ${p.id}\ncreated ${p.created}\nupdated ${p.updated}${stale ? "\n⚠ saved against a different rig structure" : ""}`,
      onclick: () => { S.libSel = p.id; S.libFocus = true; buildLibrary(); }, ondblclick: () => loadPose(p.id) },
      el("img", { src: `/poses/${p.id}.png?t=${encodeURIComponent(p.updated)}`, alt: p.name }), el("div", { class: "n" }, p.name + (S.poseId === p.id ? (poseDirty() ? " ●" : " ✓") : "")), el("div", { class: "m" }, p.id + (stale ? " ⚠" : "")), el("div", { class: "m" }, p.updated.replace("T", " ").slice(0, 16))));
  }
  for (const id of ["cmpA", "cmpB"]) {
    const s = $("#" + id), v = S.cmp[id === "cmpA" ? "a" : "b"];
    s.replaceChildren(el("option", { value: "working" }, "Working pose"), el("option", { value: "rest" }, "Rest pose"), ...S.poses.map((p) => el("option", { value: p.id }, p.name))); s.value = v;
  }
  const has = !!S.libSel && S.poses.some((p) => p.id === S.libSel);
  ["pLoad", "pUpdate", "pDup", "pRename", "pDelete", "pExport"].forEach((i) => ($("#" + i).disabled = !has));
}
async function reloadPoses() { S.poses = (await api("/api/state")).poses; if (S.libSel && !S.poses.some((p) => p.id === S.libSel)) S.libSel = null; buildLibrary(); }
function loadPose(id) {
  const p = S.poses.find((q) => q.id === id); if (!p) return;
  if (S.cmp.on) exitCompare();
  beginEdit(); S.pose = { bones: clone(p.bones || {}), ik: clone(p.ik || {}) }; S.poseId = id; S.poseBase = cleanPose(); S.rest = false; $("#optRest").checked = false;
  const miss = Object.keys(p.bones || {}).filter((n) => !bone(n)); commitEdit();
  if (miss.length) toast(`Pose has bones missing from this rig (ignored by the renderer): ${miss.join(", ")}`, true, 6000);
  if (p.rig && p.rig.topology !== S.topology) toast("This pose was saved against a different rig structure", true, 6000);
}
async function poseOp(body, msg) { try { const r = await api("/api/pose", body); await reloadPoses(); if (msg) toast(msg); return r; } catch (e) { toast(e.message, true, 6000); } }
$("#pNew").onclick = async () => {
  const f = await modal({ title: "Save new pose", fields: [{ label: "Name", value: "" }, { label: "Description", value: "", area: true }], ok: "Save" });
  if (!f || !f[0].trim()) return;
  const r = await poseOp({ op: "save", name: f[0], description: f[1], pose: { bones: S.pose.bones, ik: S.pose.ik } }, `Saved pose "${f[0]}"`);
  if (r) { S.libSel = r.id; S.poseId = r.id; S.poseBase = cleanPose(); buildLibrary(); updateStatus(); }
};
$("#pLoad").onclick = () => loadPose(S.libSel);
$("#pUpdate").onclick = async () => {
  const p = S.poses.find((q) => q.id === S.libSel);
  if (!(await modal({ title: "Update pose", text: `Overwrite "${p.name}" with the working pose?`, ok: "Update" }))) return;
  if (await poseOp({ op: "update", id: S.libSel, pose: { bones: S.pose.bones, ik: S.pose.ik } }, "Pose updated")) { S.poseId = S.libSel; S.poseBase = cleanPose(); buildLibrary(); updateStatus(); }
};
$("#pDup").onclick = async () => { const r = await poseOp({ op: "duplicate", id: S.libSel }, "Pose duplicated"); if (r) { S.libSel = r.id; buildLibrary(); } };
$("#pRename").onclick = async () => {
  const p = S.poses.find((q) => q.id === S.libSel);
  const f = await modal({ title: "Rename pose", fields: [{ label: "Name", value: p.name }, { label: "Description", value: p.description || "", area: true }], ok: "Rename" });
  if (f && f[0].trim()) poseOp({ op: "rename", id: p.id, name: f[0], description: f[1] }, "Pose renamed");
};
async function deletePose() {
  const p = S.poses.find((q) => q.id === S.libSel); if (!p) return;
  if (!(await modal({ title: "Delete pose", text: `Delete "${p.name}"? The files are moved to poses/.trash/.`, ok: "Delete" }))) return;
  if (await poseOp({ op: "delete", id: p.id }, "Pose deleted")) { if (S.poseId === p.id) S.poseId = null; S.libSel = null; buildLibrary(); updateStatus(); }
}
$("#pDelete").onclick = deletePose;
$("#pExport").onclick = () => { const a = el("a", { href: `/poses/${S.libSel}.json`, download: `${S.libSel}.json` }); document.body.append(a); a.click(); a.remove(); };
$("#pImport").onclick = () => $("#pFile").click();
$("#pFile").onchange = async (e) => {
  const f = e.target.files[0]; e.target.value = ""; if (!f) return;
  try {
    const d = JSON.parse(await f.text());
    if (typeof d.bones !== "object" || d.bones === null) throw new Error("Not a pose file: no bones object");
    const r = await poseOp({ op: "import", name: d.name || f.name.replace(/\.json$/, ""), description: d.description || "", pose: d }, "Pose imported");
    if (r) { S.libSel = r.id; buildLibrary(); }
  } catch (err) { toast(err.message, true); }
};
$("#pResetAll").onclick = resetPose;
function exitCompare() { S.cmp.on = false; render("final"); draw(); }
$("#cmpA").onchange = (e) => { S.cmp.a = e.target.value; S.cmp.on = true; S.cmp.showing = "a"; render("final"); };
$("#cmpB").onchange = (e) => { S.cmp.b = e.target.value; S.cmp.on = true; S.cmp.showing = "b"; render("final"); };
$("#cmpFlip").onclick = () => { S.cmp.showing = S.cmp.on && S.cmp.showing === "a" ? "b" : "a"; S.cmp.on = true; render("final"); };
$("#cmpOnion").checked = true; $("#cmpOnion").onchange = (e) => { S.cmp.onion = e.target.checked; render("final"); };
$("#cmpOff").onclick = exitCompare;

// ---------------------------------------------------------------- toolbar, keys, panels
$$("#tools button").forEach((b) => (b.onclick = () => { S.tool = b.dataset.tool; if (S.tool !== "chain") S.reach = null; refreshPanels(); draw(); }));
$("#btnUndo").onclick = undo; $("#btnRedo").onclick = redo;
$("#btnSave").onclick = () => saveRig("overwrite"); $("#btnSaveNew").onclick = () => saveRig("new");
$("#btnReload").onclick = () => openRig(S.rigFile);
$("#rigFile").onchange = (e) => openRig(e.target.value);
$("#optRest").onchange = (e) => { S.rest = e.target.checked; render("final"); };
$("#optQuality").onchange = () => render("final");
$("#btnZoomIn").onclick = () => { const r = cv.getBoundingClientRect(); zoomAt(1.25, r.width / 2, r.height / 2); };
$("#btnZoomOut").onclick = () => { const r = cv.getBoundingClientRect(); zoomAt(0.8, r.width / 2, r.height / 2); };
$("#btnFit").onclick = () => fit(); $("#btnReset").onclick = () => { S.view.zoom = 0.6; fit(); };
$("#btnActual1").onclick = () => { S.gameH = 60; actualSize(60); render("final"); };
$("#btnActual2").onclick = () => { S.gameH = 120; actualSize(120); render("final"); };
$("#optBg").onchange = (e) => { S.bg = e.target.value; draw(); };
$("#optGrid").onchange = (e) => { S.grid = e.target.checked; draw(); };
$("#optChar").onchange = (e) => { S.showChar = e.target.checked; draw(); };
$("#optGhostRig").onchange = (e) => { S.ghostRig = e.target.checked; render("final"); };
$$("[data-vis]").forEach((c) => (c.onchange = () => { S.vis[c.dataset.vis] = c.checked; draw(); }));

document.addEventListener("keydown", (e) => {
  const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) && document.activeElement.type !== "range" && document.activeElement.type !== "checkbox";
  const mod = e.ctrlKey || e.metaKey, k = e.key.toLowerCase();
  if (e.code === "Space" && !typing) { spaceDown = true; e.preventDefault(); }
  if (!$("#modal").hidden) return;
  if (mod && k === "s") { e.preventDefault(); saveRig("overwrite"); return; }
  if (typing) return;
  if (mod && k === "z") { e.preventDefault(); e.shiftKey ? redo() : undo(); return; }
  if (mod && k === "y") { e.preventDefault(); redo(); return; }
  if (mod) return;
  if (k === "q") S.tool = "select"; else if (k === "w") S.tool = "move"; else if (k === "e") S.tool = "rotate"; else if (k === "p") S.tool = "pivot"; else if (k === "c") S.tool = "chain";
  else if (k === "f") fit();
  else if (k === "h") { showGuide(); return; }
  else if (e.key === "Tab") {
    e.preventDefault(); const names = S.rig.bones.map((b) => b.name), i = names.indexOf(S.sel);
    S.sel = names[(i + (e.shiftKey ? -1 : 1) + names.length) % names.length];
  } else if (e.key.startsWith("Arrow") && S.sel) {
    e.preventDefault(); const st = e.shiftKey ? 5 : 1;
    if (S.tool === "move") { if (e.key === "ArrowLeft") nudge(S.sel, "tx", -st); else if (e.key === "ArrowRight") nudge(S.sel, "tx", st); else if (e.key === "ArrowUp") nudge(S.sel, "ty", -st); else nudge(S.sel, "ty", st); }
    else if (e.key === "ArrowLeft") nudge(S.sel, "rot", -st); else if (e.key === "ArrowRight") nudge(S.sel, "rot", st);
    return;
  }
  else if (e.key === "Delete" || e.key === "Backspace") {
    if (S.editPart && S.selVert !== null) deleteVertex(S.selVert);
    else if (S.libFocus && S.libSel) deletePose();
    else if (S.sel) resetBone(S.sel);
  } else return;
  refreshPanels(); draw();
});
document.addEventListener("keyup", (e) => { if (e.code === "Space") spaceDown = false; });
window.addEventListener("beforeunload", (e) => { if (rigDirty() || poseDirty()) { e.preventDefault(); e.returnValue = ""; } });
window.addEventListener("resize", resize);

function splitter(id, axis, target, min, max, invert) {
  const s = $(id); let st = null;
  s.addEventListener("pointerdown", (e) => { s.setPointerCapture(e.pointerId); st = { x: e.clientX, y: e.clientY, w: target().getBoundingClientRect().width, h: target().getBoundingClientRect().height }; });
  s.addEventListener("pointermove", (e) => {
    if (!st) return;
    const d = axis === "x" ? e.clientX - st.x : e.clientY - st.y, v = Math.max(min, Math.min(max, (axis === "x" ? st.w : st.h) + (invert ? -d : d)));
    target().style[axis === "x" ? "width" : "height"] = v + "px"; resize();
  });
  s.addEventListener("pointerup", () => (st = null));
}
splitter("#splitL", "x", () => $("#left"), 160, 500, false);
splitter("#splitR", "x", () => $("#right"), 220, 640, true);
splitter("#splitB", "y", () => $("#library"), 80, 500, true);

// ---------------------------------------------------------------- boot
async function loadState(first) {
  const st = await api("/api/state");
  S.rig = st.rig; S.saved = clone(st.rig); S.parts = st.parts; S.rigFile = st.rig_file; S.rigFiles = st.rig_files; S.topology = st.topology; S.poses = st.poses;
  S.rigSync = false; S.undo = []; S.redo = [];
  buildRigSelect();
  if (first) {
    S.sel = "near_forearm";
    const a = st.autosave;
    if (a && a.rig_file === st.rig_file && (JSON.stringify(a.rig) !== JSON.stringify(st.rig) || Object.keys((a.pose || {}).bones || {}).length)) {
      const yes = await modal({ title: "Restore autosave?", text: `An unsaved working state from ${a.time.replace("T", " ").slice(0, 19)} was found (rig edits: ${a.rig_dirty ? "yes" : "no"}, posed bones: ${Object.keys(a.pose.bones || {}).length}).`, ok: "Restore" });
      if (yes) { S.rig = a.rig; S.pose = { bones: a.pose.bones || {}, ik: a.pose.ik || {} }; S.rigSync = true; } else api("/api/autosave/clear", {});
    }
  }
  refreshPanels();
}
(async () => {
  resize();
  try {
    await loadState(true); fit(); render("final");
    let seen = false; try { seen = localStorage.getItem("studioGuideSeen") === "1"; localStorage.setItem("studioGuideSeen", "1"); } catch (e) { /* storage blocked: show the guide each time */ }
    if (!seen) showGuide();
  }
  catch (e) { toast("Cannot reach the Studio server: " + e.message, true, 20000); }
})();
