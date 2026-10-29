# Próximos passos

Prazo de referência: envio da candidatura ao AISS (Erasmus Mundus) até ~10/12/2026.

## Em andamento
- [x] **Colatina com relevo de 2 m (IEMA)**: feito em 29/10. Ficou como teste de sensibilidade (ver METODO e DECISOES).
- [x] **Altura real das construções em Colatina**: MDE − MDT, 65% das construções.
- [ ] **Conferir com quem conhece Colatina**: o modelo põe o Hospital Sílvio Avidos e a EEEFM Rubens Rangel alcançados
      a partir de ~8,1 m, e o Hospital Unimed a ~8,5 m (2013 chegou a 8,90 m). Isso aconteceu em 2013? Bom tema para a
      conversa com a Defesa Civil ou o grupo do Ifes.
- [ ] **Níveis baixos em Colatina**: o modelo alcança ~700 construções na cota de inundação (5,80 m). Ver se dá para
      usar a cota como segunda âncora, ou mostrar na página que abaixo de ~6 m o mapa exagera.

## Em teste
- [ ] **Régua vertical** (ramo `prototipo-regua-vertical`, também como página privada no Claude
      `https://claude.ai/artifact/6rPUBYWdxceJ3WoVgyv7sd`): no computador, régua desenhada como a de verdade, faixa de
      frequência (em quantos anos o rio chegou a cada altura) e marcos (cheias, cotas da Defesa Civil, 1ª escola,
      1º hospital). No celular continua horizontal. Antes de decidir, mostrar as duas versões para 4–5 pessoas e anotar
      o que entendem (design participativo).

## Para o portfólio AISS (por prioridade)
1. [ ] **Participação**: camada "até onde a água chegou" (marcas de moradores, sem nome) + conversas de validação
       documentadas com o Wenzel (Pedreiras), o grupo do Ifes Colatina e/ou a Defesa Civil.
2. [ ] **Quem mora na área alagável**: cruzar a mancha com os setores do Censo 2022 (população, renda, idade).
3. [ ] **Auditoria das construções detectadas por IA**: amostra sorteada (~200 pontos) dentro e fora da área alagável,
       conferida pela Thais no QGIS contra as ortofotos de 25 cm do IEMA (ECW). Medir omissões e falsos positivos.
4. [ ] **Incerteza e proveniência na página**: faixa de construções pela margem da régua; ficha de fonte por número.
5. [ ] **Versão em inglês** da página e **estudo de caso de uma página** em inglês acadêmico.

## Técnico
- [ ] Scripts com caminhos relativos e um `config` por cidade.
- [ ] Melhorar o contorno do Rio Doce (ilhas) — possível uso da hidrografia do grupo do Ifes (SBRH 2021), com citação.
- [ ] Usar a atualização da setorização da SGB de Colatina (2025).
- [x] Publicado no GitHub Pages em 29/10/2026.
- [ ] Escolher a licença do código (sugestão: MIT) e dos textos/dados derivados (sugestão: CC BY 4.0).
