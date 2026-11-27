# Testes dos leitores (padrao Template Method)

import pytest
from sistema.leitores import DadosInvalidosError, Leitor, LeitorCSV, LeitorJSON


class LeitorQueAnota(Leitor):
    "Leitor de mentira que guarda a ordem em que os passos foram chamados."

    def __init__(self):
        self.passos = []

    def verificar_existe(self, caminho):
        self.passos.append("verificar")

    def ler_conteudo(self, caminho):
        self.passos.append("ler")
        return "conteudo"

    def validar(self, caminho, conteudo):
        self.passos.append("validar")


def escrever(pasta, nome, texto):
    caminho = pasta / nome
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def test_ordem_dos_passos():
    leitor = LeitorQueAnota()
    assert leitor.ler("qualquer.txt") == "conteudo"
    assert leitor.passos == ["verificar", "ler", "validar"]


def test_leitor_base_nao_le_nada(tmp_path):
    arquivo = escrever(tmp_path, "a.txt", "x")
    with pytest.raises(NotImplementedError):
        Leitor().ler(arquivo)


@pytest.mark.parametrize("leitor", [LeitorCSV(), LeitorJSON()])
def test_arquivo_inexistente(tmp_path, leitor):
    with pytest.raises(DadosInvalidosError):
        leitor.ler(tmp_path / "nao_existe")


def test_ler_csv(tmp_path):
    arquivo = escrever(tmp_path, "a.csv", "nome , nota\nAna, 7\n")
    colunas, linhas = LeitorCSV(["nome"]).ler(arquivo)
    assert colunas == ["nome", "nota"]
    assert linhas == [(2, {"nome": "Ana", "nota": "7"})]


def test_csv_sem_coluna_obrigatoria(tmp_path):
    arquivo = escrever(tmp_path, "a.csv", "nome\nAna\n")
    with pytest.raises(DadosInvalidosError):
        LeitorCSV(["nota"]).ler(arquivo)


def test_ler_json(tmp_path):
    arquivo = escrever(tmp_path, "a.json", '{"P1": 1}')
    assert LeitorJSON().ler(arquivo) == {"P1": 1}


@pytest.mark.parametrize("texto", ["{ quebrado", "[1, 2]", "{}"])
def test_json_invalido(tmp_path, texto):
    arquivo = escrever(tmp_path, "a.json", texto)
    with pytest.raises(DadosInvalidosError):
        LeitorJSON().ler(arquivo)
