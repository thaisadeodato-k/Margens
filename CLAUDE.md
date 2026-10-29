# Margens — contexto para retomar o trabalho

Projeto pessoal da Thais Adeodato (analista de governança de dados, formada em Arquitetura e Urbanismo pelo Ifes
Colatina). Não programa: constrói com IA. Fale com ela em português. Ela trabalha de dois computadores; o ambiente de
nuvem do Claude é temporário, então **todo trabalho precisa terminar com commit e push neste repositório**.

## O que é
Mapas 3D de cheias, construção por construção, com a régua real da ANA. Página: globo (`site/index.html`) → cidade
(carrega só `site/data/<cidade>.json`). Mesmo sistema visual do projeto Camadas São Paulo
(thaisadeodato-k/camadas-sp): deck.gl 8.9.36, painéis de vidro em estilo Apple, régua com histograma na base.

Também publicado como página no Claude (artifact) `https://claude.ai/artifact/YHQ1pdLcvfqvb2wTt2wmaf`, com os mesmos
arquivos de `site/data/`. Para republicar ali, publicar o conteúdo do `<body>` de `site/index.html` (o artifact
acrescenta o esqueleto `<!doctype>`/`<head>` sozinho) com `files` apontando para `site/data/*.json`.

## Para que serve
Item principal do portfólio da candidatura ao mestrado **AISS (Erasmus Mundus: AI for Sustainable Societies)**,
envio até ~10/12/2026. Ligar sempre aos três pilares: IA/dados, sociedades sustentáveis, design participativo.
Material da candidatura em inglês acadêmico claro. Ser honesta e crítica: apontar exageros e pontos fracos.

## Regras
- **Papel da Thais**: concepção, escolha/auditoria das fontes, método, validação. Programação com assistência de IA.
  Nunca exagerar o papel dela.
- **Wenzel Nicácio** propôs o caso de Pedreiras; parceria combinada. **Não tornar o repositório nem o site públicos
  sem o acordo dele.**
- Mostrar incerteza: a régua de Pedreiras tem margem de ~1 m; "alcançada" ≠ "invadida".
- Nunca apresentar o mapa como alerta ou previsão.

## Números de referência
- Pedreiras: R0 = 3,8 m (régua = nível do modelo + R0). Régua 7,45 m (2024/2026) → 1.450 construções; 9,81 m (2009)
  → ~3.680. Setores SGB de inundação 77% cobertos em 9,81 m. Estação 33281000.
- Colatina: R0 = −0,6 m (relevo ANADEM, afluentes fora da máscara do rio), ajustado à mancha real de 1997 (7,99 m):
  acerto 92%, precisão 74%, 80% das construções da mancha alcançadas. 7,99 m → 1.851 construções; 8,90 m (2013) →
  ~2.370. 1979 ≈ 9,2 m (estimado; relato na imprensa ~9,1 m). Cota de inundação da Defesa Civil 5,80 m (~700
  construções no modelo: exagera em níveis baixos). Com o MDT de 2 m do IEMA (teste): 1.258 construções em 7,99 m.
  Altura medida (IEMA MDE − MDT) em 65% das construções. Estação 56994500.
- Inconsistência da SGB (Pedreiras/Trizidela): 12.000 pessoas no arquivo original × 1.200 no atualizado.

## Como os dados foram obtidos
O ambiente de nuvem não acessa os servidores de dados. Tudo foi baixado pelo **painel de navegador do app** no
computador da Thais, com os scripts de `pipeline/01_obter/` rodando na própria origem de cada site, e transferido
em fatias base64 (< 250 mil caracteres por resposta). Arquivos grandes (ex.: MDT do IEMA, 51 MB por bloco) a Thais
baixa no navegador dela para a pasta Downloads, e o Claude busca de lá.

## Próximo passo
Ver `docs/PROXIMOS_PASSOS.md`. O IEMA de Colatina (blocos 32_784, 33_784, 32_785, 33_785 em
`https://one.s3.es.gov.br/pr-geobases-public/MAP_ES_2012_2015/MDT/` e `/MDE/`) já foi incorporado em 29/10/2026.
A seguir: itens do portfólio AISS (participação, Censo, auditoria das construções, incerteza na página, inglês).
