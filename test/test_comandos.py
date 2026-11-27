# Testes dos comandos do menu (padrao Command)

import pytest
from sistema.cli import COMANDOS, mensagem_opcao_invalida, montar_menu
from sistema.comandos import (
    Comando,
    ComandoPrevisao,
    ComandoSair,
    ComandoSituacao,
    Terminal,
)
from sistema.fachada import SistemaReprovacao


def criar_terminal(pasta, respostas=()):
    "Terminal de teste: responde com a lista e guarda o que foi escrito."
    respostas = iter(respostas)
    textos = []
    sistema = SistemaReprovacao(pasta)
    terminal = Terminal(sistema, lambda pergunta: next(respostas), textos.append)
    return terminal, textos


def test_comando_base_nao_faz_nada(tmp_path):
    terminal, _ = criar_terminal(tmp_path)
    with pytest.raises(NotImplementedError):
        Comando().executar(terminal)


def test_sair_fecha_o_menu(tmp_path):
    terminal, textos = criar_terminal(tmp_path)
    assert ComandoSair().executar(terminal) is False
    assert textos == ["Até logo!"]


def test_situacao_mantem_o_menu(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    terminal, textos = criar_terminal(tmp_path, [str(csv), str(js)])
    assert ComandoSituacao().executar(terminal) is True
    assert "EM RISCO" in textos[-1]


def test_enter_reaproveita_os_arquivos(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    terminal, textos = criar_terminal(tmp_path, [str(csv), str(js), "", ""])
    ComandoSituacao().executar(terminal)
    textos.clear()
    ComandoSituacao().executar(terminal)
    assert "EM RISCO" in textos[-1]


def test_previsao_sem_historico(tmp_path, arquivos_validos):
    csv, js = arquivos_validos
    terminal, textos = criar_terminal(tmp_path / "vazia", [str(csv), str(js)])
    assert ComandoPrevisao().executar(terminal) is True
    assert "Previsão indisponível" in textos[-1]


def test_teclas_nao_se_repetem():
    teclas = [comando.tecla for comando in COMANDOS]
    assert len(teclas) == len(set(teclas))


def test_menu_lista_todos_os_comandos():
    menu = montar_menu(COMANDOS)
    for comando in COMANDOS:
        assert f"{comando.tecla} - {comando.descricao}" in menu


def test_mensagem_de_opcao_invalida():
    assert mensagem_opcao_invalida(COMANDOS) == "Opção inválida. Digite 1, 2 ou 0."
