# teste história de usuário 2

import pytest
from sistema.calculo import classificar_situacao

def test_verifica_nota_atual():
    "H2-C1: nota atual >= 6 -> aprovado."
    regras = {"media_aprovacao": 6.0, "avaliacoes": {"P1": 0.6, "P2": 0.4}}
    assert classificar_situacao({"P1": 10, "P2": None}, regras) == "aprovado"
 
def test_verifica_reprovacao():
    "H2-C2: mesmo com 10 nas pendentes e recuperação, não chega a 6 -> reprovado."
    regras = {"media_aprovacao": 6.0, "avaliacoes": {"P1": 0.9, "P2": 0.1}}
    assert classificar_situacao({"P1": 0, "P2": None}, regras) == "reprovado"
  
def test_verifica_possibilidades(regras_calculo):
    "H2-C3: nota abaixo de 6, mas ainda alcançável nas pendentes -> em risco."
    notas = {"P1": 4, "P2": 5, "Trabalho": None}
    assert classificar_situacao(notas, regras_calculo) == "em risco"
 
def test_verifica_nota_presenca(regras_calculo):
    "H2-C4: nota final 7 exige 65% de presença; com 60% -> reprovado."
    notas = {"P1": 7, "P2": 7, "Trabalho": 7}
    assert classificar_situacao(notas, regras_calculo, presenca=0.60) == "reprovado"
 
def test_verifica_nota_presenca_atual(regras_calculo):
    "H2-C4: nota final 9 exige só 50% de presença; com 55% -> aprovado."
    notas = {"P1": 9, "P2": 9, "Trabalho": 9}
    assert classificar_situacao(notas, regras_calculo, presenca=0.55) == "aprovado"