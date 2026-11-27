// Frame Tuner: sprite prep page. Every step runs in scripts/sprite_prep/ through serve.py; this page only shows and sends.
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v; else if (k === 'style') e.style.cssText = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else if (v !== undefined && v !== null && v !== false) e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of kids.flat()) if (c !== null && c !== undefined && c !== false) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
};
const qs = o => Object.entries(o).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
async function api(path, params = {}) { const r = await fetch(`/api/prep/${path}?${qs(params)}`); const j = await r.json(); if (!r.ok) throw new Error(j.error || r.status); return j; }
async function post(path, body) { const r = await fetch(`/api/prep/${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); const j = await r.json(); if (!r.ok || j.ok === false) throw new Error(j.error || r.status); return j; }
const loadImg = src => new Promise((ok, bad) => { const i = new Image(); i.onload = () => ok(i); i.onerror = bad; i.src = src; });
const clone = o => JSON.parse(JSON.stringify(o));
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
function toast(msg, cls = '') { const j = $('#jobs'); j.textContent = msg; j.className = 'jobs ' + cls; }

const ACT_LABEL = { attack: 'Đánh', death: 'Chết', run: 'Chạy', skill1: 'Skill 1', skill2: 'Skill 2', skill3: 'Skill 3' };
const FLAG_LABEL = { edge: 'chạm mép', pink: 'còn hồng', spike: 'diện tích vọt (vệt chém, hiệu ứng)', pieces: 'nhiều mảnh rời', empty: 'trống' };
const S = {
  ws: null, sum: null, hero: null, action: null, tab: 'takes',
  ver: {}, infos: {}, strips: {},
  clean: { clip: null, f: 0, edits: null, flags: [], tool: 'brush', r: 6, onion: false, raw: false, hist: {}, redo: {} },
  seq: null, seqCur: { seg: 0, k: 0 },
  view: { scale: 'game2', bg: 'checker', flip: false, onion: false, playing: false, i: 0, speed: 1 },
  takes: { playing: true, i: 0, speed: 1 },
};
const key = (h, c) => `${h}|${c}`;
const ver = (h, c) => S.ver[key(h, c)] || 0;
const bump = (h, c) => { S.ver[key(h, c)] = ver(h, c) + 1; delete S.strips[`${key(h, c)}|80`]; delete S.strips[`${key(h, c)}|200`]; };
const frameUrl = (h, c, f, raw = false) => `/api/prep/frame?${qs({ ws: S.ws, clip: c, hero: h, f, raw: raw ? 1 : 0, v: ver(h, c) })}`;
async function info(h, c) { const k = key(h, c); if (!S.infos[k]) S.infos[k] = await api('info', { ws: S.ws, clip: c, hero: h }); return S.infos[k]; }
async function strip(h, c, height) {
  const k = `${key(h, c)}|${height}`;
  if (!S.strips[k]) S.strips[k] = (async () => { const meta = await api('stripmeta', { ws: S.ws, clip: c, hero: h, h: height }); const img = await loadImg(`/api/prep/strip?${qs({ ws: S.ws, clip: c, hero: h, h: height, v: ver(h, c) })}`); return { img, ...meta }; })();
  return S.strips[k];
}
const act = () => S.sum.actions[S.hero][S.action];
const board = () => S.sum.board[S.hero][S.action];
const splitTakes = () => act().takes.filter(c => board().split.includes(c));

// ---------------------------------------------------------------------------------------------------------- jobs
let lastDone = new Set();
async function pollJobs() {
  try {
    const js = await api('jobs');
    const run = js.filter(j => j.status === 'running' || j.status === 'queued');
    const err = js.filter(j => j.status === 'error' && !lastDone.has(j.id));
    const done = js.filter(j => j.status === 'done' && !lastDone.has(j.id));
    if (run.length) { const r = run.find(j => j.status === 'running') || run[0]; toast(`${r.title}: ${Math.round(r.progress * 100)}% ${r.text}${run.length > 1 ? `  (+${run.length - 1} việc chờ)` : ''}`, 'warn'); }
    else if (err.length) { toast(`Lỗi: ${err[0].title}: ${err[0].error}`, 'bad'); }
    else if (done.length) toast(`Xong: ${done.map(j => j.title).join(', ')}`, 'ok');
    for (const j of js) if (j.status === 'done' || j.status === 'error') {
      if (!lastDone.has(j.id)) {
        lastDone.add(j.id);
        if (j.kind === 'split' || j.kind === 'export') { S.infos = {}; S.strips = {}; await refreshSummary(); renderTab(); }
        if (j.kind === 'export' && j.result) exportLog(Object.entries(j.result).map(([a, o]) => `${a}: ${o}`).join('\n'));
        if (j.kind === 'export' && j.error) exportLog('LỖI: ' + j.error);
        if (j.kind === 'legacy' && j.status === 'done') location.href = '/legacy.html';
      }
    }
  } catch (e) { /* server restarting */ }
  setTimeout(pollJobs, 1000);
}

// ---------------------------------------------------------------------------------------------------------- workspace and board
async function init() {
  const list = await api('workspaces');
  const sel = $('#wsSel');
  for (const w of list) sel.append(el('option', { value: w.id }, `${w.title}`));
  const saved = localStorageGet('ft.ws');
  if (saved && list.some(w => w.id === saved)) sel.value = saved;
  sel.onchange = () => openWs(sel.value);
  if (list.length) await openWs(sel.value);
  for (const b of document.querySelectorAll('#tabs button')) b.onclick = () => setTab(b.dataset.tab);
  $('#splitAll').onclick = async () => {
    const todo = Object.keys(S.sum.clips).filter(c => S.sum.heroes && Object.keys(S.sum.heroes).some(h => (S.sum.clips[c].heroes || Object.keys(S.sum.heroes)).includes(h)));
    const missing = todo.filter(c => Object.keys(S.sum.board).some(h => Object.values(S.sum.board[h]).some(a => a.takes.includes(c) && !a.split.includes(c))));
    if (!missing.length) return toast('Mọi clip đã tách.', 'ok');
    await post('split', { ws: S.ws, clips: missing }); toast(`Đã xếp ${missing.length} clip để tách.`, 'warn');
  };
  $('#helpBtn').onclick = () => $('#help').classList.remove('hidden');
  $('#helpClose').onclick = () => $('#help').classList.add('hidden');
  $('#legacyBtn').onclick = async () => {
    const p = await (await fetch('/api/ping')).json();
    if (p.legacy_built) location.href = '/legacy.html';
    else { await fetch('/api/legacy/build', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }); toast('Đang dựng dữ liệu trang cũ (lần đầu ~80 s), xong sẽ tự mở.', 'warn'); }
  };
  document.addEventListener('keydown', onKey);
  pollJobs();
  requestAnimationFrame(tick);
}
function localStorageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { } }
async function openWs(id) {
  S.ws = id; S.infos = {}; S.strips = {}; localStorageSet('ft.ws', id);
  await refreshSummary();
  const heroes = Object.keys(S.sum.actions);
  S.hero = heroes[0]; S.action = Object.keys(S.sum.actions[S.hero])[0];
  select(S.hero, S.action);
}
async function refreshSummary() { S.sum = await api('ws', { ws: S.ws }); renderBoard(); }
function renderBoard() {
  const b = $('#board'); b.innerHTML = '';
  const acts = [...new Set(Object.values(S.sum.actions).flatMap(a => Object.keys(a)))];
  const t = el('table', {}, el('tr', {}, el('th'), acts.map(a => el('th', {}, ACT_LABEL[a] || a))));
  for (const h of Object.keys(S.sum.actions)) {
    const tr = el('tr', {}, el('td', { class: 'h', title: S.sum.heroes[h].asset }, h));
    for (const a of acts) {
      const st = S.sum.board[h][a];
      if (!st) { tr.append(el('td')); continue; }
      const lab = { new: '–', split: 'tách', edited: 'dọn', sequenced: `${st.frames} kh`, exported: 'xuất' }[st.stage];
      tr.append(el('td', {}, el('span', { class: `st ${st.stage} ${h === S.hero && a === S.action ? 'sel' : ''}`, title: `${st.sheet}\ntake chọn: ${st.pick}\nđã tách: ${st.split.join(', ') || '-'}`, onclick: () => select(h, a) }, lab)));
    }
    t.append(tr);
  }
  b.append(t);
}
function select(h, a) {
  S.hero = h; S.action = a; S.seq = null; S.clean.clip = null; S.view.i = 0; S.takes.i = 0;
  $('#cur').textContent = `${h} · ${ACT_LABEL[a] || a} → ${act().sheet}`;
  renderBoard(); renderTab();
}
function setTab(t) { S.tab = t; for (const b of document.querySelectorAll('#tabs button')) b.classList.toggle('on', b.dataset.tab === t); for (const p of document.querySelectorAll('.pane')) p.classList.toggle('on', p.id === 'pane-' + t); renderTab(); }
function renderTab() { if (!S.sum) return; ({ takes: renderTakes, clean: renderClean, seq: renderSeq, view: renderView, export: renderExport })[S.tab](); }

// ---------------------------------------------------------------------------------------------------------- 1 takes
let takeCards = [];
async function renderTakes() {
  const p = $('#pane-takes'); p.innerHTML = ''; takeCards = [];
  const a = act();
  p.append(el('div', { class: 'row' },
    el('button', { onclick: () => { S.takes.playing = !S.takes.playing; } }, 'Chạy / dừng (Space)'),
    el('label', {}, 'Tốc độ ', speedSel(S.takes)),
    el('span', { class: 'muted' }, 'Các take chạy cùng nhịp (24 fps) để so sánh. Bấm "Chọn take này" để dùng take đó cho động tác.')));
  const cards = el('div', { class: 'cards' }); p.append(cards);
  for (const c of a.takes) {
    const isSplit = board().split.includes(c);
    const card = el('div', { class: `card ${c === a.pick ? 'pick' : ''}` });
    card.append(el('div', { class: 'row' }, el('b', {}, c), c === a.pick ? el('span', { class: 'ok' }, '✓ đang chọn') : ''));
    if (!isSplit) {
      card.append(el('div', { class: 'muted', style: 'width:220px;height:120px' }, 'Chưa tách clip này.'),
        el('button', { class: 'primary', onclick: async () => { await post('split', { ws: S.ws, clips: [c] }); toast(`Đã xếp tách ${c}`, 'warn'); } }, 'Tách clip này'));
    } else {
      const cv = el('canvas', { class: 'checker', height: 200, width: 160 });
      card.append(cv, el('div', { class: 'row' },
        el('button', { onclick: () => pickTake(c) }, 'Chọn take này'),
        el('button', { onclick: () => { S.clean.clip = c; setTab('clean'); } }, 'Dọn khung')));
      strip(S.hero, c, 200).then(s => { cv.width = s.w; takeCards.push({ cv, s }); }).catch(() => { });
    }
    cards.append(card);
  }
}
function speedSel(o) { const s = el('select', { onchange: e => { o.speed = +e.target.value; } }, [0.25, 0.5, 1, 2].map(v => el('option', { value: v, selected: v === o.speed }, `×${v}`))); return s; }
async function pickTake(c) {
  await post('config', { ws: S.ws, hero: S.hero, action: S.action, pick: c });
  const seq = await api('seq', { ws: S.ws, hero: S.hero, action: S.action });
  if (!seq) await post('seq', { ws: S.ws, hero: S.hero, action: S.action, data: await defaultSeq(c) });
  await refreshSummary(); renderTakes(); toast(`${S.hero} ${S.action}: dùng ${c}`, 'ok');
}
async function defaultSeq(c) {
  const inf = await info(S.hero, c);
  const keep = []; for (let f = 0; f < inf.frames; f += 2) keep.push(f);
  return { loop: !!act().loop, segments: [{ clip: c, keep, ms: keep.map(() => 83), dx: 0, dy: 0 }], hit: null };
}

// ---------------------------------------------------------------------------------------------------------- 2 clean
async function renderClean() {
  const p = $('#pane-clean'); p.innerHTML = '';
  const takes = splitTakes();
  if (!takes.length) { p.append(el('p', { class: 'muted' }, 'Chưa có take nào đã tách. Vào tab Take để tách clip.')); return; }
  const C = S.clean;
  if (!C.clip || !takes.includes(C.clip)) C.clip = takes.includes(act().pick) ? act().pick : takes[0];
  const inf = await info(S.hero, C.clip);
  C.edits = await api('edits', { ws: S.ws, hero: S.hero, clip: C.clip });
  C.f = Math.min(C.f, inf.frames - 1);
  if (inf.stale) p.append(el('p', { class: 'bad' }, 'Clip này được tách với thông số lưới khác: tách lại trước khi dọn (thao tác cũ sẽ lệch).'));
  const flagsBox = el('span', { class: 'muted' }, 'đang kiểm tra khung…');
  p.append(el('div', { class: 'row' },
    el('label', {}, 'Take ', el('select', { onchange: e => { C.clip = e.target.value; C.f = 0; renderClean(); } }, takes.map(c => el('option', { value: c, selected: c === C.clip }, c)))),
    el('label', {}, el('input', { type: 'checkbox', checked: C.raw, onchange: e => { C.raw = e.target.checked; drawEditor(); } }), 'xem bản gốc'),
    el('label', {}, el('input', { type: 'checkbox', checked: C.onion, onchange: e => { C.onion = e.target.checked; drawEditor(); } }), 'onion skin (O)'),
    el('button', { onclick: nextFlag }, 'Khung nghi ngờ tiếp (N)'), flagsBox));
  const stripBox = el('div', { class: 'strip', id: 'cleanStrip' }); p.append(stripBox);
  const ed = el('div', { class: 'editor' });
  const wrap = el('div', { class: 'canvaswrap checker' });
  const cv = el('canvas', { id: 'edCanvas' }); const ov = el('canvas', { id: 'edOverlay', style: 'position:absolute;left:0;top:0;cursor:crosshair' });
  wrap.append(cv, ov);
  ed.append(wrap, cleanTools()); p.append(ed);
  const [x0, y0, x1, y1] = inf.crop; const w = x1 - x0, h = y1 - y0;
  const z = Math.max(1, Math.min(4, 620 / h, 760 / w));
  for (const c of [cv, ov]) { c.width = Math.round(w * z); c.height = Math.round(h * z); }
  C.zoom = z; C.crop = inf.crop;
  bindEditor(ov);
  await drawStripClean();
  drawEditor();
  api('flags', { ws: S.ws, clip: C.clip, hero: S.hero }).then(fl => {
    C.flags = fl; drawStripClean();
    const bad = fl.filter(x => x.flags.length);
    flagsBox.textContent = bad.length ? `${bad.length} khung nghi ngờ: ` + Object.entries(bad.flatMap(x => x.flags).reduce((m, k) => (m[k] = (m[k] || 0) + 1, m), {})).map(([k, n]) => `${FLAG_LABEL[k]} ${n}`).join(', ') : 'Không có khung nghi ngờ.';
  });
}
function cleanTools() {
  const C = S.clean;
  const tool = (id, label, k) => el('label', {}, el('input', { type: 'radio', name: 'tool', checked: C.tool === id, onchange: () => { C.tool = id; } }), `${label} (${k})`);
  const e = C.edits; const dn = e.denoise || {};
  const specks = el('input', { type: 'number', min: 0, value: dn.specks || 0 }), pink = el('input', { type: 'checkbox', checked: !!dn.pink }), trail = el('input', { type: 'checkbox', checked: !!dn.trail });
  const val = () => ({ specks: +specks.value || 0, pink: pink.checked, trail: trail.checked });
  const copyN = el('input', { type: 'number', min: 1, value: 3 });
  const ops = (e.ops || {})[String(C.f)] || [];
  return el('div', { class: 'tools' },
    el('div', { class: 'grp' }, el('b', {}, 'Công cụ'),
      tool('brush', 'Cọ xóa', 'B'), tool('lasso', 'Vòng chọn xóa', 'L'), tool('erase', 'Bấm xóa mảnh', 'E'), tool('keep', 'Chỉ giữ mảnh bấm', 'G'), tool('restore', 'Cọ khôi phục', 'R'),
      el('label', {}, 'Cỡ cọ', el('input', { type: 'range', min: 1, max: 40, value: C.r, oninput: ev => { C.r = +ev.target.value; } })),
      el('div', { class: 'row' }, el('button', { onclick: undo }, 'Hoàn tác'), el('button', { onclick: redo }, 'Làm lại')),
      el('div', { class: 'muted' }, `Khung ${C.f}: ${ops.length} thao tác`),
      el('button', { onclick: () => mutate(ed => { delete (ed.ops || {})[String(C.f)]; }) }, 'Xóa thao tác của khung này'),
      el('div', { class: 'row' }, el('button', { onclick: () => copyOps(+copyN.value) }, 'Chép thao tác sang'), copyN, 'khung sau')),
    el('div', { class: 'grp' }, el('b', {}, 'Khử nhiễu (cả clip của hero)'),
      el('label', {}, 'Bỏ mảnh lẻ nhỏ hơn', specks, 'px'),
      el('label', {}, pink, 'khử viền hồng còn sót'),
      el('label', {}, trail, 'xóa vệt chém tím nhạt'),
      el('button', { class: 'primary', onclick: () => mutate(ed => { ed.denoise = val(); }) }, 'Áp cho clip này'),
      el('button', { onclick: () => batchDenoise(val(), [S.hero], null) }, 'Áp cho mọi clip của hero'),
      el('button', { onclick: () => batchDenoise(val(), null, null) }, 'Áp cho cả workspace')),
    el('div', { class: 'grp' }, el('b', {}, 'Cờ khung'), ...Object.entries(FLAG_LABEL).map(([k, v]) => el('div', {}, el('i', { class: `fl-${k}`, style: 'display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px' }), v))));
}
async function drawStripClean() {
  const C = S.clean, box = $('#cleanStrip'); if (!box) return;
  const s = await strip(S.hero, C.clip, 80);
  box.innerHTML = '';
  const flags = Object.fromEntries((C.flags || []).map(x => [x.f, x.flags]));
  for (let f = 0; f < s.n; f++) {
    const fl = flags[f] || [];
    const t = el('div', { class: `thumb ${f === C.f ? 'cur' : ''} ${(C.edits.ops || {})[String(f)] ? 'keep' : ''}`, title: `khung ${f}${fl.length ? '\n' + fl.map(k => FLAG_LABEL[k]).join(', ') : ''}`,
      style: `width:${s.w}px;height:${s.h}px;background-image:url(${s.img.src});background-position:-${f * s.w}px 0`, onclick: () => { C.f = f; refreshCleanSel(); } },
      el('span', { class: 'n' }, f), el('span', { class: 'fl' }, fl.map(k => el('i', { class: `fl-${k}` }))));
    box.append(t);
  }
  box.children[C.f]?.scrollIntoView({ block: 'nearest', inline: 'center' });
}
function refreshCleanSel() {
  const box = $('#cleanStrip'); if (!box) return;
  [...box.children].forEach((t, i) => t.classList.toggle('cur', i === S.clean.f));
  box.children[S.clean.f]?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  const tools = document.querySelector('#pane-clean .tools'); if (tools) tools.replaceWith(cleanTools());
  drawEditor();
}
let edToken = 0;
async function drawEditor() {
  const C = S.clean, cv = $('#edCanvas'); if (!cv) return;
  const tok = ++edToken; const n = (await info(S.hero, C.clip)).frames;
  const ctx = cv.getContext('2d'); const z = C.zoom;
  const imgs = await Promise.all([loadImg(frameUrl(S.hero, C.clip, C.f, C.raw)),
    C.onion && C.f > 0 ? loadImg(frameUrl(S.hero, C.clip, C.f - 1)) : null, C.onion && C.f < n - 1 ? loadImg(frameUrl(S.hero, C.clip, C.f + 1)) : null]);
  if (tok !== edToken) return;
  ctx.clearRect(0, 0, cv.width, cv.height); ctx.imageSmoothingEnabled = false;
  if (imgs[1]) { ctx.globalAlpha = 0.25; ctx.drawImage(imgs[1], 0, 0, imgs[1].width * z, imgs[1].height * z); }
  if (imgs[2]) { ctx.globalAlpha = 0.25; ctx.drawImage(imgs[2], 0, 0, imgs[2].width * z, imgs[2].height * z); }
  ctx.globalAlpha = 1; ctx.drawImage(imgs[0], 0, 0, imgs[0].width * z, imgs[0].height * z);
}
function bindEditor(ov) {
  const C = S.clean; const ctx = ov.getContext('2d'); let pts = null;
  const toWin = ev => { const r = ov.getBoundingClientRect(); return [Math.round((ev.clientX - r.left) / C.zoom + C.crop[0]), Math.round((ev.clientY - r.top) / C.zoom + C.crop[1])]; };
  const toCv = p => [(p[0] - C.crop[0]) * C.zoom, (p[1] - C.crop[1]) * C.zoom];
  const drawLive = (cur) => {
    ctx.clearRect(0, 0, ov.width, ov.height);
    if (cur && (C.tool === 'brush' || C.tool === 'restore')) { ctx.strokeStyle = C.tool === 'restore' ? '#44c27a' : '#ef5b5b'; ctx.beginPath(); const c = toCv(cur); ctx.arc(c[0], c[1], C.r * C.zoom, 0, 7); ctx.stroke(); }
    if (!pts || pts.length < 1) return;
    ctx.strokeStyle = C.tool === 'restore' ? '#44c27a' : '#ef5b5b'; ctx.fillStyle = 'rgba(239,91,91,.25)';
    ctx.lineWidth = (C.tool === 'lasso') ? 1.5 : 2 * C.r * C.zoom; ctx.lineCap = ctx.lineJoin = 'round';
    ctx.beginPath(); pts.forEach((p, i) => { const c = toCv(p); i ? ctx.lineTo(c[0], c[1]) : ctx.moveTo(c[0], c[1]); });
    if (C.tool === 'lasso') { ctx.closePath(); ctx.fill(); }
    ctx.stroke(); ctx.lineWidth = 1;
  };
  ov.onmousedown = ev => {
    const p = toWin(ev);
    if (C.tool === 'erase' || C.tool === 'keep') return addOp({ op: 'piece', x: p[0], y: p[1], mode: C.tool === 'keep' ? 'keep' : 'erase' });
    pts = [p]; drawLive(p);
  };
  ov.onmousemove = ev => { const p = toWin(ev); if (pts) { const l = pts[pts.length - 1]; if (Math.hypot(p[0] - l[0], p[1] - l[1]) >= 1.5) pts.push(p); } drawLive(p); };
  const end = () => {
    if (!pts) return; const ps = pts; pts = null; drawLive(null);
    if (C.tool === 'lasso') { if (ps.length >= 3) addOp({ op: 'lasso', pts: ps, mode: 'erase' }); }
    else addOp({ op: 'brush', pts: ps, r: C.r, mode: C.tool === 'restore' ? 'restore' : 'erase' });
  };
  ov.onmouseup = end; ov.onmouseleave = () => { end(); drawLive(null); };
}
function addOp(op) { const f = String(S.clean.f); return mutate(ed => { ed.ops = ed.ops || {}; (ed.ops[f] = ed.ops[f] || []).push(op); }); }
async function copyOps(n) {
  const C = S.clean; const src = (C.edits.ops || {})[String(C.f)]; if (!src) return toast('Khung này chưa có thao tác.', 'warn');
  const total = (await info(S.hero, C.clip)).frames;
  await mutate(ed => { for (let f = C.f + 1; f <= Math.min(total - 1, C.f + n); f++) ed.ops[String(f)] = [...(ed.ops[String(f)] || []), ...clone(src)]; });
}
const refreshFlags = debounce(async () => { const C = S.clean; C.flags = await api('flags', { ws: S.ws, clip: C.clip, hero: S.hero }); await drawStripClean(); }, 900);
async function mutate(fn) {
  const C = S.clean, k = key(S.hero, C.clip);
  (C.hist[k] = C.hist[k] || []).push(clone(C.edits)); C.redo[k] = [];
  fn(C.edits); await saveEdits();
}
async function saveEdits() {
  const C = S.clean;
  await post('edits', { ws: S.ws, hero: S.hero, clip: C.clip, data: C.edits });
  bump(S.hero, C.clip); drawEditor(); refreshFlags();
  const tools = document.querySelector('#pane-clean .tools'); if (tools) tools.replaceWith(cleanTools());
  refreshSummary();
}
async function undo() { const C = S.clean, k = key(S.hero, C.clip); const h = C.hist[k]; if (!h || !h.length) return; (C.redo[k] = C.redo[k] || []).push(clone(C.edits)); C.edits = h.pop(); await saveEdits(); }
async function redo() { const C = S.clean, k = key(S.hero, C.clip); const r = C.redo[k]; if (!r || !r.length) return; C.hist[k].push(clone(C.edits)); C.edits = r.pop(); await saveEdits(); }
async function batchDenoise(dn, heroes, clips) {
  const r = await post('denoise', { ws: S.ws, denoise: dn, heroes, clips });
  S.ver = {}; S.strips = {}; toast(`Khử nhiễu đã áp cho ${r.count} cặp (hero, clip).`, 'ok'); renderClean();
}
function nextFlag() {
  const C = S.clean; const fl = (C.flags || []).filter(x => x.flags.length).map(x => x.f); if (!fl.length) return;
  C.f = fl.find(f => f > C.f) ?? fl[0]; refreshCleanSel();
}

// ---------------------------------------------------------------------------------------------------------- 3 sequence
const saveSeq = debounce(async () => { await post('seq', { ws: S.ws, hero: S.hero, action: S.action, data: S.seq }); refreshSummary(); }, 400);
async function renderSeq() {
  const p = $('#pane-seq'); p.innerHTML = '';
  S.seq = await api('seq', { ws: S.ws, hero: S.hero, action: S.action });
  const takes = splitTakes();
  if (!S.seq) {
    p.append(el('p', {}, 'Chưa có chuỗi khung cho động tác này.'));
    if (!takes.length) { p.append(el('p', { class: 'muted' }, 'Tách một take trước (tab Take).')); return; }
    p.append(el('div', { class: 'row' }, 'Tạo từ take: ', takes.map(c => el('button', { onclick: async () => { S.seq = await defaultSeq(c); await post('seq', { ws: S.ws, hero: S.hero, action: S.action, data: S.seq }); refreshSummary(); renderSeq(); } }, c))));
    return;
  }
  const sq = S.seq;
  const nKeep = sq.segments.reduce((n, s) => n + s.keep.length, 0), total = sq.segments.reduce((n, s) => n + s.ms.reduce((a, b) => a + b, 0), 0);
  const msAll = el('input', { type: 'number', value: 83, min: 10 });
  p.append(el('div', { class: 'row' },
    el('b', {}, `${nKeep} khung, ${(total / 1000).toFixed(2)} s`),
    el('label', {}, el('input', { type: 'checkbox', checked: !!sq.loop, onchange: e => { sq.loop = e.target.checked; saveSeq(); renderSeq(); } }), 'lặp vòng'),
    el('span', {}, 'Thời gian đều:'), msAll, el('span', {}, 'ms'),
    el('button', { onclick: () => { sq.segments.forEach(s => s.ms = s.keep.map(() => +msAll.value)); saveSeq(); renderSeq(); } }, 'Áp'),
    [8, 10, 12, 15].map(fps => el('button', { onclick: () => { sq.segments.forEach(s => s.ms = s.keep.map(() => Math.round(1000 / fps))); saveSeq(); renderSeq(); } }, `${fps} fps`)),
    sq.hit ? el('span', { class: 'warn' }, `va chạm: đoạn ${sq.hit.seg + 1}, khung giữ thứ ${sq.hit.k + 1}`) : el('span', { class: 'muted' }, 'chưa đánh dấu va chạm (H)')));
  if (sq.loop) {
    const out = el('span', { class: 'muted' }, '');
    p.append(el('div', { class: 'row' }, el('button', { onclick: async () => {
      const its = sq.segments.flatMap(s => s.keep.map(f => [s.clip, f]));
      const r = await post('seam', { ws: S.ws, hero: S.hero, items: its });
      out.innerHTML = '';
      out.append(el('span', { class: r.ok ? 'ok' : 'warn' }, `chỗ nối cuối → đầu: ${r.score} (bước thường ${r.typical_step}) ${r.ok ? 'mượt' : 'có giật'}`),
        r.suggest_end_index < its.length - 1 ? el('button', { onclick: () => { trimTo(r.suggest_end_index); } }, `Cắt bớt sau khung giữ thứ ${r.suggest_end_index + 1} (gợi ý)`) : '');
    } }, 'Kiểm tra vòng lặp'), out));
  }
  for (let si = 0; si < sq.segments.length; si++) p.append(await segBox(si));
  const addSel = el('select', {}, takes.map(c => el('option', { value: c }, c)));
  p.append(el('div', { class: 'row' }, 'Thêm đoạn từ take ', addSel, el('button', { onclick: async () => { const s = (await defaultSeq(addSel.value)).segments[0]; s.keep = []; s.ms = []; sq.segments.push(s); saveSeq(); renderSeq(); } }, 'Thêm đoạn'),
    el('span', { class: 'muted' }, 'Ghép khung từ nhiều take: đoạn sau chạy tiếp đoạn trước. Bấm hình để giữ/bỏ (Shift+bấm: cả khoảng).')));
}
function trimTo(idx) {
  let n = 0; for (const s of S.seq.segments) { const room = Math.max(0, idx + 1 - n); n += s.keep.length; if (s.keep.length > room) { s.keep = s.keep.slice(0, room); s.ms = s.ms.slice(0, room); } }
  S.seq.segments = S.seq.segments.filter(s => s.keep.length || S.seq.segments.length === 1); saveSeq(); renderSeq();
}
async function segBox(si) {
  const sq = S.seq, s = sq.segments[si];
  const box = el('div', { class: 'seg' });
  const inf = await info(S.hero, s.clip);
  const st = await strip(S.hero, s.clip, 80);
  const a = el('input', { type: 'number', value: 0, min: 0, max: inf.frames - 1 }), b = el('input', { type: 'number', value: inf.frames - 1, min: 0, max: inf.frames - 1 }), nEvery = el('input', { type: 'number', value: 2, min: 1 });
  const setKeep = keep => { rekeep(si, keep); saveSeq(); renderSeq(); };
  box.append(el('div', { class: 'row' }, el('b', {}, `Đoạn ${si + 1}: ${s.clip}`), el('span', { class: 'muted' }, `${s.keep.length} khung giữ / ${inf.frames}`),
    el('label', {}, 'dx', el('input', { type: 'number', value: s.dx || 0, onchange: e => { s.dx = +e.target.value; saveSeq(); } })),
    el('label', {}, 'dy', el('input', { type: 'number', value: s.dy || 0, onchange: e => { s.dy = +e.target.value; saveSeq(); } })),
    si > 0 ? el('button', { onclick: () => joinPreview(si, box) }, 'Xem chỗ nối') : '',
    si > 0 ? el('button', { onclick: () => { [sq.segments[si - 1], sq.segments[si]] = [sq.segments[si], sq.segments[si - 1]]; sq.hit = null; saveSeq(); renderSeq(); } }, '↑') : '',
    sq.segments.length > 1 ? el('button', { onclick: () => { sq.segments.splice(si, 1); sq.hit = null; saveSeq(); renderSeq(); } }, 'Xóa đoạn') : ''));
  box.append(el('div', { class: 'row' }, 'Từ', a, 'đến', b,
    el('button', { onclick: () => { const k = []; for (let f = +a.value; f <= +b.value; f += Math.max(1, +nEvery.value)) k.push(f); setKeep(k); } }, 'Giữ 1 trong'), nEvery,
    el('button', { onclick: () => setKeep(s.keep.filter(f => f >= +a.value && f <= +b.value)) }, 'Chỉ giữ trong khoảng'),
    el('button', { onclick: () => setKeep(s.keep.filter(f => f < +a.value || f > +b.value)) }, 'Bỏ khoảng'),
    el('button', { onclick: () => setKeep([]) }, 'Bỏ hết')));
  const row = el('div', { class: 'strip' });
  let last = null;
  for (let f = 0; f < inf.frames; f++) {
    const ki = s.keep.indexOf(f), kept = ki >= 0;
    const isHit = sq.hit && sq.hit.seg === si && kept && sq.hit.k === ki;
    const isCur = S.seqCur.seg === si && S.seqCur.f === f;
    const t = el('div', { class: `thumb ${kept ? 'keep' : 'drop'} ${isCur ? 'cur' : ''}`, title: `khung ${f}`, style: `width:${st.w}px;height:${st.h + (kept ? 16 : 0)}px;background-image:url(${st.img.src});background-position:-${f * st.w}px 0` },
      el('span', { class: 'n' }, f), isHit ? el('span', { class: 'hit' }, 'HIT') : '');
    t.onclick = ev => {
      S.seqCur = { seg: si, f };
      if (ev.target.tagName === 'INPUT') return;
      if (ev.shiftKey && last !== null) { const lo = Math.min(last, f), hi = Math.max(last, f); const want = !kept; let k = new Set(s.keep); for (let x = lo; x <= hi; x++) want ? k.add(x) : k.delete(x); setKeep([...k]); }
      else setKeep(kept ? s.keep.filter(x => x !== f) : [...s.keep, f]);
      last = f;
    };
    if (kept) t.append(el('input', { type: 'number', value: s.ms[ki], title: 'ms', onchange: e => { s.ms[ki] = Math.max(10, +e.target.value); saveSeq(); } }));
    row.append(t);
  }
  box.append(row);
  return box;
}
function rekeep(si, keep) {
  // change the kept frames of a segment; durations and the hit follow their source frame
  const sq = S.seq, s = sq.segments[si];
  const old = Object.fromEntries(s.keep.map((f, i) => [f, s.ms[i]]));
  const hitF = sq.hit && sq.hit.seg === si ? s.keep[sq.hit.k] : undefined;
  s.keep = [...new Set(keep)].sort((x, y) => x - y);
  s.ms = s.keep.map(f => old[f] || s.ms[0] || 83);
  if (hitF !== undefined) { const k = s.keep.indexOf(hitF); sq.hit = k >= 0 ? { seg: si, k } : null; }
}
async function joinPreview(si, box) {
  const a = S.seq.segments[si - 1], b = S.seq.segments[si];
  if (!a.keep.length || !b.keep.length) return toast('Hai đoạn cần có khung giữ.', 'warn');
  const ia = await info(S.hero, a.clip), ib = await info(S.hero, b.clip);
  const [A, B] = await Promise.all([loadImg(frameUrl(S.hero, a.clip, a.keep[a.keep.length - 1])), loadImg(frameUrl(S.hero, b.clip, b.keep[0]))]);
  const W = ia.window[0], H = ia.window[1], z = Math.min(1.5, 420 / H);
  const cv = el('canvas', { width: W * z, height: H * z, class: 'checker' }); const c = cv.getContext('2d');
  c.globalAlpha = 0.5; c.drawImage(A, (ia.crop[0] + (a.dx || 0)) * z, (ia.crop[1] + (a.dy || 0)) * z, A.width * z, A.height * z);
  c.globalAlpha = 0.5; c.drawImage(B, (ib.crop[0] + (b.dx || 0)) * z, (ib.crop[1] + (b.dy || 0)) * z, B.width * z, B.height * z);
  box.append(el('div', {}, el('div', { class: 'muted' }, 'Khung cuối đoạn trước và khung đầu đoạn này chồng lên nhau: chỉnh dx, dy để khớp.'), cv));
}

// ---------------------------------------------------------------------------------------------------------- 4 view
let viewItems = [];
async function renderView() {
  const p = $('#pane-view'); p.innerHTML = '';
  const seq = await api('seq', { ws: S.ws, hero: S.hero, action: S.action });
  if (!seq || !seq.segments.some(s => s.keep.length)) { p.append(el('p', { class: 'muted' }, 'Chưa có khung nào được chọn (tab Chọn khung).')); return; }
  const V = S.view; const hcfg = S.sum.heroes[S.hero];
  viewItems = [];
  for (const [si, s] of seq.segments.entries()) {
    const inf = await info(S.hero, s.clip);
    s.keep.forEach((f, k) => viewItems.push({ clip: s.clip, f, ms: s.ms[k], dx: s.dx || 0, dy: s.dy || 0, inf, hit: seq.hit && seq.hit.seg === si && seq.hit.k === k }));
  }
  const imgs = await Promise.all(viewItems.map(it => loadImg(frameUrl(S.hero, it.clip, it.f))));
  viewItems.forEach((it, i) => it.img = imgs[i]);
  let L = 0, R = 0, U = 0, D = 0;
  for (const it of viewItems) { const [ax, ay] = it.inf.anchor, [x0, y0, x1, y1] = it.inf.crop; L = Math.max(L, ax - x0 - it.dx); R = Math.max(R, x1 + it.dx - ax); U = Math.max(U, ay - y0 - it.dy); D = Math.max(D, y1 + it.dy - ay); }
  const bodyPx = hcfg.body_px || viewItems[0].inf.body_px;
  const sc = { src: 1, game2: hcfg.body_2x / bodyPx, game1: hcfg.body_2x / 2 / bodyPx, px60: 60 / bodyPx }[V.scale];
  const zoom = V.scale === 'src' || V.scale === 'game2' ? 1 : 3;
  const cv = el('canvas', { id: 'viewCv' }); cv.width = Math.ceil((L + R) * sc * zoom) + 8; cv.height = Math.ceil((U + D) * sc * zoom) + 8;
  V.geo = { L, U, sc, zoom };
  const bgs = { checker: 'checker', dark: '', light: '', magenta: '', green: '' };
  const wrap = el('div', { class: `canvaswrap ${bgs[V.bg]}`, style: `display:inline-block;background:${{ dark: '#1a1c22', light: '#e9e6dc', magenta: '#ff00ff', green: '#3c5a3c' }[V.bg] || ''}` }, cv);
  const total = viewItems.reduce((a, b) => a + b.ms, 0);
  p.append(el('div', { class: 'row' },
    el('button', { onclick: () => { V.playing = !V.playing; } }, 'Chạy / dừng (Space)'),
    el('label', {}, 'Cỡ ', el('select', { onchange: e => { V.scale = e.target.value; renderView(); } },
      [['src', 'nguồn (pixel clip)'], ['game2', `game @2x (thân ${hcfg.body_2x}px)`], ['game1', `game @1x (thân ${hcfg.body_2x / 2}px), phóng ×3`], ['px60', 'thân 60 px, phóng ×3']].map(([v, l]) => el('option', { value: v, selected: v === V.scale }, l)))),
    el('label', {}, 'Nền ', el('select', { onchange: e => { V.bg = e.target.value; renderView(); } }, [['checker', 'ca-rô'], ['dark', 'tối'], ['light', 'sáng'], ['green', 'cỏ'], ['magenta', 'magenta']].map(([v, l]) => el('option', { value: v, selected: v === V.bg }, l)))),
    el('label', {}, el('input', { type: 'checkbox', checked: V.flip, onchange: e => { V.flip = e.target.checked; } }), 'lật trái phải'),
    el('label', {}, el('input', { type: 'checkbox', checked: V.onion, onchange: e => { V.onion = e.target.checked; } }), 'onion skin'),
    el('label', {}, 'Tốc độ ', speedSel(V)),
    el('span', { id: 'viewInfo', class: 'muted' }, `${viewItems.length} khung, ${(total / 1000).toFixed(2)} s${seq.loop ? ', lặp' : ''}`)));
  p.append(wrap);
  V.i = Math.min(V.i, viewItems.length - 1); V.t0 = performance.now(); V.loop = !!seq.loop;
  drawView();
}
function drawView() {
  const cv = $('#viewCv'); if (!cv || !viewItems.length) return;
  const V = S.view, { L, U, sc, zoom } = V.geo, c = cv.getContext('2d');
  c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, cv.width, cv.height);
  c.imageSmoothingEnabled = zoom === 1;
  const place = (it, alpha) => {
    const [ax, ay] = it.inf.anchor, [x0, y0] = it.inf.crop;
    const x = (x0 + it.dx - (ax - L)) * sc * zoom + 4, y = (y0 + it.dy - (ay - U)) * sc * zoom + 4;
    c.globalAlpha = alpha;
    if (zoom > 1) { const o = new OffscreenCanvas(Math.max(1, Math.round(it.img.width * sc)), Math.max(1, Math.round(it.img.height * sc))); const oc = o.getContext('2d'); oc.drawImage(it.img, 0, 0, o.width, o.height); c.drawImage(o, x, y, o.width * zoom, o.height * zoom); }
    else c.drawImage(it.img, x, y, it.img.width * sc, it.img.height * sc);
  };
  if (V.flip) { c.translate(cv.width, 0); c.scale(-1, 1); }
  if (V.onion && V.i > 0) place(viewItems[V.i - 1], 0.3);
  place(viewItems[V.i], 1); c.globalAlpha = 1;
  c.setTransform(1, 0, 0, 1, 0, 0);
  if (viewItems[V.i].hit) { c.strokeStyle = '#f2b94b'; c.lineWidth = 4; c.strokeRect(2, 2, cv.width - 4, cv.height - 4); }
  const vi = $('#viewInfo'); if (vi) vi.textContent = `khung ${V.i + 1}/${viewItems.length} (${viewItems[V.i].clip} #${viewItems[V.i].f}, ${viewItems[V.i].ms} ms)`;
}

// ---------------------------------------------------------------------------------------------------------- 5 export
function exportLog(t) { const l = $('#exportLog'); if (l) l.textContent = t + '\n' + l.textContent; }
async function renderExport() {
  const p = $('#pane-export'); p.innerHTML = '';
  const h = S.hero, hc = S.sum.heroes[h];
  const cw = el('input', { type: 'number', value: hc.cell[0] }), ch = el('input', { type: 'number', value: hc.cell[1] }), body = el('input', { type: 'number', value: hc.body_2x });
  const shadow = el('input', { type: 'checkbox', checked: hc.shadow !== false });
  const assetIn = el('input', { type: 'text', value: hc.asset, style: 'width:420px' });
  p.append(el('div', { class: 'card' }, el('b', {}, `Thiết lập ${h}`),
    el('div', { class: 'row' }, 'Canvas @1x', cw, '×', ch, 'Thân @2x', body, 'px', el('label', {}, shadow, 'bóng dưới chân'),
      el('button', { onclick: async () => { await post('config', { ws: S.ws, hero: h, heroPatch: { cell: [+cw.value, +ch.value], body_2x: +body.value, shadow: shadow.checked } }); await refreshSummary(); toast('Đã lưu thiết lập.', 'ok'); renderExport(); } }, 'Lưu')),
    el('div', { class: 'muted' }, `Asset: ${hc.asset}. Lần xuất đầu tiên của một asset chốt canvas và cỡ thân cho MỌI động tác: kiểm tra canvas trước. ${hc.note || ''}`)));
  const fitBox = el('div', { class: 'card' }, el('b', {}, 'Canvas và cỡ thân'), el('div', { class: 'muted' }, 'đang đo…'));
  p.append(fitBox);
  const acts = Object.keys(S.sum.actions[h]).filter(a => S.sum.board[h][a].frames > 0);
  const checks = acts.map(a => el('input', { type: 'checkbox', checked: true, 'data-a': a }));
  p.append(el('div', { class: 'card' }, el('b', {}, 'Xuất sheet'),
    el('div', { class: 'row' }, acts.length ? acts.map((a, i) => el('label', {}, checks[i], `${ACT_LABEL[a] || a} → ${S.sum.actions[h][a].sheet}`)) : el('span', { class: 'muted' }, 'Chưa có động tác nào đã chọn khung.')),
    el('div', { class: 'row' }, 'Thư mục asset đích', assetIn, el('span', { class: 'muted' }, '(đổi sang thư mục khác để xuất thử)')),
    el('div', { class: 'row' }, el('button', { class: 'primary', disabled: !acts.length, onclick: async () => {
      const sel = checks.filter(c => c.checked).map(c => c.dataset.a); if (!sel.length) return;
      const r = await post('export', { ws: S.ws, hero: h, actions: sel, asset: assetIn.value !== hc.asset ? assetIn.value : null }); toast('Đang xuất…', 'warn'); exportLog(`xếp việc xuất ${sel.join(', ')} (job ${r.job})`);
    } }, 'Xuất (một động tác một lần trước, vòng lặp sau)')),
    el('div', { id: 'exportLog', class: 'log' }, '')));
  try {
    const [fit, bd] = await Promise.all([api('fit', { ws: S.ws, hero: h }), api('body', { ws: S.ws, hero: h })]);
    fitBox.innerHTML = '';
    const big = fit.suggest[0] > fit.cell[0] || fit.suggest[1] > fit.cell[1];
    fitBox.append(el('b', {}, 'Canvas và cỡ thân'), el('div', {}, `Hệ số thu phóng của hero: ×${fit.scale} (thân trong clip → ${hc.body_2x}px @2x).`),
      el('table', { class: 'grid' }, el('tr', {}, el('th', {}, 'Động tác'), el('th', {}, 'Cần canvas @1x'), el('th', {}, 'Vừa?'), el('th', {}, 'Cỡ thân khung đầu so với trung vị')),
        Object.keys(S.sum.actions[h]).filter(a => fit.per_action[a] || bd.actions[a]).map(a => el('tr', {}, el('td', {}, ACT_LABEL[a] || a),
          el('td', {}, fit.per_action[a] ? `${fit.per_action[a].w}×${fit.per_action[a].h}` : '-'),
          el('td', { class: fit.per_action[a]?.fits ? 'ok' : 'bad' }, fit.per_action[a] ? (fit.per_action[a].fits ? 'vừa' : 'không vừa') : '-'),
          el('td', { class: bd.actions[a]?.ok ? 'ok' : 'warn' }, bd.actions[a] ? `×${bd.actions[a].vs_median} (cao ${bd.actions[a].height}px)` : '-')))),
      big ? el('div', { class: 'row' }, el('span', { class: 'bad' }, `Canvas ${fit.cell.join('×')} không đủ: cần ${fit.suggest.join('×')}.`),
        el('button', { onclick: async () => { await post('config', { ws: S.ws, hero: h, heroPatch: { cell: fit.suggest } }); await refreshSummary(); renderExport(); } }, 'Dùng canvas gợi ý')) : el('div', { class: 'ok' }, `Mọi động tác vừa canvas ${fit.cell.join('×')}.`),
      el('div', { class: 'muted' }, 'Cỡ thân lệch quá 4% sẽ bị video_to_sheet co giãn theo cỡ thân của lần xuất đầu.'));
  } catch (e) { fitBox.append(el('div', { class: 'bad' }, String(e.message || e))); }
}

// ---------------------------------------------------------------------------------------------------------- animation and keys
let lastT = performance.now(), acc = 0;
function tick(t) {
  const dt = t - lastT; lastT = t;
  if (S.tab === 'takes' && S.takes.playing && takeCards.length) {
    acc += dt * S.takes.speed;
    if (acc >= 1000 / 24) { acc = 0; S.takes.i++; for (const { cv, s } of takeCards) { const c = cv.getContext('2d'); const f = S.takes.i % s.n; c.clearRect(0, 0, cv.width, cv.height); c.drawImage(s.img, f * s.w, 0, s.w, s.h, 0, 0, s.w, s.h); } }
  }
  if (S.tab === 'view' && viewItems.length && S.view.playing) {
    const V = S.view; acc += dt * V.speed;
    if (acc >= viewItems[V.i].ms) { acc = 0; V.i = V.i + 1 >= viewItems.length ? (V.loop ? 0 : (V.playing = false, V.i)) : V.i + 1; drawView(); }
  }
  requestAnimationFrame(tick);
}
function onKey(e) {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
  const C = S.clean, k = e.key.toLowerCase();
  if (e.ctrlKey && k === 'z') { e.preventDefault(); return undo(); }
  if (e.ctrlKey && k === 'y') { e.preventDefault(); return redo(); }
  if (k === ' ') { e.preventDefault(); if (S.tab === 'takes') S.takes.playing = !S.takes.playing; if (S.tab === 'view') { S.view.playing = !S.view.playing; if (S.view.playing && S.view.i >= viewItems.length - 1 && !S.view.loop) S.view.i = 0; } return; }
  if (S.tab === 'clean') {
    if (k === 'arrowleft') { C.f = Math.max(0, C.f - 1); refreshCleanSel(); }
    else if (k === 'arrowright') { C.f = C.f + 1; info(S.hero, C.clip).then(i => { C.f = Math.min(C.f, i.frames - 1); refreshCleanSel(); }); }
    else if (k === 'n') nextFlag();
    else if (k === 'o') { C.onion = !C.onion; drawEditor(); }
    else if ('blegr'.includes(k) && k.length === 1) { C.tool = { b: 'brush', l: 'lasso', e: 'erase', g: 'keep', r: 'restore' }[k]; const t = document.querySelector('#pane-clean .tools'); if (t) t.replaceWith(cleanTools()); }
    else if (k === '[') C.r = Math.max(1, C.r - 1); else if (k === ']') C.r = Math.min(40, C.r + 1);
  } else if (S.tab === 'view') {
    if (k === 'arrowleft') { S.view.i = Math.max(0, S.view.i - 1); drawView(); }
    else if (k === 'arrowright') { S.view.i = Math.min(viewItems.length - 1, S.view.i + 1); drawView(); }
    else if (k === 'o') { S.view.onion = !S.view.onion; drawView(); }
  } else if (S.tab === 'seq' && S.seq) {
    const cur = S.seqCur, s = S.seq.segments[cur.seg]; if (!s || cur.f === undefined) return;
    if (k === 'arrowleft' || k === 'arrowright') { cur.f = Math.max(0, cur.f + (k === 'arrowleft' ? -1 : 1)); renderSeq(); }
    else if (k === 'k') { rekeep(cur.seg, s.keep.includes(cur.f) ? s.keep.filter(x => x !== cur.f) : [...s.keep, cur.f]); saveSeq(); renderSeq(); }
    else if (k === 'h') { const i = s.keep.indexOf(cur.f); if (i < 0) return toast('Khung va chạm phải là khung đang giữ.', 'warn'); S.seq.hit = (S.seq.hit && S.seq.hit.seg === cur.seg && S.seq.hit.k === i) ? null : { seg: cur.seg, k: i }; saveSeq(); renderSeq(); }
  }
}
init().catch(e => toast('Không tải được: ' + e.message, 'bad'));
