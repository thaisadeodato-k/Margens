# 01 · Obter os dados

Os dados de origem vêm de servidores públicos que o ambiente de processamento (nuvem) não alcança diretamente.
Por isso foram baixados **pelo navegador** (o painel de navegador do app do Claude, no computador da Thais):
cada script abaixo roda no console de uma página do próprio site de origem (mesma origem, sem bloqueio de CORS),
recorta só a área da cidade e devolve o resultado em base64.

Como o canal entre o navegador e o ambiente de processamento corta respostas acima de ~250 mil caracteres,
o resultado é guardado numa variável `window.__x` e lido em fatias de ~200–230 mil caracteres
(`'<<' + window.__x.slice(a, b) + '>>'`), depois remontado e decodificado em Python.

| Script | Onde rodar (página aberta) | O que faz |
|---|---|---|
| `anadem_recorte.js` | `https://metadados.snirh.gov.br/geonetwork/srv/por/catalog.search` | Lê o GeoTIFF do ANADEM (COG, 1,6 GB) por pedaços (HTTP Range) e recorta a janela da cidade em cm (uint16, gzip). |
| `overture_edificacoes.js` | qualquer página com `pmtiles.js` carregado (ex.: thaisadeodato-k.github.io/camadas-sp) | Lê os blocos z14 do `buildings.pmtiles` do Overture, decodifica o MVT e exporta os contornos em coordenadas da grade da cidade. |
| `overture_camadas.js` | idem | Ruas (`transportation`), rios (`base/water`) e escolas/hospitais (`places`) do Overture. Usado em Colatina quando o Overpass (OSM) estava sobrecarregado. |
| `osm_overpass.js` | qualquer página | Ruas, rio, escolas e hospital pelo Overpass API (usado em Pedreiras). |
| `terrarium_srtm.js` | qualquer página | Relevo SRTM (AWS Terrain Tiles). Usado só na primeira versão de Pedreiras; substituído pelo ANADEM. |
| `sgb_rigeo.js` | `https://rigeo.sgb.gov.br/...` | Lista e baixa os pacotes SIG de um item do RIGeo (SGB) pela API do DSpace. |
| `hidroweb.md` | `https://www.snirh.gov.br/hidroweb/serieshistoricas` | Passo a passo para baixar as séries de cotas pela própria interface do HidroWeb. |

## Grade de cada cidade

Todas as camadas são levadas para uma grade em Web Mercator alinhada aos blocos z14 (256 px por bloco, ~9 m por pixel):

| Cidade | Blocos z14 (x, y) | Grade |
|---|---|---|
| Pedreiras | x 6160–6163, y 8398–8401 | 1024 × 1024 |
| Colatina | x 6339–6345, y 9096–9100 | 1792 × 1280 |

Pixel `(px, py)` → `lon = (px + X0·256) / (256·2^14) · 360 − 180`; `lat = atan(sinh(π − 2π·(py + Y0·256)/(256·2^14)))`.
