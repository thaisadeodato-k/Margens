# Registro de decisões

Cada linha: o que foi decidido, por quê, e o que se perdeu ou ganhou. Útil para o estudo de caso do portfólio.

| Data | Decisão | Por quê |
|---|---|---|
| 28/10/2026 | Pedreiras e Trizidela como primeiro caso | Pedido do Wenzel Nicácio, que propôs mapear a área urbana suscetível a inundação das duas cidades. Parceria combinada no LinkedIn. |
| 28/10/2026 | Modelo de "água conectada ao rio" em vez de modelagem hidráulica | Funciona só com dados públicos nacionais e pode ser repetido em outras cidades. Modelagem hidráulica exigiria batimetria e vazões detalhadas. |
| 28/10/2026 | Construções do Overture (Google Open Buildings) | O OpenStreetMap tinha só 42 construções em Pedreiras. Custo: são detectadas por IA e não têm altura. |
| 29/10/2026 | Trocar SRTM por ANADEM | ANADEM remove o viés da vegetação. Resultado: a diferença na área construída foi pequena (mediana 0,2 m), o ganho foi nas áreas com árvores. |
| 29/10/2026 | Régua real da ANA em vez de "metros acima do rio" | As pessoas e a imprensa falam em metros na régua (ex.: 7,40 m em 2024). Permite também contar a frequência de cada nível. |
| 29/10/2026 | Pedreiras calibrada pelo início dos impactos (6 m) | Não há mancha real mapeada nem altitude do zero da régua. É a âncora pública disponível; margem ~1 m declarada na página. |
| 29/10/2026 | Colatina calibrada pela mancha real de 1997 | A SGB mapeou a cheia de 1997 e a estação registrou 7,99 m: calibração por evento real, mais forte que em Pedreiras. |
| 29/10/2026 | Colatina como segunda cidade | Cidade de origem da Thais, onde fez SIG na Prefeitura e participou do artigo do SBRH 2021 sobre o Rio Doce. Prova que o método se repete. |
| 29/10/2026 | Overture para ruas/rios/escolas em Colatina | O Overpass (OSM) estava sobrecarregado. O Overture redistribui os dados do OSM. |
| 29/10/2026 | Página com globo e uma cidade por arquivo | Antes as duas cidades carregavam juntas (5 MB). Agora cada cidade é um arquivo; acrescentar uma cidade não exige mudar o código. |
| 29/10/2026 | Repositório `Margens`, privado até combinar com o Wenzel | A parte de Pedreiras é da parceria; publicar só com o acordo dele. |
| 29/10/2026 | Repositório e site públicos (GitHub Pages) | Decisão da Thais: o estudo foi feito só com dados públicos, nenhum dado do Wenzel. O crédito pela proposta do caso de Pedreiras continua no site e no README. |
| 29/10/2026 | Colatina: tirar os afluentes da máscara do rio | Testando o IEMA, apareceram construções alcançadas cedo demais ao longo dos rios Pancas e Santa Maria do Doce: os polígonos deles estavam na máscara, então o modelo enchia esses vales a partir do leito do afluente. Sem eles, a mancha de 1997 fica mais bem reproduzida (IoU 0,65 → 0,70; acerto 81% → 92%), R0 passa de 2,4 para −0,6 m e 1979 sai em 9,2 m (antes 11,5), perto do relato de ~9,1 m. Em 7,99 m: 1.440 → 1.851 construções. |
| 29/10/2026 | Colatina: modelo de água continua no ANADEM; IEMA só para relevo sombreado e altura | O MDT de 2 m reproduz um pouco melhor a área da mancha de 1997 (IoU 0,75), mas acerta menos construções (60% contra 80%) e põe 1979 em 10,2 m. Como a página conta construções, ficou o ANADEM. O resultado do IEMA entra no texto como faixa de incerteza (1.258 a 1.851 construções em 7,99 m). Resolução maior não melhorou o resultado sozinha. |
| 29/10/2026 | Colatina: altura medida das construções (IEMA MDE − MDT) | Antes era estimada pela área. 65% ganham altura medida; o resto continua estimado, e a ficha diz qual é o caso. |
| 29/10/2026 | Colatina: cursos livres, autoescolas e escolas de idiomas fora da contagem de escolas | O Overture classifica Kumon, autoescolas e cursos como escola. Escolas: 31 → 17. |
