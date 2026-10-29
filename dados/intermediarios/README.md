# Intermediários

Recortes já levados para a grade de cada cidade (ver `pipeline/01_obter/README.md`), para não precisar baixar de novo.

- `*_relevo_*_grade.npz` — relevo em metros (float32), chave `dem`. Pedreiras 1024×1024, Colatina 1280×1792.
- `pedreiras_osm.json.gz` — ruas, rio, escolas e hospital (Overpass, 28/10/2026).
- `colatina_overture_camadas.json.gz` — ruas (`seg`), rios (`wat`) e escolas/hospitais (`pl`) do Overture, 29/10/2026.

As construções e o limiar de água de cada pixel já estão nos arquivos de `site/data/`.
