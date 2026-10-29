# Método

## Água conectada ao rio

1. **Grade**: todas as camadas vão para uma grade Web Mercator alinhada aos blocos z14 (~9 m por pixel).
2. **Rio**: linha do rio principal (Mearim ou Doce) do OSM/Overture, alargada alguns pixels; em Colatina, unida aos
   polígonos do próprio Rio Doce. Os afluentes ficam **fora** da máscara: a água entra neles pelo nível do Doce
   (remanso), e não a partir do leito do afluente. (Até 29/10 os polígonos dos rios Pancas e Santa Maria do Doce
   entravam na máscara, e o modelo enchia esses vales cedo demais; ver DECISOES.)
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
| Colatina | Nível que melhor reproduz a **mancha real de 1997** (SGB), quando a régua marcou 7,99 m. Melhor ajuste: nível 8,6 m (IoU 0,70; acerto 92%; precisão 74%, dentro do corredor que a SGB mapeou). O mesmo nível é o melhor também contando construções (80% das construções dentro da mancha alcançadas) | **−0,6 m** | Forte: evento real mapeado |
| Pedreiras | As famílias começam a ser afetadas acima de **6 m** na régua (Agência Brasil). No modelo: nível em que 1% das construções é alcançado (2,16 m) | **3,8 m** | Indireta, margem ~1 m |

A mancha de 1979 em Colatina corresponde, pelo modelo, a 9,8 m de nível → **~9,2 m na régua (estimado; a estação não
registrou)**. Um relato independente (comerciante do centro, A Gazeta 2020: em 2013, com 8,90 m, a água ficou 20 cm abaixo
da marca de 1979) daria ~9,1 m. Antes da correção da máscara do rio a estimativa era 11,5 m.

R0 negativo quer dizer só que o zero da régua fica 0,6 m abaixo da superfície de referência do rio no modelo (o
percentil 10 do relevo sobre o rio, perto do nível de águas baixas).

## Relevo de 2 m do IEMA (Colatina): teste de sensibilidade

O mesmo modelo foi rodado no MDT de 2 m do IEMA (grade z15, ~4,8 m), com a referência do rio vinda do ANADEM
(o MDT tem ruído sobre a água) e recalibrado com 1997.

| Relevo | R0 | Mancha 1997: IoU / acerto / precisão | Construções dentro da mancha 1997 alcançadas | Construções a 7,99 m | 1979 estimada |
|---|---|---|---|---|---|
| ANADEM 30 m (usado) | −0,6 m | 0,70 / 92% / 74% | 80% (885 de 1.109) | 1.851 | 9,2 m |
| IEMA 2 m (teste) | 3,1 m | 0,75 / 87% / 84% | 60% (670 de 1.109) | 1.258 | 10,2 m |

O IEMA desenha a mancha um pouco melhor, mas erra mais construção por construção, e o que a página conta são
construções. A diferença entre os dois (1.258 a 1.851 em 7,99 m) é uma medida da incerteza que vem do relevo.
Hipóteses para a diferença, não testadas: metros inteiros no MDT; o ANADEM ainda carrega parte das construções na
cidade (por isso precisa de um nível mais alto, R0 menor); a mancha de 1997 da SGB foi traçada por quarteirão.

## Altura das construções (Colatina)

Mediana de MDE − MDT do IEMA (grade z16, ~2,4 m) dentro de cada contorno. Teste de alinhamento: deslocar os contornos
não aumenta a altura média, então contornos (Overture) e relevo (IEMA) estão alinhados. Mediana ≥ 2,5 m → altura
medida (65% das construções; mediana dessas 5,5 m). Abaixo disso (construção posterior ao voo de 2012–2015, muito
pequena ou sob árvore) → altura estimada pela área, como em Pedreiras. A ficha de cada construção diz qual é o caso.

## Frequência

Máximos anuais da régua, só anos com mais de 300 dias de leitura: Pedreiras 48 anos (1978–2025), Colatina 79 anos
(1938–2025). Para cada nível, conta-se em quantos anos o máximo anual chegou a ele.

## Validação

- **Pedreiras**: com a régua de 2009 (9,81 m), a mancha cobre 77% dos dois setores de inundação da SGB (2012);
  os setores de deslizamento ficam a 0%.
- **Colatina**: 92% de acerto e 74% de precisão contra a mancha real de 1997 (80% das construções dentro da mancha).
  Os 15 setores de inundação de 2019 ficam 62% cobertos (pela área) nesse nível; os menos cobertos estão nas margens dos
  afluentes (cheias deles, fora do modelo). Setores de deslizamento: 0%.
- **Colatina, níveis baixos**: na cota de inundação da Defesa Civil (5,80 m) o modelo já alcança ~700 construções, e
  ~280 com 3 m (nível que o rio passa em quase todos os anos). O modelo exagera nas margens em níveis baixos; a
  calibração vale para cheias grandes.

## Limites

- Relevo de 30 m; o ANADEM remove vegetação, não construções. Em Colatina, o relevo de 2 m do IEMA muda o número de construções em ~30% (ver acima).
- "Alcançada" = a água toca o contorno, não necessariamente entra na casa. O modelo alcança mais construções do que
  as famílias desalojadas nas cheias reais (ex.: Pedreiras 2026: ~260 famílias desalojadas ou em abrigos nas duas
  cidades, contra ~1.450 construções alcançadas com régua equivalente).
- Só a cheia do rio principal: afluentes, enxurradas e alagamento por chuva ficam de fora.
- Diques, barragens e drenagem urbana não estão representados.
