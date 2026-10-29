// Recorte do ANADEM v1 (ANA/UFRGS) para a janela de uma cidade.
// Rodar no console de https://metadados.snirh.gov.br/ (mesma origem dos arquivos).
// Arquivos por zona MGRS: Pedreiras = anadem_v1_23M.tif, Colatina = anadem_v1_24K.tif
// O GeoTIFF é um COG: float32, deflate, blocos 512×512, EPSG:4326, nodata −9999.
const U = '/files/anadem_v1_tiles/anadem_v1_24K.tif';          // trocar por cidade
const BBOX = { W: -40.705, E: -40.575, N: -19.475, S: -19.575 }; // trocar por cidade

const rng = async (a, n) => await (await fetch(U, { headers: { Range: `bytes=${a}-${a + n - 1}` } })).arrayBuffer();
let dv = new DataView(await rng(0, 262144));
const ifd = dv.getUint32(4, true), n = dv.getUint16(ifd, true), T = {}, TS = { 1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 11: 4, 12: 8, 16: 8 };
for (let i = 0; i < n; i++) {
  const o = ifd + 2 + i * 12, tag = dv.getUint16(o, true), typ = dv.getUint16(o + 2, true), cnt = dv.getUint32(o + 4, true);
  T[tag] = { typ, cnt, vo: (TS[typ] || 1) * cnt <= 4 ? o + 8 : dv.getUint32(o + 8, true) };
}
const v = (t, k = 0) => { const { typ, vo } = T[t]; return typ === 3 ? dv.getUint16(vo + k * 2, true) : typ === 4 ? dv.getUint32(vo + k * 4, true) : dv.getFloat64(vo + k * 8, true); };
const W = v(256), TWd = v(322), res = v(33550, 0), lon0 = v(33922, 3), lat0 = v(33922, 4), across = Math.ceil(W / TWd);
const offs = new DataView(await rng(T[324].vo, T[324].cnt * 4)), cnts = new DataView(await rng(T[325].vo, T[325].cnt * 4));
const c0 = Math.floor((BBOX.W - lon0) / res), c1 = Math.ceil((BBOX.E - lon0) / res), r0 = Math.floor((lat0 - BBOX.N) / res), r1 = Math.ceil((lat0 - BBOX.S) / res);
const w = c1 - c0, h = r1 - r0, out = new Float32Array(w * h).fill(NaN);
for (let tr = Math.floor(r0 / TWd); tr <= Math.floor((r1 - 1) / TWd); tr++) for (let tc = Math.floor(c0 / TWd); tc <= Math.floor((c1 - 1) / TWd); tc++) {
  const idx = tr * across + tc;
  const dec = new Float32Array(await new Response(new Blob([await rng(offs.getUint32(idx * 4, true), cnts.getUint32(idx * 4, true))]).stream().pipeThrough(new DecompressionStream('deflate'))).arrayBuffer());
  for (let y = 0; y < TWd; y++) { const gr = tr * TWd + y; if (gr < r0 || gr >= r1) continue;
    for (let x = 0; x < TWd; x++) { const gc = tc * TWd + x; if (gc < c0 || gc >= c1) continue; out[(gr - r0) * w + (gc - c0)] = dec[y * TWd + x]; } }
}
const u = new Uint16Array(w * h); for (let i = 0; i < w * h; i++) u[i] = out[i] > -1000 ? Math.round(out[i] * 100) : 0; // centímetros
const gz = new Uint8Array(await new Response(new Blob([u.buffer]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
let s = ''; for (let i = 0; i < gz.length; i += 8192) s += String.fromCharCode.apply(null, gz.subarray(i, i + 8192));
window.__ana = btoa(s);
({ c0, r0, w, h, res, lon0, lat0, b64: window.__ana.length }); // guardar c0, r0, res, lon0, lat0 para reamostrar em Python
