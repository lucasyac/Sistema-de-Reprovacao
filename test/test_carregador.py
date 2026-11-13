# Testes do carregador (leitura e validacao dos arquivos)

import json
import pytest
from sistema.carregador import (
    DadosInvalidosError,
    buscar_historico,
    carregar_frequencia,
    carregar_materia,
    carregar_notas,
    carregar_regras,
    carregar_regras_da_materia,
    normalizar_nome,
    validar_consistencia,
)

CSV_CALCULO = (
    "disciplina,avaliacao,nota,aulas_totais,faltas\n"
    "Calculo 1,P1,4,60,8\n"
    "Calculo 1,P2,5,,\n"
    "Calculo 1,Trabalho,,,\n"
)
REGRAS_CALCULO = {
    "media_aprovacao": 6.0,
    "avaliacoes": {"P1": 0.3, "P2": 0.3, "Trabalho": 0.4},
}


def escrever(pasta, nome, texto):
    caminho = pasta / nome
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def escrever_json(pasta, nome, conteudo):
    return escrever(pasta, nome, json.dumps(conteudo))


# carregar_notas

def test_carregar_notas_valido(arquivos_validos):
    csv, _ = arquivos_validos
    esperado = {"Calculo I": {"P1": 4.0, "P2": 5.0, "Trabalho": None}}
    assert carregar_notas(csv) == esperado


def test_nota_com_virgula(tmp_path):
    csv = escrever(tmp_path, "n.csv", 'disciplina,avaliacao,nota\nCalculo,P1,"7,5"\n')
    assert carregar_notas(csv)["Calculo"]["P1"] == 7.5


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(DadosInvalidosError):
        carregar_notas(tmp_path / "nao_existe.csv")


def test_csv_sem_coluna_nota(tmp_path):
    csv = escrever(tmp_path, "n.csv", "disciplina,avaliacao\nCalculo,P1\n")
    with pytest.raises(DadosInvalidosError):
        carregar_notas(csv)


def test_csv_so_com_cabecalho(tmp_path):
    csv = escrever(tmp_path, "n.csv", "disciplina,avaliacao,nota\n")
    with pytest.raises(DadosInvalidosError):
        carregar_notas(csv)


@pytest.mark.parametrize("nota", ["11", "-1", "abc"])
def test_nota_invalida(tmp_path, nota):
    csv = escrever(tmp_path, "n.csv", f"disciplina,avaliacao,nota\nCalculo,P1,{nota}\n")
    with pytest.raises(DadosInvalidosError):
        carregar_notas(csv)


def test_avaliacao_repetida(tmp_path):
    texto = "disciplina,avaliacao,nota\nCalculo,P1,4\nCalculo,P1,5\n"
    csv = escrever(tmp_path, "n.csv", texto)
    with pytest.raises(DadosInvalidosError):
        carregar_notas(csv)


# carregar_regras

def test_carregar_regras_valido(arquivos_validos):
    _, js = arquivos_validos
    regras = carregar_regras(js)
    assert regras["Calculo I"]["avaliacoes"]["Trabalho"] == 0.4


def test_media_padrao_e_6(tmp_path):
    js = escrever_json(tmp_path, "r.json", {"Calculo": {"avaliacoes": {"P1": 1}}})
    assert carregar_regras(js)["Calculo"]["media_aprovacao"] == 6.0


def test_json_quebrado(tmp_path):
    js = escrever(tmp_path, "r.json", "{ isso nao e json")
    with pytest.raises(DadosInvalidosError):
        carregar_regras(js)


def test_pesos_nao_somam_1(tmp_path):
    regras = {"Calculo": {"avaliacoes": {"P1": 0.5, "P2": 0.3}}}
    js = escrever_json(tmp_path, "r.json", regras)
    with pytest.raises(DadosInvalidosError):
        carregar_regras(js)


def test_peso_zero(tmp_path):
    regras = {"Calculo": {"avaliacoes": {"P1": 0, "P2": 1}}}
    js = escrever_json(tmp_path, "r.json", regras)
    with pytest.raises(DadosInvalidosError):
        carregar_regras(js)


def test_regra_sem_avaliacoes(tmp_path):
    js = escrever_json(tmp_path, "r.json", {"Calculo": {"media_aprovacao": 6}})
    with pytest.raises(DadosInvalidosError):
        carregar_regras(js)


# carregar_regras_da_materia

def test_regras_de_uma_materia(tmp_path):
    js = escrever_json(tmp_path, "r.json", REGRAS_CALCULO)
    assert carregar_regras_da_materia(js, "qualquer")["avaliacoes"]["P1"] == 0.3


def test_regras_achadas_pelo_nome_sem_acento(tmp_path):
    js = escrever_json(tmp_path, "r.json", {"Cálculo I": REGRAS_CALCULO})
    regras = carregar_regras_da_materia(js, "calculo i")
    assert regras["avaliacoes"]["Trabalho"] == 0.4


def test_materia_sem_regras(tmp_path):
    js = escrever_json(tmp_path, "r.json", {"Calculo": REGRAS_CALCULO})
    with pytest.raises(DadosInvalidosError):
        carregar_regras_da_materia(js, "Fisica")


# carregar_frequencia

def test_carregar_frequencia(tmp_path):
    csv = escrever(tmp_path, "n.csv", CSV_CALCULO)
    assert carregar_frequencia(csv) == {"Calculo 1": {"aulas_totais": 60, "faltas": 8}}


def test_frequencia_sem_as_colunas(arquivos_validos):
    csv, _ = arquivos_validos
    assert carregar_frequencia(csv) == {}


def test_faltas_maior_que_aulas(tmp_path):
    texto = "disciplina,avaliacao,nota,aulas_totais,faltas\nCalculo,P1,4,10,20\n"
    csv = escrever(tmp_path, "n.csv", texto)
    with pytest.raises(DadosInvalidosError):
        carregar_frequencia(csv)


def test_so_faltas_sem_aulas(tmp_path):
    texto = "disciplina,avaliacao,nota,aulas_totais,faltas\nCalculo,P1,4,,3\n"
    csv = escrever(tmp_path, "n.csv", texto)
    with pytest.raises(DadosInvalidosError):
        carregar_frequencia(csv)


# validar_consistencia

def test_consistencia_ok():
    notas = {"Calculo": {"P1": 4.0, "P2": None}}
    regras = {"Calculo": {"media_aprovacao": 6.0, "avaliacoes": {"P1": 0.5, "P2": 0.5}}}
    validar_consistencia(notas, regras)


def test_disciplina_sem_regras():
    with pytest.raises(DadosInvalidosError):
        validar_consistencia({"Fisica": {"P1": 4.0}}, {})


def test_avaliacao_fora_das_regras():
    notas = {"Calculo": {"P1": 4.0, "P3": 5.0}}
    regras = {"Calculo": {"media_aprovacao": 6.0, "avaliacoes": {"P1": 1.0}}}
    with pytest.raises(DadosInvalidosError):
        validar_consistencia(notas, regras)


# carregar_materia

def test_carregar_materia(tmp_path):
    csv = escrever(tmp_path, "calculo1.csv", CSV_CALCULO)
    js = escrever_json(tmp_path, "calculo1.json", REGRAS_CALCULO)
    materia = carregar_materia(csv, js)
    assert materia.nome == "Calculo 1"
    assert materia.notas["P2"] == 5.0
    assert materia.frequencia == {"aulas_totais": 60, "faltas": 8}


def test_csv_com_duas_materias(tmp_path):
    texto = "disciplina,avaliacao,nota\nCalculo,P1,4\nFisica,P1,5\n"
    csv = escrever(tmp_path, "n.csv", texto)
    js = escrever_json(tmp_path, "r.json", REGRAS_CALCULO)
    with pytest.raises(DadosInvalidosError):
        carregar_materia(csv, js)


# historico

def test_normalizar_nome():
    assert normalizar_nome("Cálculo 1") == "calculo1"
    assert normalizar_nome("fisica_1") == "fisica1"


def test_buscar_historico(tmp_path):
    escrever(tmp_path, "calculo1.csv", "aluno,P1,P2\nA1,5.5,6\nA2,7,8\n")
    historico = buscar_historico(tmp_path, "Cálculo 1")
    assert historico == [{"P1": 5.5, "P2": 6.0}, {"P1": 7.0, "P2": 8.0}]


def test_historico_de_materia_inexistente(tmp_path):
    assert buscar_historico(tmp_path, "Fisica") is None


def test_pasta_de_historico_inexistente(tmp_path):
    assert buscar_historico(tmp_path / "nao_existe", "Fisica") is None
