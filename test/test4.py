# teste história de usuário 4

import pytest
from sistema.calculo import calcular_nota_necessaria, calcular_nota_recuperacao

def test_nota_necessaria(regras_calculo):
    "H4-C1: (6 - 2,7) / 0,4 = 8,25."
    notas = {"P1": 4, "P2": 5, "Trabalho": None}
    assert calcular_nota_necessaria(notas, regras_calculo) == pytest.approx(8.25)

def test_ja_aprovado():
    "H4-C2: nota atual >= 6 -> nota necessária 0."
    regras = {"media_aprovacao": 6.0, "avaliacoes": {"P1": 0.6, "P2": 0.4}}
    assert calcular_nota_necessaria({"P1": 10, "P2": None}, regras) == 0

def test_recuperacao(regras_p1_p2):
    "H4-C3: nota necessária = 11 (> 10) e recuperação possível -> 'Recuperação'."
    notas = {"P1": 1, "P2": None}
    assert calcular_nota_necessaria(notas, regras_p1_p2) == "Recuperação"

def test_reprovado():
    "H4-C4: nota necessária 60 e recuperação > 10 -> 'Reprovado'."
    regras = {"media_aprovacao": 6.0, "avaliacoes": {"P1": 0.9, "P2": 0.1}}
    assert calcular_nota_necessaria({"P1": 0, "P2": None}, regras) == "Reprovado"

def test_nota_necessaria_recuperacao():
    "H4-C4: média final 4 -> (4 + rec) / 2 >= 6 -> rec = 8."
    assert calcular_nota_recuperacao(4.0) == pytest.approx(8.0)