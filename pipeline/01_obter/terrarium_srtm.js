// Relevo SRTM via AWS Terrain Tiles (formato Terrarium), z14 4×4 blocos sobre Pedreiras.
// Usado só na primeira versão (substituído pelo ANADEM). Mantido para reprodutibilidade da comparação.
const z = 14, x0 = 6160, y0 = 8398, nx = 4, ny = 4;
const cv = document.createElement('canvas'); cv.width = nx * 256; cv.height = ny * 256;
const ctx = cv.getContext('2d', { willReadFrequently: true });
await Promise.all([...Array(nx * ny).keys()].map(async i => { const tx = x0 + i % nx, ty = y0 + Math.floor(i / nx);
  const r = await fetch(`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${tx}/${ty}.png`);
  ctx.drawImage(await createImageBitmap(await r.blob()), (tx - x0) * 256, (ty - y0) * 256); }));
const d = ctx.getImageData(0, 0, cv.width, cv.height).data, n = cv.width * cv.height, u = new Uint16Array(n);
for (let i = 0; i < n; i++) u[i] = Math.max(0, Math.round(((d[4 * i] * 256 + d[4 * i + 1] + d[4 * i + 2] / 256) - 32768) * 10)); // decímetros
// diferença por linha + gzip para comprimir melhor
const dl = new Int16Array(n); for (let i = 0; i < n; i++) dl[i] = (i % cv.width === 0) ? u[i] : u[i] - u[i - 1];
const gz = new Uint8Array(await new Response(new Blob([dl.buffer]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());
let s = ''; for (let i = 0; i < gz.length; i += 8192) s += String.fromCharCode.apply(null, gz.subarray(i, i + 8192));
window.__dem = btoa(s);
({ b64: window.__dem.length });
