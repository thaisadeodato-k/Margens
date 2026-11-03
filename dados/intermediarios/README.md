# Intermediários

Recortes já levados para a grade de cada cidade (ver `pipeline/01_obter/README.md`), para não precisar baixar de novo.

- `*_relevo_*_grade.npz` — relevo em metros (float32), chave `dem`. Pedreiras 1024×1024, Colatina 1280×1792.
- `pedreiras_osm.json.gz` — ruas, rio, escolas e hospital (Overpass, 28/10/2026).
- `colatina_overture_camadas.json.gz` — ruas (`seg`), rios (`wat`) e escolas/hospitais (`pl`) do Overture, 29/10/2026.

- `colatina_alturas_iema.npz` — para cada construção de Colatina (mesma ordem do site): `med` e `p75` de MDE − MDT do
  IEMA dentro do contorno (m) e `npx` (pixels de 2,4 m usados).

- `<cidade>_wsf_evolution.b64` — recorte do WSF Evolution (gzip + base64 de uint8, valor = ano − 1984, 0 = não
  detectado). Parâmetros de cada recorte em `CFG`, no início de `pipeline/02_modelo/ocupacao_wsf.py`.
- `<cidade>_ocupacao_wsf.npz` — para cada construção (ordem do site): `ano` (0 = sem ano) e `origem`
  (1 = pixel do centro, 2 = vizinhança, 0 = nenhum).

O MDT/MDE do IEMA (8 blocos, ~400 MB) não vai para o Git: baixar de novo do GEOBASES e rodar
`pipeline/02_modelo/colatina_iema_mosaico.py`.

As construções e o limiar de água de cada pixel já estão nos arquivos de `site/data/`.
