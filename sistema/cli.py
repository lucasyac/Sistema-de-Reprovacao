"""Terminal interativo para o aluno"""

import argparse
import sys
from pathlib import Path

#Permite também rodar o arquivo diretamente (python sistema/cli.py)
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sistema.fachada import (
    DadosInvalidosError,
    PrevisaoIndisponivelError,
    SistemaReprovacao,
)

RAIZ = Path(__file__).resolve().parent.parent
HISTORICO_PADRAO = RAIZ / "dados" / "historico"

LINHA = "=" * 62
MENU = f"""
{LINHA}
 SISTEMA DE REPROVAÇÃO
{LINHA}
 1 - Ver minha situação em uma matéria
 2 - Prever minhas notas e a chance de aprovação
 0 - Sair
{LINHA}"""



#Perguntas ao aluno 
def _pedir_caminho(entrada, pergunta, ultimo):
    """Pede o caminho de um arquivo. Enter reaproveita o ultimo; '0' volta ao menu."""
    dica = f"Enter = usar o último ({Path(ultimo).name}), 0 = voltar" if ultimo else "0 = voltar"
    texto = entrada(f"{pergunta} [{dica}]: ").strip().strip("\"'")
    if texto == "0":
        return None
    return texto or ultimo


def _pedir_materia(sistema, entrada, saida, sessao):
    """Pede o CSV de notas e o JSON de regras e carrega UMA matéria. Devolve (Materia, caminho do CSV) ou None se o aluno voltou ou houve erro.
    sessao guarda os ultimos arquivos usados com sucesso.
    """
    saida("\nUma matéria por vez. Modelos de arquivo: pasta exemplos/ (calculo1.csv e calculo1.json).")
    csv = _pedir_caminho(entrada, "Arquivo CSV com suas notas", sessao.get("csv"))
    if not csv:
        return None
    regras = _pedir_caminho(entrada, "Arquivo JSON com as regras da matéria (pesos)", sessao.get("json"))
    if not regras:
        return None
    try:
        materia = sistema.carregar_materia(csv, regras)
    except DadosInvalidosError as erro:
        saida(f"Erro: {erro}")
        return None
    sessao["csv"], sessao["json"] = csv, regras
    return materia, csv


#Opcoes do menu
def _opcao_situacao(sistema, sessao, entrada, saida):
    carregada = _pedir_materia(sistema, entrada, saida, sessao)
    if carregada:
        materia, _ = carregada
        saida("\n" + sistema.relatorio_situacao(materia))


def _opcao_previsao(sistema, sessao, entrada, saida):
    disponiveis = sistema.materias_com_previsao()
    saida("\nMatérias com previsão disponível (turmas passadas):")
    for nome in disponiveis:
        saida(f"  - {nome}")
    if not disponiveis:
        saida("  (nenhuma: não há arquivos na pasta de histórico)")
    saida("O seu arquivo CSV de notas deve ter o MESMO NOME da matéria (ex.: calculo1.csv).")

    carregada = _pedir_materia(sistema, entrada, saida, sessao)
    if not carregada:
        return
    materia, csv = carregada
    try:
        texto = sistema.relatorio_previsao(materia, csv)
    except (PrevisaoIndisponivelError, DadosInvalidosError) as erro:
        saida(f"Previsão indisponível: {erro}")
        return
    saida("\n" + texto)


def executar_terminal(pasta_historico, entrada=None, saida=None):
    """Laço do menu. Termina quando o aluno escolhe sair."""
    entrada = entrada or input  #resolvidos aqui
    saida = saida or print
    sessao = {}  #ultimos arquivos usados, para nao digitar os caminhos de novo
    sistema = SistemaReprovacao(pasta_historico)
    while True:
        saida(MENU)
        opcao = entrada("Escolha uma opção: ").strip()
        if opcao == "1":
            _opcao_situacao(sistema, sessao, entrada, saida)
        elif opcao == "2":
            _opcao_previsao(sistema, sessao, entrada, saida)
        elif opcao == "0":
            saida("Até logo!")
            return
        else:
            saida("Opção inválida. Digite 1, 2 ou 0.")


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

