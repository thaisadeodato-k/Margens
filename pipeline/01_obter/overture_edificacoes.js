// Contornos de construções do Overture Maps (buildings.pmtiles, release 2026-09-23).
// Rodar numa página que já carregue pmtiles.js (ex.: https://thaisadeodato-k.github.io/camadas-sp/).
// Saída binária (gzip + base64): [uint32 nb, uint32 nv][uint8 altura×4 por prédio][uint16 vértices]
// vértices: para cada anel, n seguido de n pares (px·16, py·16) na grade da cidade.
const P = new pmtiles.PMTiles('https://tiles.overturemaps.org/2026-09-23.0/buildings.pmtiles');
const z = 14, x0 = 6339, y0 = 9096, NX = 7, NY = 5; // Colatina; Pedreiras: x0=6160, y0=8398, NX=4, NY=4

// --- leitor mínimo de protobuf / Mapbox Vector Tile ---
function R(buf) { this.b = buf; this.p = 0; }
R.prototype.v = function () { let r = 0, s = 0, c; do { c = this.b[this.p++]; r += (c & 0x7f) * Math.pow(2, s); s += 7; } while (c & 0x80); return r; };
R.prototype.bytes = function () { const n = this.v(); const o = this.b.subarray(this.p, this.p + n); this.p += n; return o; };
R.prototype.skip = function (w) { if (w === 0) this.v(); else if (w === 1) this.p += 8; else if (w === 2) { const n = this.v(); this.p += n; } else if (w === 5) this.p += 4; };
const td = new TextDecoder(), packed = b => { const r = new R(b), o = []; while (r.p < b.length) o.push(r.v()); return o; };
function val(b) { const r = new R(b); let out = null; while (r.p < b.length) { const k = r.v(), f = k >> 3, w = k & 7;
  if (f === 1) out = td.decode(r.bytes()); else if (f === 2) { out = new DataView(b.buffer, b.byteOffset + r.p, 4).getFloat32(0, true); r.p += 4; }
  else if (f === 3) { out = new DataView(b.buffer, b.byteOffset + r.p, 8).getFloat64(0, true); r.p += 8; } else if (f === 4 || f === 5) out = r.v();
  else if (f === 6) { const n = r.v(); out = (n % 2) ? -(n + 1) / 2 : n / 2; } else if (f === 7) out = !!r.v(); else r.skip(w); } return out; }

const verts = [], meta = [], src = {}, seen = new Set(); let nb = 0;
for (let tx = x0; tx < x0 + NX; tx++) for (let ty = y0; ty < y0 + NY; ty++) {
  const t = await P.getZxy(z, tx, ty); if (!t) continue; let buf = new Uint8Array(t.data);
  if (buf[0] === 0x1f && buf[1] === 0x8b) buf = new Uint8Array(await new Response(new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
  const r = new R(buf);
  while (r.p < buf.length) { const k = r.v(); if ((k >> 3) !== 3) { r.skip(k & 7); continue; }
    const lb = r.bytes(), L = new R(lb); let name = '', ext = 4096; const feats = [], keys = [], vals = [];
    while (L.p < lb.length) { const kk = L.v(), f = kk >> 3, w = kk & 7; if (f === 1) name = td.decode(L.bytes()); else if (f === 2) feats.push(L.bytes()); else if (f === 3) keys.push(td.decode(L.bytes())); else if (f === 4) vals.push(val(L.bytes())); else if (f === 5) ext = L.v(); else L.skip(w); }
    if (name !== 'building') continue;
    for (const fb of feats) { const F = new R(fb); let tags = [], geom = [], type = 0;
      while (F.p < fb.length) { const kk = F.v(), f = kk >> 3, w = kk & 7; if (f === 2) tags = packed(F.bytes()); else if (f === 3) type = F.v(); else if (f === 4) geom = packed(F.bytes()); else F.skip(w); }
      if (type !== 3) continue; const p = {}; for (let i = 0; i < tags.length; i += 2) p[keys[tags[i]]] = vals[tags[i + 1]];
      if (p.id) { if (seen.has(p.id)) continue; seen.add(p.id); }        // o mesmo prédio aparece em blocos vizinhos
      let cx = 0, cy = 0, i = 0, ring = [], rings = [];
      while (i < geom.length) { const ci = geom[i++], cmd = ci & 7, cnt = ci >> 3;
        if (cmd === 1 || cmd === 2) { for (let j = 0; j < cnt; j++) { const dx = geom[i++], dy = geom[i++]; cx += (dx >>> 1) ^ -(dx & 1); cy += (dy >>> 1) ^ -(dy & 1); if (cmd === 1 && ring.length) { rings.push(ring); ring = []; } ring.push([cx, cy]); } }
        else if (cmd === 7) { rings.push(ring); ring = []; } }
      if (ring.length) rings.push(ring);
      const hh = p.height != null ? +p.height : (p.num_floors != null ? p.num_floors * 3 : 0);
      for (const rg of rings) { let a = 0; for (let j = 0; j < rg.length; j++) { const [x1, y1] = rg[j], [x2, y2] = rg[(j + 1) % rg.length]; a += x1 * y2 - x2 * y1; }
        if (a <= 0 || rg.length < 3) continue; // só anéis externos
        verts.push(rg.length); for (const [ax, ay] of rg) { verts.push(Math.round(((tx - x0) * 256 + ax / ext * 256) * 16), Math.round(((ty - y0) * 256 + ay / ext * 256) * 16)); }
        meta.push(Math.min(255, Math.round(hh * 4))); nb++; }
      const s = p['@geometry_source'] || '?'; src[s] = (src[s] || 0) + 1; } }
}
const gz = new Uint8Array(await new Response(new Blob([new Uint32Array([nb, verts.length]).buffer, new Uint8Array(meta).buffer, new Uint16Array(verts).buffer]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
let s = ''; for (let i = 0; i < gz.length; i += 8192) s += String.fromCharCode.apply(null, gz.subarray(i, i + 8192));
window.__bld = btoa(s);
({ nb, src, b64: window.__bld.length });
