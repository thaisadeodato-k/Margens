// Ruas, rios e escolas/hospitais do Overture Maps (release 2026-09-23), para Colatina.
// Rodar numa página com pmtiles.js. Usa o mesmo leitor MVT (R, packed, val, td) de overture_edificacoes.js:
// cole aquelas funções antes deste trecho.
async function dump(theme, z, layers, keep, filter) {
  const P = new pmtiles.PMTiles(`https://tiles.overturemaps.org/2026-09-23.0/${theme}.pmtiles`);
  const k = 2 ** (14 - z), X0 = 6339, Y0 = 9096;
  const tx0 = Math.floor(X0 / k), tx1 = Math.floor((X0 + 6) / k), ty0 = Math.floor(Y0 / k), ty1 = Math.floor((Y0 + 4) / k);
  const feats = [], seen = new Set();
  for (let tx = tx0; tx <= tx1; tx++) for (let ty = ty0; ty <= ty1; ty++) {
    const t = await P.getZxy(z, tx, ty); if (!t) continue; let buf = new Uint8Array(t.data);
    if (buf[0] === 0x1f && buf[1] === 0x8b) buf = new Uint8Array(await new Response(new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
    const r = new R(buf);
    while (r.p < buf.length) { const kk = r.v(); if ((kk >> 3) !== 3) { r.skip(kk & 7); continue; }
      const lb = r.bytes(), L = new R(lb); let name = '', ext = 4096; const fs = [], keys = [], vals = [];
      while (L.p < lb.length) { const q = L.v(), f = q >> 3, w = q & 7; if (f === 1) name = td.decode(L.bytes()); else if (f === 2) fs.push(L.bytes()); else if (f === 3) keys.push(td.decode(L.bytes())); else if (f === 4) vals.push(val(L.bytes())); else if (f === 5) ext = L.v(); else L.skip(w); }
      if (!layers.includes(name)) continue;
      for (const fb of fs) { const F = new R(fb); let tags = [], geom = [], type = 0;
        while (F.p < fb.length) { const q = F.v(), f = q >> 3, w = q & 7; if (f === 2) tags = packed(F.bytes()); else if (f === 3) type = F.v(); else if (f === 4) geom = packed(F.bytes()); else F.skip(w); }
        const p = {}; for (let i = 0; i < tags.length; i += 2) p[keys[tags[i]]] = vals[tags[i + 1]];
        if (filter && !filter(p)) continue;
        const key = (p.id || '') + '|' + tx + '|' + ty; if (seen.has(key)) continue; seen.add(key);
        let cx = 0, cy = 0, i = 0, part = [], parts = [];
        const P2 = (ax, ay) => [Math.round(((tx * k - X0) * 256 + ax / ext * 256 * k) * 10) / 10, Math.round(((ty * k - Y0) * 256 + ay / ext * 256 * k) * 10) / 10];
        while (i < geom.length) { const ci = geom[i++], cmd = ci & 7, cnt = ci >> 3;
          if (cmd === 1 || cmd === 2) { for (let j = 0; j < cnt; j++) { const dx = geom[i++], dy = geom[i++]; cx += (dx >>> 1) ^ -(dx & 1); cy += (dy >>> 1) ^ -(dy & 1); if (cmd === 1 && part.length) { parts.push(part); part = []; } part.push(P2(cx, cy)); } }
          else if (cmd === 7) { parts.push(part); part = []; } }
        if (part.length) parts.push(part);
        const o = { ty: type, g: parts }; for (const kk of keep) if (p[kk] != null) o[kk] = p[kk]; feats.push(o); } }
  }
  return feats;
}
const seg = await dump('transportation', 14, ['segment'], ['class', '@name'], p => p.subtype === 'road');
const wat = (await dump('base', 13, ['water'], ['class', 'subtype', '@name'])).filter(w => w.subtype !== 'stream');
const pl = await dump('places', 14, ['place'], ['basic_category', '@name', 'confidence'],
  p => /elementary_school|middle_school|high_school|preschool|^school$|specialty_school|hospital|college_university/.test(p.basic_category || ''));
// compactar e ler em fatias como nos outros scripts
const js = new TextEncoder().encode(JSON.stringify({ seg, wat, pl }));
const gz = new Uint8Array(await new Response(new Blob([js]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
let s = ''; for (let i = 0; i < gz.length; i += 8192) s += String.fromCharCode.apply(null, gz.subarray(i, i + 8192));
window.__ov = btoa(s);
({ seg: seg.length, wat: wat.length, pl: pl.length, b64: window.__ov.length });
