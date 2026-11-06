# Dados de exemplo que os testes das histórias usam (todos fictícios)

import json
import pytest


@pytest.fixture
def regras_calculo():
    "Regras de Calculo I: P1 e P2 valem 30% cada, o trabalho vale 40%."
    return {
        "media_aprovacao": 6.0,
        "avaliacoes": {"P1": 0.3, "P2": 0.3, "Trabalho": 0.4},
    }


@pytest.fixture
def regras_p1_p2():
    "Regras com só duas provas de 50% cada."
    return {
        "media_aprovacao": 6.0,
        "avaliacoes": {"P1": 0.5, "P2": 0.5},
    }


@pytest.fixture
def arquivos_validos(tmp_path):
    "Cria um CSV e um JSON válidos de Calculo I e devolve os dois caminhos."
    caminho_csv = tmp_path / "notas.csv"
    caminho_csv.write_text(
        "disciplina,avaliacao,nota\n"
        "Calculo I,P1,4\n"
        "Calculo I,P2,5\n"
        "Calculo I,Trabalho,\n",  # nota vazia = avaliação pendente
        encoding="utf-8",
    )

    regras = {
        "Calculo I": {
            "media_aprovacao": 6.0,
            "avaliacoes": {"P1": 0.3, "P2": 0.3, "Trabalho": 0.4},
        }
    }
    caminho_json = tmp_path / "regras.json"
    caminho_json.write_text(json.dumps(regras), encoding="utf-8")

    return caminho_csv, caminho_json
