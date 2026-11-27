# Relação entre testes e critérios de aceitação

Os critérios estão em [historia_usuario.md](historia_usuario.md). Cada teste das histórias começa a docstring com o código do critério (por exemplo, `H3-C2` é a história 3, critério 2).

| Critério | Arquivo | Teste |
|---|---|---|
| H1-C1 | `test/test1.py` | `test_criterios_prof` |
| H1-C2 | `test/test1.py` | `test_calcular_notas` |
| H1-C3 | `test/test1.py` | `test_av_pendentes` |
| H1-C4 | `test/test1.py` | `test_nota_atual` |
| H2-C1 | `test/test2.py` | `test_verifica_nota_atual` |
| H2-C2 | `test/test2.py` | `test_verifica_reprovacao` |
| H2-C3 | `test/test2.py` | `test_verifica_possibilidades` |
| H2-C4 | `test/test2.py` | `test_verifica_nota_presenca` e `test_verifica_nota_presenca_atual` |
| H3-C1 | `test/test3.py` | `test_informa_aulas_e_faltas` |
| H3-C2 | `test/test3.py` | `test_limite_depende_da_nota` |
| H3-C3 | `test/test3.py` | `test_regras_fixas_de_presenca` |
| H3-C4 | `test/test3.py` | `test_faltas_permitidas_com_nota_6` |
| H4-C1 | `test/test4.py` | `test_nota_necessaria` |
| H4-C2 | `test/test4.py` | `test_ja_aprovado` |
| H4-C3 | `test/test4.py` | `test_recuperacao` |
| H4-C4 | `test/test4.py` | `test_reprovado` e `test_nota_necessaria_recuperacao` |

São 18 testes para os 16 critérios.

## Testes dos módulos

Além dos testes das histórias, cada módulo tem testes próprios:

| Arquivo | O que testa | Testes |
|---|---|---|
| `test/test_carregador.py` | leitura e validação de CSV, JSON, frequência e histórico | 31 |
| `test/test_predicao.py` | regressão, nota prevista e chance de aprovação | 12 |
| `test/test_relatorio.py` | relatório, previsão e formatação do texto | 12 |
| `test/test_cli.py` | menu e comando `python -m sistema` | 7 |
| `test/test_leitores.py` | passos do Template Method e leitores | 10 |
| `test/test_fachada.py` | métodos da fachada | 5 |
| `test/test_comandos.py` | cada comando e a montagem do menu | 8 |

Total: 103 testes. Para rodar tudo: `python -m pytest`. O arquivo `test/test_regras_negocio.py` só reúne os testes de `test1.py` a `test4.py`, para o pytest encontrá-los.
