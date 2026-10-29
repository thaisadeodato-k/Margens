// Ruas, rio, escolas e hospital do OpenStreetMap via Overpass API (usado em Pedreiras).
// Pode rodar em qualquer página. Em horários de pico o Overpass responde 502 ("all query workers are busy");
// nesse caso, tentar mais tarde ou usar overture_camadas.js.
const bb = '(-4.605,-44.645,-4.530,-44.570)'; // S, W, N, E
const q = `[out:json][timeout:90];(way["highway"]${bb};way["waterway"]${bb};way["natural"="water"]${bb};relation["natural"="water"]${bb};` +
  `way["building"]${bb};node["place"]${bb};node["amenity"~"school|hospital|clinic"]${bb};way["amenity"~"school|hospital"]${bb};);out geom;`;
const j = await (await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q) })).json();
const rd = p => [+p.lon.toFixed(6), +p.lat.toFixed(6)];
const out = j.elements.map(e => { const o = { t: e.type[0], id: e.id, g: e.tags || {} };
  if (e.lat) o.c = rd(e); if (e.geometry) o.c = e.geometry.map(rd);
  if (e.members) o.m = e.members.filter(m => m.geometry).map(m => ({ r: m.role, c: m.geometry.map(rd) })); return o; });
window.__osm = btoa(unescape(encodeURIComponent(JSON.stringify(out))));
({ n: out.length, b64: window.__osm.length });
