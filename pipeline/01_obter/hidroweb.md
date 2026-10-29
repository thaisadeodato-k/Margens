# HidroWeb (ANA): séries de cotas

1. Abrir https://www.snirh.gov.br/hidroweb/serieshistoricas
2. **Tipo Estação** = Fluviométrica; **Nome Estação** = nome da cidade; Consultar.
3. Estações usadas:
   - Pedreiras II — **33281000** (rio Mearim, 1978–2026) — régua principal de Pedreiras
   - Pedreiras — 33280000 (1968–1982, régua antiga, ~0,47 m acima da atual)
   - Colatina Ponte — **56994500** (rio Doce, 1938–2026)
4. Baixar o CSV da estação (botão "baixar csv"). Vem um zip com `*_Cotas.csv` (cm, uma linha por mês, colunas `Cota01..Cota31`),
   além de vazões, resumo de descarga e, em algumas, perfil transversal.

Observação: a API do HidroWeb exige token; o download foi feito pela interface pública, sem login.
No painel do navegador do app (que não salva downloads), o arquivo foi capturado interceptando `URL.createObjectURL`
antes de clicar no botão de download.

A ficha da estação **não informa a altitude do zero da régua** (campo Altitude vazio), por isso a régua é calibrada
no modelo (ver `docs/METODO.md`).
