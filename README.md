# Margens

**Duas margens · Cheias no Brasil** — mapas 3D de cidades construídas na planície de um rio, mostrando, construção por
construção, até onde a água chega quando o rio sobe. A régua de cada mapa é a da estação fluviométrica da ANA na
cidade, a mesma citada nas notícias das cheias.

Cidades mapeadas:

| Cidade | Rio | Construções | Régua | Calibração |
|---|---|---|---|---|
| Pedreiras e Trizidela do Vale (MA) | Mearim | 21.466 | Pedreiras II, 1978–2026 | início dos impactos (6 m) |
| Colatina (ES) | Doce | 34.334 | Colatina Ponte, 1938–2026 | mancha real da cheia de 1997 (SGB); altura das construções pelo IEMA |

## Como ver

No navegador: **https://thaisadeodato-k.github.io/Margens/**

Ou localmente: abra `site/index.html` por um servidor local (os dados são carregados de `site/data/`):

```
cd site
python -m http.server 8000
# abrir http://localhost:8000
```

## Estrutura

```
site/          página (globo + mapa de cada cidade) e dados de cada cidade
pipeline/      como os dados foram obtidos, modelados e preparados para a página
dados/         séries da ANA e pacotes SIG da SGB (pequenos); dados grandes ficam fora do Git
docs/          FONTES (proveniência), METODO, DECISOES, PROXIMOS_PASSOS
CLAUDE.md      contexto para retomar o trabalho com o Claude de qualquer computador
```

## Acrescentar uma cidade

1. Rodar o pipeline para a cidade (`pipeline/README.md`).
2. Salvar `site/data/<cidade>.json` (com o bloco `cfg`: textos, faixa da régua, cheias marcadas).
3. Acrescentar uma linha em `site/data/cities.json`. O globo e a lista se atualizam sozinhos.

## Créditos

Concepção, escolha e auditoria das fontes, método e validação: **Thais Adeodato**.
Proposta do caso de Pedreiras e Trizidela do Vale: **Wenzel Nicácio**.
Programação e processamento feitos com assistência de IA (Claude, Anthropic).

Dados: ANA (HidroWeb, ANADEM com IPH/UFRGS), Serviço Geológico do Brasil, Overture Maps (Google Open Buildings,
Microsoft, OpenStreetMap), © colaboradores do OpenStreetMap (ODbL), IEMA/GEOBASES-ES, Natural Earth.
Detalhes e licenças em `docs/FONTES.md`.

Este é um mapa de suscetibilidade para entender o território. Não é previsão nem alerta.
Em emergência: Defesa Civil 199, Bombeiros 193.

Licença do código: a definir.
