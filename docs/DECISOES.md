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
