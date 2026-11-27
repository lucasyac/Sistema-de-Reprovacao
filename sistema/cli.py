"""Terminal interativo para o aluno"""

import argparse
import sys
from pathlib import Path

#Permite também rodar o arquivo diretamente (python sistema/cli.py)
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sistema.comandos import ComandoPrevisao, ComandoSair, ComandoSituacao, Terminal
from sistema.fachada import SistemaReprovacao

RAIZ = Path(__file__).resolve().parent.parent
HISTORICO_PADRAO = RAIZ / "dados" / "historico"

LINHA = "=" * 62

#Para criar uma opcao nova: fazer a classe em comandos.py e colocar nesta lista
COMANDOS = [ComandoSituacao(), ComandoPrevisao(), ComandoSair()]


def montar_menu(comandos):
    linhas = ["", LINHA, " SISTEMA DE REPROVAÇÃO", LINHA]
    for comando in comandos:
        linhas.append(f" {comando.tecla} - {comando.descricao}")
    linhas.append(LINHA)
    return "\n".join(linhas)


def mensagem_opcao_invalida(comandos):
    teclas = [comando.tecla for comando in comandos]
    return f"Opção inválida. Digite {', '.join(teclas[:-1])} ou {teclas[-1]}."


def executar_terminal(pasta_historico, entrada=None, saida=None):
    """Laço do menu. Termina quando o aluno escolhe sair."""
    entrada = entrada or input  #resolvidos aqui
    saida = saida or print
    terminal = Terminal(SistemaReprovacao(pasta_historico), entrada, saida)
    opcoes = {comando.tecla: comando for comando in COMANDOS}

    continuar = True
    while continuar:
        saida(montar_menu(COMANDOS))
        comando = opcoes.get(entrada("Escolha uma opção: ").strip())
        if comando is None:
            saida(mensagem_opcao_invalida(COMANDOS))
        else:
            continuar = comando.executar(terminal)


#Ponto de entrada
def construir_parser():
    parser = argparse.ArgumentParser(
        prog="python -m sistema",
        description="Terminal para o aluno acompanhar sua situação em uma matéria e a chance de aprovação.",
    )
    parser.add_argument("--historico", default=str(HISTORICO_PADRAO),
                        help="pasta com um <matéria>.csv de turmas passadas por matéria "
                             "(padrão: dados/historico)")
    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)
    try:
        executar_terminal(args.historico)
    except (EOFError, KeyboardInterrupt):  # Ctrl+D / Ctrl+Z / Ctrl+C
        print("\nAté logo!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

