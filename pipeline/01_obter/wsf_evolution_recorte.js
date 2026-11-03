// Recorte do WSF Evolution (DLR) para a janela de uma cidade: ano em que cada pixel de ~30 m foi detectado como área
// construída pela primeira vez (1985–2015; 1985 = já ocupado no início da série; 0 = não detectado).
// Rodar no console de qualquer página de https://download.geoservice.dlr.de/ (mesma origem do arquivo), por exemplo a
// miniatura do bloco: https://download.geoservice.dlr.de/WSF_EVO/files/WSFevolution_v1_-42_-20/WSFevolution_v1_-42_-20_thumbnail.png
// Blocos de 2° × 2°, nomeados pelo canto sudoeste (STAC: https://geoservice.dlr.de/eoc/ogc/stac/v1/collections/WSF_Evolution).
// Colatina = WSFevolution_v1_-42_-20 (1,3 MB). O GeoTIFF é int32, LZW, blocos de 512 × 512, EPSG:4326.
const U = '/WSF_EVO/files/WSFevolution_v1_-42_-20/WSFevolution_v1_-42_-20.tif';               // trocar por cidade
const BB = { W: -40.71533203125, E: -40.5615234375, N: -19.476950206488418, S: -19.58049347920253 }; // grade da cidade (bounds do site)

const raw = new Uint8Array(await (await fetch(U)).arrayBuffer()); const dv = new DataView(raw.buffer);
const ifd = dv.getUint32(4, true), n = dv.getUint16(ifd, true), T = {};
for (let i = 0; i < n; i++) { const o = ifd + 2 + i * 12; T[dv.getUint16(o, true)] = { cnt: dv.getUint32(o + 4, true), v: dv.getUint32(o + 8, true), o }; }
const W = dv.getUint16(T[256].o + 8, true), TW = 512, across = Math.ceil(W / TW);
const res = dv.getFloat64(T[33550].v, true), lon0 = dv.getFloat64(T[33922].v + 24, true), lat0 = dv.getFloat64(T[33922].v + 32, true);
function lzw(src) { // LZW do TIFF (bits mais significativos primeiro)
  const out = []; let dict = [], bits = 9, pos = 0, prev = null;
  const reset = () => { dict = []; for (let i = 0; i < 256; i++) dict[i] = [i]; dict[256] = null; dict[257] = null; bits = 9; };
  const read = () => { let v = 0; for (let k = 0; k < bits; k++) { const by = src[pos >> 3]; v = (v << 1) | ((by >> (7 - (pos & 7))) & 1); pos++; } return v; };
  reset();
  while (pos + bits <= src.length * 8) {
    const c = read(); if (c === 257) break;
    if (c === 256) { reset(); prev = null; continue; }
    const e = c < dict.length && dict[c] ? dict[c] : prev.concat([prev[0]]);
    for (const x of e) out.push(x);
    if (prev) dict.push(prev.concat([e[0]]));
    prev = e;
    if (dict.length + 1 >= (1 << bits) && bits < 12) bits++;
  }
  return new Uint8Array(out);
}
const c0 = Math.floor((BB.W - lon0) / res) - 2, c1 = Math.ceil((BB.E - lon0) / res) + 2, r0 = Math.floor((lat0 - BB.N) / res) - 2, r1 = Math.ceil((lat0 - BB.S) / res) + 2;
const w = c1 - c0, h = r1 - r0, out = new Uint8Array(w * h); let nz = 0;
for (let tr = Math.floor(r0 / TW); tr <= Math.floor((r1 - 1) / TW); tr++) for (let tc = Math.floor(c0 / TW); tc <= Math.floor((c1 - 1) / TW); tc++) {
  const idx = tr * across + tc, off = dv.getUint32(T[324].v + idx * 4, true), cnt = dv.getUint32(T[325].v + idx * 4, true);
  const iv = new Int32Array(lzw(raw.subarray(off, off + cnt)).buffer, 0, TW * TW);
  for (let y = 0; y < TW; y++) { const gr = tr * TW + y; if (gr < r0 || gr >= r1) continue;
    for (let x = 0; x < TW; x++) { const gc = tc * TW + x; if (gc < c0 || gc >= c1) continue;
      const yv = iv[y * TW + x], u = yv >= 1985 && yv <= 2015 ? yv - 1984 : 0; out[(gr - r0) * w + (gc - c0)] = u; if (u) nz++; } }
}
const gz = new Uint8Array(await new Response(new Blob([out]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
let s = ''; for (let i = 0; i < gz.length; i += 8192) s += String.fromCharCode.apply(null, gz.subarray(i, i + 8192));
window.__wsf = btoa(s); // ler com '<<' + window.__wsf + '>>' (Colatina: 15 mil caracteres, cabe numa resposta)
({ c0, r0, w, h, res, lon0, lat0, nz, b64: window.__wsf.length }); // Colatina: c0 4802, r0 5516, 576 × 389, nz 16797
