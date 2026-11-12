"""Leitura e validacao dos arquivos de entrada (CSV e JSON)."""

import csv
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class DadosInvalidosError(ValueError):
    """Arquivo de entrada com formato ou conteudo invalido."""


NOTA_MINIMA, NOTA_MAXIMA = 0.0, 10.0



#AUXILIARES
def _ler_csv(caminho, colunas_obrigatorias):
    caminho = Path(caminho)
    if not caminho.is_file():
        raise DadosInvalidosError(f"Arquivo não encontrado: {caminho}")

    with caminho.open(newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = [c.strip() for c in (leitor.fieldnames or [])]
        faltando = [c for c in colunas_obrigatorias if c not in colunas]
        if faltando:
            raise DadosInvalidosError(
                f"{caminho.name}: coluna(s) obrigatória(s) ausente(s): "
                f"{', '.join(faltando)}"
            )
        linhas = []
        for numero, linha in enumerate(leitor, start=2): 
            limpa = {
                (k or "").strip(): (v or "").strip() for k, v in linha.items() if k
            }
            linhas.append((numero, limpa))
    return caminho.name, colunas, linhas


def converter_nota(texto, onde):
    """'' -> None (pendente); aceita vírgula decimal; exige 0 <= nota <= 10."""
    if texto == "":
        return None
    try:
        nota = float(texto.replace(",", "."))
    except ValueError:
        raise DadosInvalidosError(f"{onde}: nota inválida '{texto}'.") from None
    if not NOTA_MINIMA <= nota <= NOTA_MAXIMA:
        raise DadosInvalidosError(f"{onde}: nota {nota:g} fora do intervalo 0 a 10.")
    return nota


def _converter_inteiro(texto, onde, campo):
    try:
        valor = int(texto)
    except ValueError:
        raise DadosInvalidosError(f"{onde}: {campo} inválido '{texto}'.") from None
    if valor < 0:
        raise DadosInvalidosError(f"{onde}: {campo} não pode ser negativo.")
    return valor


#REGRAS DO PROFESSOR
def _ler_json(caminho):
    caminho = Path(caminho)
    if not caminho.is_file():
        raise DadosInvalidosError(f"Arquivo não encontrado: {caminho}")
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as erro:
        raise DadosInvalidosError(f"{caminho.name}: JSON inválido ({erro}).") from None
    if not isinstance(bruto, dict) or not bruto:
        raise DadosInvalidosError(f"{caminho.name}: esperado um objeto JSON com as regras.")
    return caminho.name, bruto


def _validar_regra(conteudo, onde):
    """Valida as regras de UMA materia e devolve {media_aprovacao, avaliacoes}."""
    if not isinstance(conteudo, dict) or "avaliacoes" not in conteudo:
        raise DadosInvalidosError(f"{onde}: campo 'avaliacoes' é obrigatório.")

    media = conteudo.get("media_aprovacao", 6.0)
    if isinstance(media, bool) or not isinstance(media, (int, float)):
        raise DadosInvalidosError(f"{onde}: 'media_aprovacao' deve ser numérica.")
    if not 0 < media <= NOTA_MAXIMA:
        raise DadosInvalidosError(f"{onde}: 'media_aprovacao' deve estar entre 0 e 10.")

    avaliacoes = conteudo["avaliacoes"]
    if not isinstance(avaliacoes, dict) or not avaliacoes:
        raise DadosInvalidosError(f"{onde}: 'avaliacoes' deve ter ao menos uma avaliação.")
    pesos = {}
    for nome, peso in avaliacoes.items():
        if isinstance(peso, bool) or not isinstance(peso, (int, float)) or peso <= 0:
            raise DadosInvalidosError(f"{onde}: peso de '{nome}' deve ser um número > 0.")
        pesos[nome] = float(peso)
    if abs(sum(pesos.values()) - 1.0) > 1e-6:
        raise DadosInvalidosError(f"{onde}: os pesos devem somar 1 (somam {sum(pesos.values()):g}).")
    return {"media_aprovacao": float(media), "avaliacoes": pesos}


def carregar_regras(caminho):
    """Le o JSON com várias materias: {disciplina: {media_aprovacao, avaliacoes}}."""
    nome, bruto = _ler_json(caminho)
    return {
        disciplina: _validar_regra(conteudo, f"{nome}, disciplina '{disciplina}'")
        for disciplina, conteudo in bruto.items()
    }


def carregar_regras_da_materia(caminho, materia):
    """Le o JSON de UMA matéria. Aceita dois formatos:"""
    nome, bruto = _ler_json(caminho)
    if "avaliacoes" in bruto:
        return _validar_regra(bruto, nome)

    regras = carregar_regras(caminho)
    por_nome = {normalizar_nome(disciplina): regra for disciplina, regra in regras.items()}
    if normalizar_nome(materia) not in por_nome:
        raise DadosInvalidosError(
            f"{nome}: não há regras para a matéria '{materia}' (o arquivo tem: {', '.join(regras)})."
        )
    return por_nome[normalizar_nome(materia)]



# Notas e faltas do aluno (CSV)
def carregar_notas(caminho):
    """Le o CSV do aluno. Devolve {disciplina: {avaliacao: nota | None}}."""
    nome, _, linhas = _ler_csv(caminho, ["disciplina", "avaliacao", "nota"])
    notas = {}
    for numero, linha in linhas:
        onde = f"{nome}, linha {numero}"
        disciplina, avaliacao = linha["disciplina"], linha["avaliacao"]
        if not disciplina or not avaliacao:
            raise DadosInvalidosError(f"{onde}: 'disciplina' e 'avaliacao' são obrigatórias.")
        por_disciplina = notas.setdefault(disciplina, {})
        if avaliacao in por_disciplina:
            raise DadosInvalidosError(f"{onde}: avaliação '{avaliacao}' repetida em '{disciplina}'.")
        por_disciplina[avaliacao] = converter_nota(linha["nota"], onde)
    if not notas:
        raise DadosInvalidosError(f"{nome}: o arquivo não tem nenhuma nota.")
    return notas


def carregar_frequencia(caminho):
    """Le as colunas opcionais aulas_totais e faltas do CSV do aluno."""
    nome, colunas, linhas = _ler_csv(caminho, ["disciplina"])
    frequencia = {}
    if "aulas_totais" not in colunas or "faltas" not in colunas:
        return frequencia

    for numero, linha in linhas:
        onde = f"{nome}, linha {numero}"
        if linha["aulas_totais"] == "" and linha["faltas"] == "":
            continue
        if linha["aulas_totais"] == "" or linha["faltas"] == "":
            raise DadosInvalidosError(f"{onde}: informe 'aulas_totais' e 'faltas' juntos.")
        atual = {
            "aulas_totais": _converter_inteiro(linha["aulas_totais"], onde, "aulas_totais"),
            "faltas": _converter_inteiro(linha["faltas"], onde, "faltas"),
        }
        if atual["aulas_totais"] == 0:
            raise DadosInvalidosError(f"{onde}: 'aulas_totais' deve ser maior que zero.")
        if atual["faltas"] > atual["aulas_totais"]:
            raise DadosInvalidosError(f"{onde}: 'faltas' maior que 'aulas_totais'.")
        anterior = frequencia.setdefault(linha["disciplina"], atual)
        if anterior != atual:
            raise DadosInvalidosError(
                f"{onde}: valores de faltas/aulas diferentes para '{linha['disciplina']}'."
            )
    return frequencia


def validar_consistencia(notas, regras):
    """Confere se as disciplinas e avaliações do CSV existem no JSON de regras."""
    for disciplina, avaliacoes in notas.items():
        if disciplina not in regras:
            raise DadosInvalidosError(f"Disciplina '{disciplina}' não tem regras no JSON.")
        desconhecidas = set(avaliacoes) - set(regras[disciplina]["avaliacoes"])
        if desconhecidas:
            raise DadosInvalidosError(
                f"Disciplina '{disciplina}': avaliação(ões) fora das regras: "
                f"{', '.join(sorted(desconhecidas))}."
            )



#Uma materia por vez: CSV de notas + JSON de regras
@dataclass
class Materia:
    nome: str                       
    notas: dict                     
    regras: dict                    
    frequencia: Optional[dict]      


def carregar_materia(caminho_notas, caminho_regras):
    """Le e valida o CSV do aluno (UMA materia) e o JSON com as regras dela."""
    notas = carregar_notas(caminho_notas)
    if len(notas) != 1:
        raise DadosInvalidosError(
            f"{Path(caminho_notas).name}: o arquivo tem {len(notas)} matérias ({', '.join(notas)}). "
            "Envie um arquivo por matéria."
        )
    (nome, notas_da_materia), = notas.items()
    regras = carregar_regras_da_materia(caminho_regras, nome)
    validar_consistencia({nome: notas_da_materia}, {nome: regras})
    return Materia(nome, notas_da_materia, regras, carregar_frequencia(caminho_notas).get(nome))


#Historico de turmas passadas: um CSV por materia
def normalizar_nome(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return "".join(c for c in sem_acento.casefold() if c not in " _-")


def listar_materias_com_historico(pasta):
    pasta = Path(pasta)
    if not pasta.is_dir():
        return {}
    return {normalizar_nome(arquivo.stem): arquivo for arquivo in sorted(pasta.glob("*.csv"))}


def buscar_historico(pasta, materia):
    caminho = listar_materias_com_historico(pasta).get(normalizar_nome(materia))
    if caminho is None:
        return None

    nome, colunas, linhas = _ler_csv(caminho, [])
    avaliacoes = [c for c in colunas if c and c.casefold() != "aluno"]
    if not avaliacoes:
        raise DadosInvalidosError(f"{nome}: nenhuma coluna de avaliação encontrada.")
    return [
        {a: converter_nota(linha.get(a, ""), f"{nome}, linha {numero}") for a in avaliacoes}
        for numero, linha in linhas
    ]
