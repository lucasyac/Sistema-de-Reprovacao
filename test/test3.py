# Teste história de usuário 3

import pytest
from sistema.calculo import calcular_faltas_permitidas

# Nos testes usamos 100 aulas para a conta dar número inteiro:
# 75% de presença -> 25 faltas no máximo
# 65% de presença -> 35 faltas no máximo
# 50% de presença -> 50 faltas no máximo

def test_informa_aulas_e_faltas():
    "H3-C1: o aluno informa aulas totais e faltas; sem aulas totais não há como calcular."
    assert calcular_faltas_permitidas(aulas_totais=100, faltas=10, nota_atual=6) == 15
    with pytest.raises(ValueError):
        calcular_faltas_permitidas(aulas_totais=0, faltas=0, nota_atual=6)

def test_limite_depende_da_nota():
    "H3-C2: com a mesma quantidade de faltas, a nota atual muda o limite (6 -> 15, 9 -> 40)."
    assert calcular_faltas_permitidas(100, 10, nota_atual=6) == 15
    assert calcular_faltas_permitidas(100, 10, nota_atual=9) == 40

def test_regras_fixas_de_presenca():
    "H3-C3: nota < 6.5 exige 75%, de 6.5 a menos de 8 exige 65%, de 8 em diante exige 50%."
    assert calcular_faltas_permitidas(100, 0, nota_atual=6.4) == 25
    assert calcular_faltas_permitidas(100, 0, nota_atual=6.5) == 35
    assert calcular_faltas_permitidas(100, 0, nota_atual=7.9) == 35
    assert calcular_faltas_permitidas(100, 0, nota_atual=8) == 50

def test_faltas_permitidas_com_nota_6():
    "H3-C4: aprovado com nota 6 -> presença mínima de 75%; 100 aulas e 10 faltas -> 15 faltas ainda permitidas."
    assert calcular_faltas_permitidas(100, 10, nota_atual=6) == 15
