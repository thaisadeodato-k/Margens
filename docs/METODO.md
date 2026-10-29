# Método

## Água conectada ao rio

1. **Grade**: todas as camadas vão para uma grade Web Mercator alinhada aos blocos z14 (~9 m por pixel).
2. **Rio**: linha do rio principal (Mearim ou Doce) do OSM/Overture, alargada alguns pixels; em Colatina, unida aos
   polígonos de rio que a tocam.
3. **Nível de referência do rio**: percentil 10 do relevo sobre as células do rio (janela de 41 px), propagado para cada
   ponto pelo rio mais próximo e suavizado (σ = 25 px).
4. **Altura acima do rio** = relevo − referência.
5. **Preenchimento conectado**: reconstrução morfológica por erosão a partir do rio. Para cada pixel, resulta o menor nível
   de água (acima do rio) capaz de alcançá-lo sem atravessar terreno mais alto. Baixadas isoladas atrás de um morro
   continuam secas. É o princípio dos modelos HAND / "altura acima da drenagem".
6. **Construção alcançada**: o menor nível entre os vértices do contorno e o centroide.

## Calibração da régua

O modelo mede "metros acima da referência do rio"; a página mostra "metros na régua da estação". A ligação é
`régua = nível do modelo + R0`.

| Cidade | Como R0 foi obtido | R0 | Força |
|---|---|---|---|
| Colatina | Nível que melhor reproduz a **mancha real de 1997** (SGB), quando a régua marcou 7,99 m. Melhor ajuste: nível 5,6 m (IoU 0,65; acerto 81%; precisão 76%, dentro do corredor que a SGB mapeou) | **2,4 m** | Forte: evento real mapeado |
| Pedreiras | As famílias começam a ser afetadas acima de **6 m** na régua (Agência Brasil). No modelo: nível em que 1% das construções é alcançado (2,16 m) | **3,8 m** | Indireta, margem ~1 m |

A mancha de 1979 em Colatina corresponde, pelo modelo, a ~9,1 m de nível → **~11,5 m na régua (estimado; a estação não registrou)**.

## Frequência

Máximos anuais da régua, só anos com mais de 300 dias de leitura: Pedreiras 48 anos (1978–2025), Colatina 79 anos
(1938–2025). Para cada nível, conta-se em quantos anos o máximo anual chegou a ele.

## Validação

- **Pedreiras**: com a régua de 2009 (9,81 m), a mancha cobre 77% dos dois setores de inundação da SGB (2012);
  os setores de deslizamento ficam a 0%.
- **Colatina**: 81% de acerto e 76% de precisão contra a mancha real de 1997. Os 15 setores de inundação de 2019 ficam
  só 42% cobertos nesse nível, porque parte está nos vales dos rios Pancas e Santa Maria do Doce (cheias dos afluentes,
  fora do modelo). Setores de deslizamento: 0%.

## Limites

- Relevo de 30 m; o ANADEM remove vegetação, não construções.
- "Alcançada" = a água toca o contorno, não necessariamente entra na casa. O modelo alcança mais construções do que
  as famílias desalojadas nas cheias reais (ex.: Pedreiras 2026: ~260 famílias desalojadas ou em abrigos nas duas
  cidades, contra ~1.450 construções alcançadas com régua equivalente).
- Só a cheia do rio principal: afluentes, enxurradas e alagamento por chuva ficam de fora.
- Diques, barragens e drenagem urbana não estão representados.
