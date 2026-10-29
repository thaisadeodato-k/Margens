// Busca e download de pacotes SIG do RIGeo (Serviço Geológico do Brasil), API do DSpace 7.
// Rodar no console de https://rigeo.sgb.gov.br/
const q = 'Colatina';
const j = await (await fetch('/server/api/discover/search/objects?query=' + encodeURIComponent(q) + '&size=40')).json();
const itens = j._embedded.searchResult._embedded.objects.map(o => o._embedded.indexableObject)
  .map(o => ({ nome: o.name, data: (o.metadata['dc.date.issued'] || [{}])[0].value, handle: o.handle, uuid: o.uuid }));
// Arquivos de um item:
async function arquivos(uuid) {
  const b = await (await fetch('/server/api/core/items/' + uuid + '/bundles')).json(); const out = [];
  for (const bd of b._embedded.bundles) { if (bd.name !== 'ORIGINAL') continue;
    const bs = await (await fetch(bd._links.bitstreams.href)).json();
    for (const x of bs._embedded.bitstreams) out.push({ nome: x.name, kb: Math.round(x.sizeBytes / 1024), uuid: x.uuid }); }
  return out;
}
// Download de um arquivo: fetch('/server/api/core/bitstreams/' + uuid + '/content')
// Itens usados:
//  Pedreiras (2012)  handle doc/19860 · sig_pedreiras_ma_risco_2012.zip
//  Trizidela (2012)  handle doc/19866 · sig_trizideladovale_ma_risco_2012.zip
//  Colatina setorização (2019)  doc/19463.2 · sig_colatina_es_risco_revisita_2019.zip
//  Colatina planície de inundação (2016)  doc/24362 · colatina_SIG.zip (manchas das cheias de 1979 e 1997)
itens;
