# Testes da fachada (padrao Facade)

import pytest
from sistema.fachada import PrevisaoIndisponivelError, SistemaReprovacao


def escrever_historico(pasta, nome):
    linhas = ["aluno,P1,P2,Trabalho"]
    for numero in range(12):
        nota = 2 + numero * 0.5
        linhas.append(f"A{numero},{nota},{nota},{nota}")
    (pasta / f"{nome}.csv").write_text("\n".join(linhas), encoding="utf-8")


def test_materias_em_ordem(tmp_path):
    escrever_historico(tmp_path, "fisica1")
    escrever_historico(tmp_path, "calculo1")
    sistema = SistemaReprovacao(tmp_path)
    assert sistema.materias_com_previsao() == ["calculo1", "fisica1"]


def test_sem_pasta_de_historico(tmp_path):
    sistema = SistemaReprovacao(tmp_path / "nao_existe")
    assert sistema.materias_com_previsao() == []


def test_relatorio_de_situacao(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    sistema = SistemaReprovacao(tmp_path)
    materia = sistema.carregar_materia(csv, js)
    texto = sistema.relatorio_situacao(materia)
    assert "2,70" in texto
    assert "EM RISCO" in texto


def test_relatorio_de_previsao(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    # o arquivo de notas da fixture se chama notas.csv, entao o historico
    # precisa do mesmo nome, em outra pasta para nao sobrescrever
    pasta = tmp_path / "historico"
    pasta.mkdir()
    escrever_historico(pasta, "notas")
    sistema = SistemaReprovacao(pasta)
    materia = sistema.carregar_materia(csv, js)
    assert "Chance de aprovação" in sistema.relatorio_previsao(materia, csv)


def test_previsao_sem_historico(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    sistema = SistemaReprovacao(tmp_path / "vazia")
    materia = sistema.carregar_materia(csv, js)
    with pytest.raises(PrevisaoIndisponivelError):
        sistema.relatorio_previsao(materia, csv)
