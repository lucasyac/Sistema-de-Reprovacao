# Testes do relatorio (montagem e formatacao do texto)

import pytest
from sistema.carregador import Materia
from sistema.predicao import PrevisaoIndisponivelError
from sistema.relatorio import (
    formatar_numero,
    formatar_percentual,
    formatar_previsao,
    formatar_relatorio,
    gerar_previsao,
    gerar_relatorio,
)

FREQUENCIA = {"aulas_totais": 60, "faltas": 8}


def materia_calculo(regras, frequencia=None, notas=None):
    notas = notas or {"P1": 4.0, "P2": 5.0, "Trabalho": None}
    return Materia("Calculo 1", notas, regras, frequencia)


def escrever_historico(pasta, alunos=12):
    linhas = ["aluno,P1,P2,Trabalho"]
    for numero in range(alunos):
        nota = 2 + numero * 0.5
        linhas.append(f"A{numero},{nota},{nota},{nota}")
    (pasta / "calculo1.csv").write_text("\n".join(linhas), encoding="utf-8")


# gerar_relatorio

def test_relatorio_sem_frequencia(regras_calculo):
    relatorio = gerar_relatorio(materia_calculo(regras_calculo))
    assert relatorio.nota_atual == pytest.approx(2.7)
    assert relatorio.situacao == "em risco"
    assert relatorio.nota_necessaria == pytest.approx(8.25)
    assert relatorio.avaliacoes_pendentes == ["Trabalho"]
    assert relatorio.faltas_permitidas is None


def test_relatorio_com_frequencia(regras_calculo):
    relatorio = gerar_relatorio(materia_calculo(regras_calculo, FREQUENCIA))
    assert relatorio.presenca == pytest.approx(52 / 60)
    assert relatorio.presenca_minima == 0.75
    assert relatorio.faltas_permitidas == 7


def test_relatorio_de_quem_ja_passou(regras_calculo):
    notas = {"P1": 8.0, "P2": 8.0, "Trabalho": 8.0}
    relatorio = gerar_relatorio(materia_calculo(regras_calculo, notas=notas))
    assert relatorio.situacao == "aprovado"
    assert relatorio.nota_necessaria == 0
    assert relatorio.avaliacoes_pendentes == []


# formatacao

def test_formatar_numero():
    assert formatar_numero(2.7) == "2,70"
    assert formatar_numero(8.254, casas=1) == "8,3"


def test_formatar_percentual():
    assert formatar_percentual(0.5) == "50,0%"
    assert formatar_percentual(0) == "0,0%"
    assert formatar_percentual(1) == "100,0%"
    assert formatar_percentual(0.0004) == "< 0,1%"
    assert formatar_percentual(0.9995) == "> 99,9%"


def test_texto_do_relatorio(regras_calculo):
    relatorio = gerar_relatorio(materia_calculo(regras_calculo, FREQUENCIA))
    texto = formatar_relatorio(relatorio)
    assert "Calculo 1" in texto
    assert "2,70" in texto
    assert "EM RISCO" in texto
    assert "8,25" in texto
    assert "Faltas ainda permitidas" in texto


def test_texto_do_relatorio_sem_frequencia(regras_calculo):
    relatorio = gerar_relatorio(materia_calculo(regras_calculo))
    assert "Faltas ainda permitidas" not in formatar_relatorio(relatorio)


def test_texto_quando_so_a_recuperacao_salva(regras_p1_p2):
    materia = Materia("Algoritmos", {"P1": 1.0, "P2": None}, regras_p1_p2, None)
    texto = formatar_relatorio(gerar_relatorio(materia))
    assert "Recuperação" in texto


# previsao

def test_previsao_sem_historico(tmp_path, regras_calculo):
    with pytest.raises(PrevisaoIndisponivelError):
        gerar_previsao(materia_calculo(regras_calculo), "calculo1", tmp_path)


def test_previsao_com_historico(tmp_path, regras_calculo):
    escrever_historico(tmp_path)
    materia = materia_calculo(regras_calculo)
    predicao = gerar_previsao(materia, "calculo1", tmp_path)
    assert "Trabalho" in predicao.notas_previstas
    assert 0 <= predicao.chance_aprovacao <= 1


def test_texto_da_previsao(tmp_path, regras_calculo):
    escrever_historico(tmp_path)
    materia = materia_calculo(regras_calculo)
    predicao = gerar_previsao(materia, "calculo1", tmp_path)
    texto = formatar_previsao(materia, predicao)
    assert "Previsão" in texto
    assert "Chance de aprovação direta" in texto


def test_texto_da_previsao_sem_pendentes(tmp_path, regras_calculo):
    escrever_historico(tmp_path)
    notas = {"P1": 8.0, "P2": 8.0, "Trabalho": 8.0}
    materia = materia_calculo(regras_calculo, notas=notas)
    predicao = gerar_previsao(materia, "calculo1", tmp_path)
    assert "Nada a prever" in formatar_previsao(materia, predicao)
