# Pipeline

Ordem de execução para uma cidade:

1. **`01_obter/`** — scripts de navegador que baixam e recortam relevo (ANADEM), construções e camadas (Overture/OSM),
   setores e manchas da SGB, e as séries da ANA. Ver `01_obter/README.md`.
2. **Decodificar** os pacotes base64 em Python e levar tudo para a grade da cidade (relevo reamostrado por bilinear
   da grade geográfica do ANADEM para a grade Web Mercator z14). Saídas intermediárias: `dem.npy`, `bld.npy`, `ov.json`/`osm.json`.
3. **`02_modelo/`**
   - `*_modelo.py`: máscara do rio, superfície de referência do rio, altura acima do rio e **preenchimento conectado**
     (reconstrução morfológica por erosão a partir do rio), resultando em `spill.npy`: para cada pixel, quantos metros
     acima do rio a água precisa subir para chegar ali. Também cobre os setores da SGB e, em Colatina, ajusta o nível
     à mancha real de 1997 (IoU dentro do corredor que a SGB mapeou).
   - `*_cotas.py`: lê o CSV do HidroWeb e gera a série diária e os máximos anuais.
4. **`03_pagina/`** — gera o JSON da cidade usado pelo site: relevo sombreado (JPEG), limiar de cada pixel (PNG 8 bits),
   rio, ruas, escolas/hospitais, setores, curvas (área urbana e ruas por nível), construções (contornos, limiar, área),
   calibração `R0` e máximos anuais. O bloco `cfg` (textos, eventos da régua, faixa da régua) é editado à mão.
5. Copiar para `site/data/<cidade>.json` e acrescentar a cidade em `site/data/cities.json`.

**Atenção:** os scripts ainda usam caminhos absolutos da pasta de trabalho do ambiente de nuvem
(`/root/work`, `/root/col`, `/home/claude/work`). Os intermediários `.npy` não vão para o Git (são grandes e
regeráveis). Próximo passo técnico: um único `config` por cidade e caminhos relativos.

Dependências Python: numpy, scipy, scikit-image, geopandas, pyogrio, pyproj, pandas, pillow.
