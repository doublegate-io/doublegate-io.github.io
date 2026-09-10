/* sky.js — the knowledge map on sky.html.
 *
 * What it draws
 * -------------
 * Twenty constellations, one per category of what an organization's agents
 * learn. Each star is one claim a reviewer signed. Faint long lines join
 * categories that relate to each other; short lines inside a constellation
 * join each star to its nearest neighbours. Every couple of seconds a claim
 * arrives from outside and one of the five verdicts happens to it, drawn in
 * the same five colours as the still figure on the overview:
 *
 *   new        a star appears; the first star in a dormant category founds
 *              the constellation and its name fades in
 *   sharpened  a revision supersedes a star; the parent stays faint behind
 *   merged     two stars converge on one; both parents stay faint behind
 *   held       the claim contradicts a star, reconciliation is refused, both
 *              stay live with the tension drawn between them
 *   refused    the arrival turns hollow and falls away; it is never a star,
 *              and the ledger on the right records why
 *
 * The verdict mix follows the still figure's split (23 / 14 / 11 / 8 / 4 of
 * sixty). Which claim arrives next is random, and so is when: inter-arrival
 * times are exponential around two seconds with the occasional burst, which is
 * what a real queue looks like and what a metronome does not. When every claim
 * has arrived once, the ones that were superseded or refused come round again
 * -- the same lesson learned by another agent -- so the stream does not stop.
 * The base sky is seeded, so two visitors see the same constellations in the
 * same places; from there on, no two visits are alike.
 *
 * Camera: drag turns the sky, the wheel zooms at the pointer, a double-click
 * dives into a constellation, shift-drag (or a second finger) pans, arrow keys
 * turn, +/- zoom, 0 resets the view. Zoom is a magnification of the
 * projection, not a move of the camera through the stars, so a constellation
 * at 6x is the same shape it was at 1x, only readable.
 *
 * Why canvas 2D and no library: 800 points, a few hundred segments, and a
 * perspective projection are well inside what one canvas does at 60 fps, and
 * the site ships no JavaScript dependencies. The colours come from style.css
 * so the five verdicts cannot drift from the rest of the site.
 */
(function () {
  'use strict';

  var data = window.SKY_DATA;
  var canvas = document.getElementById('sky');
  if (!data || !canvas || !canvas.getContext) return;
  var ctx = canvas.getContext('2d');
  var stage = canvas.parentNode;
  var feedEl = document.getElementById('sky-feed');
  var countEl = document.getElementById('sky-count');
  var tip = document.getElementById('sky-tip');
  var pauseBtn = document.getElementById('sky-pause');
  var resetBtn = document.getElementById('sky-reset');
  var zoomEl = document.getElementById('sky-zoom');
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- palette: the five verdicts are the site's five accents -------------
  var css = getComputedStyle(document.documentElement);
  function v(name, fallback) { var s = css.getPropertyValue(name).trim(); return s || fallback; }
  var COLOR = {
    'new': v('--cyn', '#22d3ee'),
    sharp: v('--grn', '#34d399'),
    merge: v('--vio', '#a78bfa'),
    held: v('--amb', '#fbbf24'),
    refused: v('--red', '#fb7185'),
    ink: v('--ink', '#e6e9ef'),
    faint: v('--ink-faint', '#8d97a9'),
    line: v('--line', '#1e2430')
  };
  var SANS = v('--sans', 'system-ui, sans-serif');
  var VERDICTS = ['new', 'sharp', 'merge', 'held', 'refused'];
  var WEIGHT = { 'new': 23, sharp: 14, merge: 11, held: 8, refused: 4 };
  var CHIP = {
    'new': 'New', sharp: 'Sharpened', merge: 'Merged from two',
    held: 'Held, both kept', refused: 'Refused'
  };
  // Why an arrival is refused, by the kind of thing it is: a skill fails for what
  // it carries, a belief for what it says.
  var REFUSAL = {
    s: ['a payload where a skill expected text', 'a credential in the body', 'reaches the network without saying so'],
    m: ['instructions aimed at the reviewer', 'contradicts its own cited source', 'a secret pasted in the body'],
    f: ['contradicts its own cited source', 'no source, and the claim is about a regulated matter', 'instructions aimed at the reviewer'],
    p: ['names a person, not a role', 'instructions aimed at the reviewer'],
    c: ['contradicts the convention it cites', 'scoped to a system that does not exist here', 'a secret pasted in the body']
  };
  var KIND = data.kinds; // m s f p c -> words

  // ---- seeded randomness for the base sky; Math.random for arrivals ---------
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function hash(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function gauss(r) {
    var u = 0, w = 0;
    while (u === 0) u = r();
    while (w === 0) w = r();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * w);
  }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  // ---- tiny vector kit -------------------------------------------------------
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function addTo(a, d, s) { a[0] += d[0] * s; a[1] += d[1] * s; a[2] += d[2] * s; }
  function len(a) { return Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]); }
  function lerp3(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
  function dist(a, b) { return len(sub(a, b)); }

  // ---- layout: category centres from a small 3D force layout ---------------
  // Repulsion between every pair, springs along the relation edges, a pull to
  // the centre, a squash on y so the sky is a thick disc rather than a ball,
  // then a separation pass so no two constellations sit inside each other.
  // Seeded and run once, so it is the same on every load.
  var cats = data.categories;
  var index = {};
  cats.forEach(function (c, i) { index[c.id] = i; });
  var edges = [];
  (function () {
    var seen = {};
    cats.forEach(function (c, i) {
      c.related.forEach(function (rid) {
        var j = index[rid];
        if (j === undefined) return;
        var k = i < j ? i + ':' + j : j + ':' + i;
        if (!seen[k]) { seen[k] = 1; edges.push([i, j]); }
      });
    });
  })();
  var CLUSTER_R = 0.085;     // sigma of a constellation's star cloud
  var MIN_SEP = 0.5;         // no two centres closer than this after layout
  var centres = (function () {
    var r = rng(7), n = cats.length, i, j, it;
    var p = cats.map(function () { return [gauss(r), gauss(r) * 0.5, gauss(r)]; });
    for (it = 0; it < 600; it++) {
      var f = p.map(function () { return [0, 0, 0]; });
      for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) {
        var d = sub(p[i], p[j]); var L = Math.max(len(d), 0.05); var s = 0.05 / (L * L);
        addTo(f[i], d, s / L); addTo(f[j], d, -s / L);
      }
      edges.forEach(function (e) {
        var d = sub(p[e[1]], p[e[0]]); var L = Math.max(len(d), 0.01); var s = (L - 0.8) * 0.05;
        addTo(f[e[0]], d, s / L); addTo(f[e[1]], d, -s / L);
      });
      for (i = 0; i < n; i++) { addTo(f[i], p[i], -0.012); f[i][1] -= p[i][1] * 0.05; addTo(p[i], f[i], 1); }
    }
    var m = 0;
    p.forEach(function (q) { m = Math.max(m, len(q)); });
    p = p.map(function (q) { return [q[0] / m, q[1] / m * 0.6, q[2] / m]; });
    for (it = 0; it < 300; it++) {
      var moved = false;
      for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) {
        var d2 = sub(p[i], p[j]); var L2 = len(d2);
        if (L2 < MIN_SEP) {
          var push = (MIN_SEP - L2) / 2 / Math.max(L2, 0.001);
          addTo(p[i], d2, push); addTo(p[j], d2, -push); moved = true;
        }
      }
      if (!moved) break;
    }
    var m2 = 0;
    p.forEach(function (q) { m2 = Math.max(m2, len(q)); });
    var k = m2 > 1.08 ? 1.08 / m2 : 1;   // shrink only if the separation pass pushed past the rim
    return p.map(function (q) { return [q[0] * k, q[1] * k, q[2] * k]; });
  })();

  // ---- state -----------------------------------------------------------------
  var stars, ghosts, tensions, present, pool, inflight, counts, arrivals, dormant, founded, lineCache;

  function seededPos(ci, j) {
    var r = rng(hash(cats[ci].id + ':' + j));
    var c = centres[ci], best = null, bestGap = -1;
    for (var t = 0; t < 8; t++) {
      var p = [c[0] + gauss(r) * CLUSTER_R, c[1] + gauss(r) * CLUSTER_R * 0.7, c[2] + gauss(r) * CLUSTER_R];
      var gap = Infinity;
      present[ci].forEach(function (s) { gap = Math.min(gap, dist(s.pos, p)); });
      if (gap > 0.03) return p;
      if (gap > bestGap) { bestGap = gap; best = p; }
    }
    return best;
  }

  function makeStar(ci, j, k, text, pos, verdict, now) {
    var s = { ci: ci, j: j, k: k, text: text, pos: pos, born: now, halo: verdict, haloT: now, revs: 0, via: verdict, parents: 0 };
    stars.push(s); present[ci].add(s); lineCache[ci] = null;
    return s;
  }
  function retire(s, pos, now) {
    present[s.ci].delete(s); lineCache[s.ci] = null;
    stars.splice(stars.indexOf(s), 1);
    for (var i = tensions.length - 1; i >= 0; i--) if (tensions[i].a === s || tensions[i].b === s) tensions.splice(i, 1);
    if (pinned === s) { pinned = null; hideTip(); }
    ghosts.push({ ci: s.ci, pos: pos || s.pos, born: now });
  }

  function reset() {
    var now = performance.now();
    stars = []; ghosts = []; tensions = []; inflight = []; pool = []; arrivals = 0;
    present = cats.map(function () { return new Set(); });
    lineCache = cats.map(function () { return null; });
    counts = {}; VERDICTS.forEach(function (x) { counts[x] = 0; });
    // Six categories start dark and are founded live; the rest start with a
    // seeded handful of stars so the sky reads as pre-existing.
    dormant = new Set(['devenv', 'product', 'queues', 'ml', 'testing', 'analytics']);
    founded = {};
    var r = rng(11);
    cats.forEach(function (c, ci) {
      var order = c.claims.map(function (_, j) { return j; });
      for (var i = order.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)); var t = order[i]; order[i] = order[j]; order[j] = t; }
      var seedN = dormant.has(c.id) ? 0 : 9 + Math.floor(r() * 8);
      order.forEach(function (j, n) {
        if (n < seedN) makeStar(ci, j, c.claims[j][0], c.claims[j][1], seededPos(ci, j), null, now - 60000);
        else pool.push([ci, j]);
      });
    });
    while (feedEl.firstChild) feedEl.removeChild(feedEl.firstChild);
    updateCounts();
    dirty = true;
  }

  // ---- arrivals ----------------------------------------------------------------
  var paused = !!reduced, nextAt = 0;
  if (pauseBtn) {
    pauseBtn.textContent = paused ? 'Resume' : 'Pause';
    pauseBtn.setAttribute('aria-pressed', paused ? 'true' : 'false');
  }

  function chooseVerdict(ci) {
    var n = present[ci].size, total = 0, ok = [];
    VERDICTS.forEach(function (x) {
      if (x === 'sharp' && n < 1) return;
      if (x === 'merge' && n < 2) return;
      if (x === 'held' && n < 1) return;
      ok.push(x); total += WEIGHT[x];
    });
    var roll = Math.random() * total;
    for (var i = 0; i < ok.length; i++) { roll -= WEIGHT[ok[i]]; if (roll <= 0) return ok[i]; }
    return ok[ok.length - 1];
  }
  function others(ci, count) {
    var arr = Array.from(present[ci]).filter(function (s) { return !s.slideTo; });
    for (var i = arr.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
    return arr.slice(0, count);
  }

  function refill() {
    // Every claim has arrived once. Claims with no star in the sky right now --
    // superseded parents, refused arrivals -- can come round again.
    var live = {};
    stars.forEach(function (s) { live[s.ci + ':' + s.j] = 1; });
    cats.forEach(function (c, ci) {
      c.claims.forEach(function (_, j) { if (!live[ci + ':' + j]) pool.push([ci, j]); });
    });
  }
  function arrive(now) {
    if (!pool.length) refill();
    if (!pool.length) return;
    var pi = Math.floor(Math.random() * pool.length);
    var entry = pool.splice(pi, 1)[0], ci = entry[0], j = entry[1];
    var claim = cats[ci].claims[j];
    var verdict = chooseVerdict(ci);
    var target = seededPos(ci, j), parents = [];
    if (verdict === 'sharp') { parents = others(ci, 1); if (parents.length < 1) verdict = 'new'; }
    if (verdict === 'merge') { parents = others(ci, 2); if (parents.length < 2) verdict = 'new'; }
    if (verdict === 'held') { parents = others(ci, 1); if (parents.length < 1) verdict = 'new'; }
    if (verdict === 'sharp') target = [parents[0].pos[0] + 0.009, parents[0].pos[1] + 0.007, parents[0].pos[2]];
    if (verdict === 'merge') target = lerp3(parents[0].pos, parents[1].pos, 0.5);
    if (verdict === 'held') target = lerp3(target, parents[0].pos, 0.5);
    var dir = len(target) > 0.01 ? target : centres[ci];
    var m = len(dir) || 1;
    var from = [dir[0] / m * 1.9 + gauss(Math.random) * 0.08, dir[1] / m * 1.9 + gauss(Math.random) * 0.08, dir[2] / m * 1.9];
    inflight.push({ ci: ci, j: j, k: claim[0], text: claim[1], verdict: verdict, from: from, to: target, parents: parents, start: now, dur: reduced ? 1 : 1100, landed: false });
  }

  function land(a, now) {
    var ci = a.ci, s;
    counts[a.verdict] += 1; arrivals += 1;
    var isFounding = false;
    if (a.verdict === 'refused') {
      a.reason = pick(REFUSAL[a.k] || REFUSAL.m);
    } else if (a.verdict === 'new') {
      if (dormant.has(cats[ci].id)) { dormant.delete(cats[ci].id); founded[ci] = now; isFounding = true; }
      s = makeStar(ci, a.j, a.k, a.text, a.to, 'new', now);
    } else if (a.verdict === 'sharp') {
      var p = a.parents[0];
      s = makeStar(ci, a.j, a.k, a.text, a.to, 'sharp', now);
      s.revs = p.revs + 1; s.parents = 1;
      retire(p, [p.pos[0] - 0.011, p.pos[1] - 0.009, p.pos[2]], now);
    } else if (a.verdict === 'merge') {
      s = makeStar(ci, a.j, a.k, a.text, a.to, 'merge', now);
      s.parents = 2;
      a.parents.forEach(function (p, i) {
        // the parents slide to the merge point, then stay behind as ghosts
        p.slideTo = a.to; p.slideFrom = p.pos.slice(); p.slideStart = now;
        p.slideOffset = i === 0 ? [-0.016, -0.01, 0] : [0.016, -0.01, 0];
      });
    } else if (a.verdict === 'held') {
      s = makeStar(ci, a.j, a.k, a.text, a.to, 'held', now);
      a.parents[0].halo = 'held'; a.parents[0].haloT = now;
      tensions.push({ a: s, b: a.parents[0], born: now });
    }
    feed(a, isFounding);
    updateCounts();
  }

  function inspectContribution(text, outcome, announce) {
    var selection = document.getElementById('sky-selection-text');
    var detail = document.getElementById('sky-selection-outcome');
    if (selection && detail) {
      selection.parentNode.setAttribute('aria-live', announce ? 'polite' : 'off');
      selection.textContent = text;
      detail.textContent = outcome;
    }
  }

  function feed(a, isFounding) {
    var li = document.createElement('li');
    li.className = 'arr v-' + a.verdict;
    var chip = document.createElement('span');
    chip.className = 'chip';
    chip.textContent = isFounding ? 'New constellation' : CHIP[a.verdict];
    var cat = document.createElement('span');
    cat.className = 'cat';
    cat.textContent = cats[a.ci].name;
    var txt = document.createElement('span');
    txt.className = 'txt';
    txt.textContent = a.text + (a.verdict === 'refused' ? ' \u2014 ' + a.reason : '');
    var when = document.createElement('time');
    var d = new Date();
    when.dateTime = d.toISOString();
    when.textContent = [d.getHours(), d.getMinutes(), d.getSeconds()].map(function (n) { return (n < 10 ? '0' : '') + n; }).join(':');
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'sky-inspect';
    button.setAttribute('aria-controls', 'sky-selection');
    button.appendChild(when); button.appendChild(chip); button.appendChild(cat); button.appendChild(txt);
    button.addEventListener('focus', function () {
      // Freeze arrivals while keyboard users navigate; don't remove their focused row.
      if (pauseBtn && pauseBtn.getAttribute('aria-pressed') !== 'true') pauseBtn.click();
    });
    button.addEventListener('click', function () {
      var outcomes = {
        new: 'A new contribution enters the shared knowledge in this example.',
        sharp: 'A revision supersedes an earlier claim; its history is retained.',
        merge: 'Related claims are reconciled, with their parents retained.',
        held: 'A disagreement stays open for review.',
        refused: 'Refused in this example: ' + (a.reason || 'review rejected the contribution.')
      };
      inspectContribution(a.text, CHIP[a.verdict] + ' — ' + outcomes[a.verdict], true);
    });
    li.appendChild(button);
    feedEl.insertBefore(li, feedEl.firstChild);
    while (feedEl.children.length > 14) feedEl.removeChild(feedEl.lastChild);
  }

  function updateCounts() {
    VERDICTS.forEach(function (x) {
      var el = document.getElementById('sky-n-' + x);
      if (el) el.textContent = counts[x];
    });
    if (countEl) countEl.textContent = arrivals;
  }

  // ---- camera ------------------------------------------------------------------
  // yaw/pitch turn the sky; Z magnifies the projection; ox/oy pan the image in
  // screen pixels so a zoomed-in constellation can be brought to the middle.
  var HOME = { yaw: -0.55, pitch: 0.62 };
  var yaw = HOME.yaw, pitch = HOME.pitch, vYaw = 0, vPitch = 0, D = 2.7;
  var Z = 1, ox = 0, oy = 0, ZMIN = 0.6, ZMAX = 9;
  var W = 0, H = 0, dpr = 1, F = 1;
  function project(p, out) {
    var cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    var x = p[0] * cy + p[2] * sy, z1 = -p[0] * sy + p[2] * cy;
    var y = p[1] * cp - z1 * sp, z = p[1] * sp + z1 * cp;
    var s = F * Z / (D - z);
    out.x = W / 2 + ox + x * s; out.y = H / 2 + oy - y * s; out.z = z;
    out.s = D / (D - z) * Math.pow(Z, 0.72);     // point-size scale: grows with zoom, slower than the picture
    out.a = Math.max(0.12, Math.min(1, 0.3 + 0.7 * (z + 1) / 2));
    return out;
  }
  function resize() {
    var w = stage.clientWidth, h = stage.clientHeight || Math.round(w * 0.62);
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = w; H = h; F = Math.min(w * 1.05, h * 1.28);
    HOME.pitch = w < 600 ? 0.8 : 0.62;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    canvas.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    dirty = true;
  }
  // Zoom so that the sky point under (px, py) stays under (px, py).
  function zoomAt(px, py, factor, animate) {
    var z2 = Math.max(ZMIN, Math.min(ZMAX, Z * factor));
    var k = z2 / Z;
    if (k === 1) return;
    var tox = (px - W / 2) - ((px - W / 2) - ox) * k;
    var toy = (py - H / 2) - ((py - H / 2) - oy) * k;
    if (animate && !reduced) { tween = { z0: Z, z1: z2, x0: ox, x1: tox, y0: oy, y1: toy, t0: performance.now(), dur: 420 }; }
    else { Z = z2; ox = tox; oy = toy; }
    dirty = true; showZoom();
  }
  function resetView(animate) {
    if (animate && !reduced) tween = { z0: Z, z1: 1, x0: ox, x1: 0, y0: oy, y1: 0, t0: performance.now(), dur: 420, yaw0: yaw, yaw1: HOME.yaw, pitch0: pitch, pitch1: HOME.pitch };
    else { Z = 1; ox = oy = 0; yaw = HOME.yaw; pitch = HOME.pitch; }
    vYaw = vPitch = 0; dirty = true; showZoom();
  }
  var tween = null;
  function showZoom() { if (zoomEl) zoomEl.textContent = (Z < 1.05 ? '1' : Z.toFixed(Z < 3 ? 1 : 0)) + '\u00d7'; }
  // Keep a zoomed view from being panned off into nothing: the sky's centre
  // may not leave the canvas.
  function clampPan() {
    // the sky's radius on screen grows with zoom, and so must the pan range
    var rx = F * Z / D * 1.3 + W * 0.4, ry = F * Z / D * 1.3 + H * 0.4;
    ox = Math.max(-rx, Math.min(rx, ox));
    oy = Math.max(-ry, Math.min(ry, oy));
  }

  // ---- constellation lines: nearest-neighbour sticks, cached per category ------
  function lines(ci) {
    if (lineCache[ci]) return lineCache[ci];
    var arr = Array.from(present[ci]), out = [], seen = {};
    arr.forEach(function (s, i) {
      var best = [];
      arr.forEach(function (t, j) { if (i !== j) best.push([dist(s.pos, t.pos), j]); });
      best.sort(function (a, b) { return a[0] - b[0]; });
      best.slice(0, 2).forEach(function (b, n) {
        if (n === 1 && b[0] > best[0][0] * 1.5) return;
        var k = i < b[1] ? i + ':' + b[1] : b[1] + ':' + i;
        if (!seen[k]) { seen[k] = 1; out.push([s, arr[b[1]]]); }
      });
    });
    lineCache[ci] = out;
    return out;
  }

  // ---- drawing -----------------------------------------------------------------
  var P = {}, Q = {}, hover = null, pinned = null, pointer = null, dragging = false, dirty = true;
  var ease = function (t) { return 1 - Math.pow(1 - t, 3); };

  function rgba(hex, a) {
    var h = hex.replace('#', '');
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    var n = parseInt(h, 16);
    return 'rgba(' + (n >> 16 & 255) + ',' + (n >> 8 & 255) + ',' + (n & 255) + ',' + a + ')';
  }
  function onscreen(p) { return p.x > -40 && p.x < W + 40 && p.y > -40 && p.y < H + 40; }

  function draw(now) {
    ctx.clearRect(0, 0, W, H);
    var i, j;
    var lw = Math.min(2, 0.8 + 0.3 * Z);      // lines thicken a little when zoomed

    // relations between categories
    ctx.lineWidth = 1;
    edges.forEach(function (e) {
      project(centres[e[0]], P); project(centres[e[1]], Q);
      var a = Math.min(P.a, Q.a) * 0.18;
      if (dormant.has(cats[e[0]].id) || dormant.has(cats[e[1]].id)) a *= 0.35;
      ctx.strokeStyle = rgba(COLOR.faint, a);
      ctx.beginPath(); ctx.moveTo(P.x, P.y); ctx.lineTo(Q.x, Q.y); ctx.stroke();
    });

    // sticks inside each constellation
    ctx.lineWidth = lw;
    for (i = 0; i < cats.length; i++) {
      if (present[i].size < 2) continue;
      var hl = hover && hover.ci === i;
      lines(i).forEach(function (e) {
        project(e[0].pos, P); project(e[1].pos, Q);
        if (!onscreen(P) && !onscreen(Q)) return;
        ctx.strokeStyle = rgba(hl ? COLOR.ink : COLOR.faint, Math.min(P.a, Q.a) * (hl ? 0.5 : 0.3));
        ctx.beginPath(); ctx.moveTo(P.x, P.y); ctx.lineTo(Q.x, Q.y); ctx.stroke();
      });
    }

    // tensions: a held contradiction, both sides kept
    ctx.setLineDash([3, 4]);
    tensions.forEach(function (tn) {
      project(tn.a.pos, P); project(tn.b.pos, Q);
      var age = Math.min(1, (now - tn.born) / 40000);
      ctx.strokeStyle = rgba(COLOR.held, Math.min(P.a, Q.a) * (0.8 - 0.45 * age));
      ctx.beginPath(); ctx.moveTo(P.x, P.y); ctx.lineTo(Q.x, Q.y); ctx.stroke();
    });
    ctx.setLineDash([]);

    // ghosts: retained parents, faint behind
    ghosts.forEach(function (g) {
      project(g.pos, P);
      if (!onscreen(P)) return;
      ctx.fillStyle = rgba(COLOR.faint, P.a * 0.35);
      ctx.beginPath(); ctx.arc(P.x, P.y, 1.4 * P.s, 0, 6.2832); ctx.fill();
    });

    // stars, far to near
    var order = stars.slice();
    order.forEach(function (st) { project(st.pos, P); st._z = P.z; });
    order.sort(function (a, b) { return a._z - b._z; });
    order.forEach(function (st) {
      // a merged parent sliding to the merge point
      if (st.slideTo) {
        var u = Math.min(1, (now - st.slideStart) / (reduced ? 1 : 520));
        st.pos = lerp3(st.slideFrom, st.slideTo, ease(u));
        if (u >= 1) {
          var g = [st.slideTo[0] + st.slideOffset[0], st.slideTo[1] + st.slideOffset[1], st.slideTo[2]];
          retire(st, g, now);
          return;
        }
        lineCache[st.ci] = null;
      }
      project(st.pos, P);
      if (!onscreen(P)) return;
      var r = (st.k === 's' ? 2.4 : 1.8) * P.s;
      var age = now - st.born;
      var pop = age < 700 ? 1 + 1.6 * (1 - age / 700) : 1;
      if (st.halo) {
        var ha = Math.max(0, 1 - (now - st.haloT) / 30000);
        if (ha > 0) {
          ctx.fillStyle = rgba(COLOR[st.halo], P.a * ha * 0.5);
          ctx.beginPath(); ctx.arc(P.x, P.y, r * (2.6 + pop), 0, 6.2832); ctx.fill();
        }
      }
      var isHover = st === hover || st === pinned;
      var inHl = hover && st.ci === hover.ci;
      ctx.fillStyle = rgba(COLOR.ink, P.a * (isHover ? 1 : inHl ? 0.98 : 0.88));
      ctx.beginPath(); ctx.arc(P.x, P.y, r * pop, 0, 6.2832); ctx.fill();
      if (st.revs > 0) { // a sharpened star carries a thin ring
        ctx.strokeStyle = rgba(COLOR.sharp, P.a * 0.65); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(P.x, P.y, r + 2.4, 0, 6.2832); ctx.stroke();
      }
      if (isHover) {
        ctx.strokeStyle = rgba(COLOR.ink, 0.9); ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.arc(P.x, P.y, r + 5, 0, 6.2832); ctx.stroke();
      }
    });

    // arrivals in flight and refusals falling away
    for (i = inflight.length - 1; i >= 0; i--) {
      var a = inflight[i];
      if (!a.landed) {
        var u2 = Math.min(1, (now - a.start) / a.dur);
        var pos = lerp3(a.from, a.to, ease(u2));
        project(pos, P);
        ctx.fillStyle = rgba(COLOR.ink, 0.95);
        ctx.beginPath(); ctx.arc(P.x, P.y, 2.2 * P.s, 0, 6.2832); ctx.fill();
        var back = lerp3(a.from, a.to, ease(Math.max(0, u2 - 0.06)));
        project(back, Q);
        ctx.strokeStyle = rgba(COLOR.ink, 0.35); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(Q.x, Q.y); ctx.lineTo(P.x, P.y); ctx.stroke();
        if (u2 >= 1) { a.landed = true; a.landedAt = now; land(a, now); }
        continue;
      }
      var since = now - a.landedAt;
      project(a.to, P);
      if (a.verdict === 'refused') {
        var f = Math.min(1, since / (reduced ? 1 : 900));
        var away = [a.to[0] * (1 + 0.35 * f), a.to[1] * (1 + 0.35 * f) - 0.12 * f, a.to[2] * (1 + 0.35 * f)];
        project(away, P);
        ctx.strokeStyle = rgba(COLOR.refused, 0.95 * (1 - f)); ctx.lineWidth = 1.4;
        ctx.beginPath(); ctx.arc(P.x, P.y, 3.2 * P.s, 0, 6.2832); ctx.stroke();
        if (f >= 1) inflight.splice(i, 1);
      } else {
        var f2 = Math.min(1, since / (reduced ? 1 : 650));
        ctx.strokeStyle = rgba(COLOR[a.verdict], 0.9 * (1 - f2)); ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(P.x, P.y, 4 + 26 * ease(f2), 0, 6.2832); ctx.stroke();
        if (f2 >= 1) inflight.splice(i, 1);
      }
    }

    // constellation names, near to far, skipping any that would overlap
    var fs = Math.round(Math.min(15, 12 + Z));
    ctx.font = fs + 'px ' + SANS; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    var labels = [];
    for (i = 0; i < cats.length; i++) {
      if (!present[i].size) continue;
      var cx = 0, cy = 0, cz = 0, top = Infinity, n = 0;
      present[i].forEach(function (st) { project(st.pos, P); cx += P.x; cy += P.y; cz += P.z; top = Math.min(top, P.y); n++; });
      labels.push({ i: i, x: cx / n, y: top - 8, z: cz / n, n: n });
    }
    labels.sort(function (a, b) { return b.z - a.z; });
    var boxes = [];
    labels.forEach(function (L) {
      var name = cats[L.i].name;
      var w = ctx.measureText(name).width + 10;
      var box = [L.x - w / 2, L.y - fs - 3, L.x + w / 2, L.y + 2];
      if (box[2] < 0 || box[0] > W || box[3] < 0 || box[1] > H) return;
      for (j = 0; j < boxes.length; j++) {
        var b = boxes[j];
        if (box[0] < b[2] && box[2] > b[0] && box[1] < b[3] && box[3] > b[1]) return;
      }
      // a name over another constellation's stars is worse than no name
      var tol = Z >= 2 ? 6 : (W < 600 ? 1 : 3);
      var covered = 0;
      for (j = 0; j < order.length && covered < tol; j++) {
        var o = order[j];
        if (o.ci === L.i) continue;
        project(o.pos, P);
        if (P.x > box[0] && P.x < box[2] && P.y > box[1] && P.y < box[3]) covered++;
      }
      if (covered >= tol) return;
      boxes.push(box);
      var fa = 0.3 + 0.7 * (L.z + 1) / 2;
      if (founded[L.i]) fa *= Math.min(1, (now - founded[L.i]) / 1400);
      var hl2 = hover && hover.ci === L.i;
      ctx.fillStyle = 'rgba(5,6,10,' + (0.6 * fa) + ')';
      ctx.fillRect(box[0], box[1] + 1, box[2] - box[0], box[3] - box[1] - 1);
      ctx.fillStyle = rgba(hl2 ? COLOR.ink : COLOR.faint, Math.min(1, fa * (hl2 ? 1 : 0.9)));
      ctx.fillText(name, L.x, L.y);
    });
  }

  // ---- hit testing and the tooltip -----------------------------------------
  function nearest(x, y) {
    var best = null, bd = 10 + 4 * Math.min(Z, 3);
    stars.forEach(function (st) {
      project(st.pos, P);
      var d = Math.hypot(P.x - x, P.y - y);
      if (d < bd) { bd = d; best = st; }
    });
    return best;
  }
  function nearestCategory(x, y) {
    var best = -1, bd = 220;
    for (var i = 0; i < cats.length; i++) {
      if (!present[i].size) continue;
      var cx = 0, cy = 0, n = 0;
      present[i].forEach(function (st) { project(st.pos, P); cx += P.x; cy += P.y; n++; });
      var d = Math.hypot(cx / n - x, cy / n - y);
      if (d < bd) { bd = d; best = i; }
    }
    return best;
  }
  function showTip(st, x, y) {
    if (!tip) return;
    var kind = KIND[st.k] || st.k;
    var how = st.via === 'sharp' ? 'A revision: it supersedes an earlier claim, kept faint behind it.'
      : st.via === 'merge' ? 'Merged from two claims; both parents kept faint behind it.'
      : st.via === 'held' ? 'Held: it contradicts a neighbour and the merge was refused, so both stay.'
      : st.via === 'new' ? 'Arrived as a new claim.' : 'In the sky at the start.';
    if (st.revs > 1) how += ' Sharpened ' + st.revs + ' times.';
    inspectContribution(st.text, kind + ' · ' + cats[st.ci].name + '. ' + how);
    tip.innerHTML = '';
    var k = document.createElement('span'); k.className = 'kind'; k.textContent = kind + ' \u00b7 ' + cats[st.ci].name;
    var t = document.createElement('p'); t.textContent = st.text;
    var h = document.createElement('span'); h.className = 'how'; h.textContent = how;
    tip.appendChild(k); tip.appendChild(t); tip.appendChild(h);
    tip.style.display = 'block';
    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var left = x + 16, topy = y + 14;
    if (left + tw > W - 8) left = x - tw - 12;
    if (topy + th > H - 8) topy = y - th - 12;
    tip.style.left = Math.max(6, left) + 'px'; tip.style.top = Math.max(6, topy) + 'px';
  }
  function hideTip() { if (tip) tip.style.display = 'none'; }

  // ---- interaction ---------------------------------------------------------------
  // One pointer: drag turns (shift-drag pans). Two pointers: pinch zooms at the
  // midpoint and the midpoint's movement pans. Tap without moving pins a star.
  var pointers = {}, last = null, moved = false, panning = false, pinch = null;
  function local(e) { var r = canvas.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; }
  function pinchState() {
    var ids = Object.keys(pointers);
    if (ids.length < 2) return null;
    var a = pointers[ids[0]], b = pointers[ids[1]];
    return { d: Math.hypot(a[0] - b[0], a[1] - b[1]), x: (a[0] + b[0]) / 2, y: (a[1] + b[1]) / 2 };
  }
  canvas.addEventListener('pointerdown', function (e) {
    pointers[e.pointerId] = local(e);
    canvas.setPointerCapture(e.pointerId);
    if (Object.keys(pointers).length === 2) { pinch = pinchState(); dragging = false; moved = true; return; }
    dragging = true; panning = e.shiftKey || e.button === 1 || e.button === 2;
    last = [e.clientX, e.clientY, performance.now()]; vYaw = vPitch = 0; moved = false;
    canvas.classList.add('dragging');
    e.preventDefault();
  });
  canvas.addEventListener('pointermove', function (e) {
    var pt = local(e);
    if (pointers[e.pointerId]) pointers[e.pointerId] = pt;
    pointer = pt;
    var ps = pinchState();
    if (ps && pinch) {
      if (pinch.d > 0) zoomAt(ps.x, ps.y, ps.d / pinch.d, false);
      ox += ps.x - pinch.x; oy += ps.y - pinch.y; clampPan();
      pinch = ps; hideTip(); hover = null; dirty = true;
      return;
    }
    if (dragging && last) {
      var dx = e.clientX - last[0], dy = e.clientY - last[1], dt = Math.max(1, performance.now() - last[2]);
      if (panning) { ox += dx; oy += dy; clampPan(); }
      else {
        yaw += dx * 0.006; pitch = Math.max(0.12, Math.min(1.35, pitch + dy * 0.006));
        vYaw = dx * 0.006 / dt * 16; vPitch = dy * 0.006 / dt * 16;
      }
      last = [e.clientX, e.clientY, performance.now()];
      hideTip(); hover = null;
      if (Math.abs(dx) + Math.abs(dy) > 2) moved = true;
    }
    dirty = true;
  });
  function endDrag(e) {
    delete pointers[e.pointerId];
    if (Object.keys(pointers).length < 2) pinch = null;
    if (!dragging) return;
    dragging = false; canvas.classList.remove('dragging');
    if (!moved && !panning && pointer) {
      var t = performance.now();
      if (lastTap && t - lastTap.t < 350 && Math.hypot(pointer[0] - lastTap.x, pointer[1] - lastTap.y) < 24) {
        lastTap = null; dive(pointer); // second tap in place: dive
      } else {
        lastTap = { t: t, x: pointer[0], y: pointer[1] };
        var st = nearest(pointer[0], pointer[1]);   // a single tap pins or unpins a star
        pinned = st === pinned ? null : st;
        if (pinned) showTip(pinned, pointer[0], pointer[1]); else hideTip();
      }
    }
    moved = false; panning = false;
    if (reduced) vYaw = vPitch = 0;
  }
  canvas.addEventListener('pointerup', endDrag);
  canvas.addEventListener('pointercancel', endDrag);
  canvas.addEventListener('pointerleave', function () { pointer = null; if (!pinned) { hover = null; hideTip(); } dirty = true; });
  canvas.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  canvas.addEventListener('dblclick', function (e) { e.preventDefault(); }); // handled from pointer events
  canvas.addEventListener('wheel', function (e) {
    var pt = local(e);
    var factor = Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0018));
    zoomAt(pt[0], pt[1], factor, false);
    e.preventDefault();
  }, { passive: false });
  // Dive: zoom 3x into the constellation under the point and centre it. Past
  // 70% of the maximum a second dive returns to the whole sky.
  function dive(pt) {
    var st = nearest(pt[0], pt[1]);
    var ci = st ? st.ci : nearestCategory(pt[0], pt[1]);
    if (Z > ZMAX * 0.7) { resetView(true); return; }
    if (ci < 0) { zoomAt(pt[0], pt[1], 2.2, true); return; }
    var cx = 0, cy = 0, n = 0;
    present[ci].forEach(function (s) { project(s.pos, P); cx += P.x; cy += P.y; n++; });
    zoomAt(cx / n, cy / n, 3, true);
    if (tween) { tween.x1 += W / 2 - cx / n; tween.y1 += H / 2 - cy / n; }
    else { ox += W / 2 - cx / n; oy += H / 2 - cy / n; clampPan(); }
    pinned = null; hideTip();
  }
  // Detected from pointer events rather than the dblclick event: a canvas with
  // touch-action none gets no dblclick from a double tap on most mobile browsers.
  var lastTap = null;
  canvas.addEventListener('keydown', function (e) {
    var step = 0.08, pan = 40;
    if (e.key === 'ArrowLeft') { if (e.shiftKey) ox -= pan; else yaw -= step; }
    else if (e.key === 'ArrowRight') { if (e.shiftKey) ox += pan; else yaw += step; }
    else if (e.key === 'ArrowUp') { if (e.shiftKey) oy -= pan; else pitch = Math.max(0.12, pitch - step); }
    else if (e.key === 'ArrowDown') { if (e.shiftKey) oy += pan; else pitch = Math.min(1.35, pitch + step); }
    else if (e.key === '+' || e.key === '=') zoomAt(W / 2, H / 2, 1.25, true);
    else if (e.key === '-' || e.key === '_') zoomAt(W / 2, H / 2, 0.8, true);
    else if (e.key === '0' || e.key === 'Home') resetView(true);
    else return;
    clampPan(); dirty = true; e.preventDefault();
  });
  if (pauseBtn) pauseBtn.addEventListener('click', function () {
    paused = !paused;
    pauseBtn.textContent = paused ? 'Resume' : 'Pause';
    pauseBtn.setAttribute('aria-pressed', paused ? 'true' : 'false');
    if (!paused) nextAt = performance.now() + 400;
  });
  if (resetBtn) resetBtn.addEventListener('click', function () { reset(); pinned = null; hideTip(); resetView(true); nextAt = performance.now() + 1200; });
  var zin = document.getElementById('sky-zoom-in'), zout = document.getElementById('sky-zoom-out'), zfit = document.getElementById('sky-fit');
  if (zin) zin.addEventListener('click', function () { zoomAt(W / 2, H / 2, 1.6, true); });
  if (zout) zout.addEventListener('click', function () { zoomAt(W / 2, H / 2, 1 / 1.6, true); });
  if (zfit) zfit.addEventListener('click', function () { resetView(true); });
  document.addEventListener('visibilitychange', function () { if (!document.hidden) nextAt = performance.now() + 800; });
  window.addEventListener('resize', resize);

  // ---- main loop ---------------------------------------------------------------
  var prev = performance.now();
  function frame(now) {
    var dt = Math.min(50, now - prev); prev = now;
    var animating = inflight.length > 0 || !!tween || stars.some(function (s) { return s.slideTo || now - s.born < 800 || (s.halo && now - s.haloT < 30000); });

    if (tween) {
      var u = Math.min(1, (now - tween.t0) / tween.dur), k = ease(u);
      Z = tween.z0 + (tween.z1 - tween.z0) * k; ox = tween.x0 + (tween.x1 - tween.x0) * k; oy = tween.y0 + (tween.y1 - tween.y0) * k;
      if (tween.yaw1 !== undefined) { yaw = tween.yaw0 + (tween.yaw1 - tween.yaw0) * k; pitch = tween.pitch0 + (tween.pitch1 - tween.pitch0) * k; }
      if (u >= 1) tween = null;
      showZoom(); dirty = true;
    }
    if (!dragging && !pinch) {
      if (Math.abs(vYaw) > 1e-4 || Math.abs(vPitch) > 1e-4) {
        yaw += vYaw; pitch = Math.max(0.12, Math.min(1.35, pitch + vPitch));
        vYaw *= 0.93; vPitch *= 0.93; dirty = true;
      } else if (!paused && !reduced && !pinned && Z < 1.3 && !tween) {
        yaw += 0.00004 * dt; dirty = true; // a slow idle turn about the vertical, only when not zoomed in
      }
    }
    if (!paused && !document.hidden && now >= nextAt) {
      arrive(now);
      // exponential inter-arrival, mean 2.1 s, clamped; one in eight is a burst
      var gap = -Math.log(1 - Math.random()) * 2100;
      if (Math.random() < 0.125) gap = 300 + Math.random() * 250;
      nextAt = now + Math.max(280, Math.min(6500, gap)) * (reduced ? 1.8 : 1);
    }
    if (pointer && !dragging && !pinned && !pinch) {
      var h = nearest(pointer[0], pointer[1]);
      if (h !== hover) { hover = h; if (h) showTip(h, pointer[0], pointer[1]); else hideTip(); dirty = true; }
    }
    if (dirty || animating) { draw(now); dirty = false; }
    requestAnimationFrame(frame);
  }

  resize();
  pitch = HOME.pitch;
  reset();
  showZoom();
  nextAt = performance.now() + 1400;
  requestAnimationFrame(frame);
})();
