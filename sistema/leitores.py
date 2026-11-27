"""Leitura dos arquivos de entrada, usando o padrao Template Method."""

import csv
import json
from pathlib import Path


class DadosInvalidosError(ValueError):
    """Arquivo de entrada com formato ou conteudo invalido."""


class Leitor:
    """ler() define os passos da leitura. Cada formato muda apenas
    ler_conteudo() e validar()."""

    def ler(self, caminho):
        caminho = Path(caminho)
        self.verificar_existe(caminho)
        conteudo = self.ler_conteudo(caminho)
        self.validar(caminho, conteudo)
        return conteudo

    def verificar_existe(self, caminho):
        if not caminho.is_file():
            raise DadosInvalidosError(f"Arquivo não encontrado: {caminho}")

    def ler_conteudo(self, caminho):
        raise NotImplementedError

    def validar(self, caminho, conteudo):
        raise NotImplementedError


class LeitorCSV(Leitor):
    """Devolve (colunas, linhas). Cada linha e um par (numero da linha, dados)."""

    def __init__(self, colunas_obrigatorias=()):
        self.colunas_obrigatorias = colunas_obrigatorias

    def ler_conteudo(self, caminho):
        with caminho.open(newline="", encoding="utf-8-sig") as arquivo:
            leitor = csv.DictReader(arquivo)
            colunas = [coluna.strip() for coluna in (leitor.fieldnames or [])]
            linhas = []
            for numero, linha in enumerate(leitor, start=2):
                limpa = {
                    chave.strip(): (valor or "").strip()
                    for chave, valor in linha.items()
                    if chave
                }
                linhas.append((numero, limpa))
        return colunas, linhas

    def validar(self, caminho, conteudo):
        colunas, _ = conteudo
        faltando = [c for c in self.colunas_obrigatorias if c not in colunas]
        if faltando:
            raise DadosInvalidosError(
                f"{caminho.name}: coluna(s) obrigatória(s) ausente(s): "
                f"{', '.join(faltando)}"
            )


class LeitorJSON(Leitor):
    """Devolve o objeto (dicionario) do arquivo JSON."""

    def ler_conteudo(self, caminho):
        try:
            return json.loads(caminho.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as erro:
            raise DadosInvalidosError(f"{caminho.name}: JSON inválido ({erro}).") from None

    def validar(self, caminho, conteudo):
        if not isinstance(conteudo, dict) or not conteudo:
            raise DadosInvalidosError(f"{caminho.name}: esperado um objeto JSON com as regras.")
