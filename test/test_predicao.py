# Testes da predicao (regressao linear simples)

import pytest
from sistema.predicao import PrevisaoIndisponivelError, RegressaoSimples, prever


def historico_igual(quantidade=10):
    "Alunos de turmas passadas em que a P2 foi igual a P1."
    return [{"P1": nota, "P2": nota} for nota in range(1, quantidade + 1)]


# RegressaoSimples

def test_reta_exata():
    modelo = RegressaoSimples.treinar([1, 2, 3, 4], [3, 5, 7, 9])
    assert modelo.coeficiente == pytest.approx(2)
    assert modelo.intercepto == pytest.approx(1)
    assert modelo.erro_padrao == pytest.approx(0, abs=1e-9)
    assert modelo.r2 == pytest.approx(1)


def test_prever_com_a_reta():
    modelo = RegressaoSimples.treinar([1, 2, 3, 4], [3, 5, 7, 9])
    assert modelo.prever(10) == pytest.approx(21)


def test_poucas_observacoes():
    with pytest.raises(PrevisaoIndisponivelError):
        RegressaoSimples.treinar([1, 2], [3, 5])


def test_todos_com_a_mesma_nota_base():
    with pytest.raises(PrevisaoIndisponivelError):
        RegressaoSimples.treinar([5, 5, 5], [3, 5, 7])


# prever

def test_previsao_de_quem_vai_mal(regras_p1_p2):
    resultado = prever(historico_igual(), {"P1": 4, "P2": None}, regras_p1_p2)
    assert resultado.notas_previstas["P2"] == pytest.approx(4)
    assert resultado.media_final_prevista == pytest.approx(4)
    assert resultado.chance_aprovacao == 0


def test_previsao_de_quem_vai_bem(regras_p1_p2):
    resultado = prever(historico_igual(), {"P1": 8, "P2": None}, regras_p1_p2)
    assert resultado.media_final_prevista == pytest.approx(8)
    assert resultado.chance_aprovacao == 1


def test_chance_entre_0_e_1_e_cresce_com_a_nota(regras_p1_p2):
    # Com ruido na P2 a previsao deixa de ser certa
    historico = [
        {"P1": nota, "P2": nota + (1 if nota % 2 == 0 else -1)}
        for nota in range(1, 11)
    ]
    chance_baixa = prever(historico, {"P1": 5, "P2": None}, regras_p1_p2).chance_aprovacao
    chance_alta = prever(historico, {"P1": 7, "P2": None}, regras_p1_p2).chance_aprovacao
    assert 0 < chance_baixa < chance_alta < 1


def test_chance_abaixo_da_media(regras_p1_p2):
    resultado = prever(historico_igual(), {"P1": 8, "P2": None}, regras_p1_p2)
    assert resultado.chance_abaixo_da_media == 0


def test_nota_prevista_nao_passa_de_10(regras_p1_p2):
    historico = [{"P1": nota, "P2": 2 * nota} for nota in range(10)]
    resultado = prever(historico, {"P1": 10, "P2": None}, regras_p1_p2)
    assert resultado.notas_previstas["P2"] == 10


def test_sem_avaliacoes_pendentes(regras_p1_p2):
    resultado = prever([], {"P1": 8, "P2": 8}, regras_p1_p2)
    assert resultado.notas_previstas == {}
    assert resultado.chance_aprovacao == 1


def test_sem_nenhuma_nota_conhecida(regras_p1_p2):
    with pytest.raises(PrevisaoIndisponivelError):
        prever(historico_igual(), {"P1": None, "P2": None}, regras_p1_p2)


def test_historico_pequeno_demais(regras_p1_p2):
    with pytest.raises(PrevisaoIndisponivelError):
        prever(historico_igual(5), {"P1": 4, "P2": None}, regras_p1_p2)
