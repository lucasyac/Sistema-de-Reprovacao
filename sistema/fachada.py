"""Facade: um ponto unico para o terminal usar o sistema."""

from pathlib import Path

from sistema.carregador import carregar_materia, listar_materias_com_historico
from sistema.leitores import DadosInvalidosError
from sistema.predicao import PrevisaoIndisponivelError
from sistema.relatorio import (
    formatar_previsao,
    formatar_relatorio,
    gerar_previsao,
    gerar_relatorio,
)


class SistemaReprovacao:
    """Junta o carregador, o relatorio e a previsao em poucos metodos."""

    def __init__(self, pasta_historico):
        self.pasta_historico = pasta_historico

    def carregar_materia(self, caminho_notas, caminho_regras):
        return carregar_materia(caminho_notas, caminho_regras)

    def materias_com_previsao(self):
        arquivos = listar_materias_com_historico(self.pasta_historico).values()
        return sorted(arquivo.stem for arquivo in arquivos)

    def relatorio_situacao(self, materia):
        return formatar_relatorio(gerar_relatorio(materia))

    def relatorio_previsao(self, materia, caminho_notas):
        # o historico e achado pelo nome do arquivo de notas
        nome_do_arquivo = Path(caminho_notas).stem
        predicao = gerar_previsao(materia, nome_do_arquivo, self.pasta_historico)
        return formatar_previsao(materia, predicao)
