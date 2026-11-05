# Teste história de usuário 1

import pytest
from sistema.carregador import carregar_notas, carregar_regras
from sistema.calculo import calcular_nota_atual

def test_criterios_prof(arquivos_validos):
    "H1-C1: dado um JSON válido, o sistema lê os pesos do professor."
    _, js = arquivos_validos
    regras = carregar_regras(js)["Calculo I"]
    assert regras["avaliacoes"] == {"P1": 0.3, "P2": 0.3, "Trabalho": 0.4}

def test_calcular_notas(arquivos_validos):
    "H1-C2: dado um CSV válido, o sistema retorna a nota atual (P1=4, P2=5 -> 2,7)."
    csv, js = arquivos_validos
    notas = carregar_notas(csv)["Calculo I"]
    regras = carregar_regras(js)["Calculo I"]
    assert calcular_nota_atual(notas, regras) == pytest.approx(2.7)


def test_av_pendentes(regras_calculo):
    "H1-C3: avaliações pendentes não entram na soma."
    notas = {"P1": 4, "P2": 5, "Trabalho": None}
    assert calcular_nota_atual(notas, regras_calculo) == pytest.approx(2.7)


def test_nota_atual(regras_calculo):
    "H1-C4: nota atual = soma de (nota x peso) das avaliações realizadas."
    notas = {"P1": 4, "P2": 5, "Trabalho": 10}
    assert calcular_nota_atual(notas, regras_calculo) == pytest.approx(6.7)
