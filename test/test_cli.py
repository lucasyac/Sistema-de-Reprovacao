# Testes do terminal (menu e opcoes)

import os
import subprocess
import sys
from pathlib import Path

from sistema.cli import executar_terminal

RAIZ = Path(__file__).resolve().parent.parent


def rodar_menu(respostas, pasta_historico):
    "Roda o menu com as respostas combinadas e devolve tudo que foi escrito."
    respostas = iter(respostas)
    textos = []
    executar_terminal(pasta_historico, lambda pergunta: next(respostas), textos.append)
    return "\n".join(textos)


def test_sair(tmp_path):
    assert "Até logo!" in rodar_menu(["0"], tmp_path)


def test_opcao_invalida(tmp_path):
    saida = rodar_menu(["9", "0"], tmp_path)
    assert "Opção inválida" in saida


def test_ver_situacao(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    saida = rodar_menu(["1", str(csv), str(js), "0"], tmp_path)
    assert "2,70" in saida
    assert "EM RISCO" in saida


def test_situacao_com_arquivo_inexistente(tmp_path):
    saida = rodar_menu(["1", "nao_existe.csv", "nao_existe.json", "0"], tmp_path)
    assert "Erro:" in saida


def test_voltar_ao_menu(tmp_path):
    saida = rodar_menu(["1", "0", "0"], tmp_path)
    assert "Até logo!" in saida
    assert "Erro:" not in saida


def test_previsao_sem_historico(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    saida = rodar_menu(["2", str(csv), str(js), "0"], tmp_path)
    assert "Previsão indisponível" in saida


def test_python_m_sistema():
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
    resultado = subprocess.run(
        [sys.executable, "-m", "sistema"],
        input="0\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=RAIZ,
        env=ambiente,
    )
    assert resultado.returncode == 0
    assert "SISTEMA DE REPROVAÇÃO" in resultado.stdout
