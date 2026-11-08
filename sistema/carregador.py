#Leitura e validacao dos arquivos de entrada (CSV e JSON).
import csv
import json
from pathlib import Path

class DadosInvalidosError(ValueError):
    """Arquivo de entrada com formato ou conteúdo inválido."""


NOTA_MINIMA, NOTA_MAXIMA = 0.0, 10.0



#AUXILIARES
def _ler_csv(caminho, colunas_obrigatorias):
    caminho = Path(caminho)
    if not caminho.is_file():
        raise DadosInvalidosError(f"Arquivo não encontrado: {caminho}")

    #descarta o  que o Excel costuma gravar no início do CSV.
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
        for numero, linha in enumerate(leitor, start=2):  # linha 1 = cabeçalho
            limpa = {
                (k or "").strip(): (v or "").strip() for k, v in linha.items() if k
            }
            linhas.append((numero, limpa))
    return caminho.name, colunas, linhas


def converter_nota(texto, onde):
    """'' -> None (pendente). aceita virgula decimal. exige 0 <= nota <= 10."""
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


# REGRAS DO PROFESSOR(JSON)-
def carregar_regras(caminho):
    """Le e valida o JSON de regras. Devolve {disciplina: {media_aprovacao, avaliacoes}}."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise DadosInvalidosError(f"Arquivo não encontrado: {caminho}")
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as erro:
        raise DadosInvalidosError(f"{caminho.name}: JSON inválido ({erro}).") from None

    if not isinstance(bruto, dict) or not bruto:
        raise DadosInvalidosError(f"{caminho.name}: esperado um objeto com disciplinas.")

    regras = {}
    for disciplina, conteudo in bruto.items():
        onde = f"{caminho.name}, disciplina '{disciplina}'"
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
            raise DadosInvalidosError(
                f"{onde}: os pesos devem somar 1 (somam {sum(pesos.values()):g})."
            )

        regras[disciplina] = {"media_aprovacao": float(media), "avaliacoes": pesos}
    return regras


#NOTAS E FALTAS DO ALUNO(CSV)
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
    """Le as colunas opcionais aulas_totais e faltas do CSV do aluno.
    Devolve {disciplina: {"aulas_totais": int, "faltas": int}}; disciplinas sem
    esses dados simplesmente nao aparecem no resultado.
    """
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


def carregar_historico(caminho):
    """Le o historico. Devolve {disciplina: [{avaliacao: nota | None}, ...]}.
    Todas as colunas alem de 'disciplina' e 'aluno' sao avaliacoes, na ordem
    em que aparecem no cabecalho.
    """
    nome, colunas, linhas = _ler_csv(caminho, ["disciplina"])
    avaliacoes = [c for c in colunas if c not in ("disciplina", "aluno")]
    if not avaliacoes:
        raise DadosInvalidosError(f"{nome}: nenhuma coluna de avaliação encontrada.")

    historico = {}
    for numero, linha in linhas:
        onde = f"{nome}, linha {numero}"
        if not linha["disciplina"]:
            raise DadosInvalidosError(f"{onde}: 'disciplina' é obrigatória.")
        historico.setdefault(linha["disciplina"], []).append(
            {a: converter_nota(linha.get(a, ""), onde) for a in avaliacoes}
        )
    if not historico:
        raise DadosInvalidosError(f"{nome}: o histórico está vazio.")

    for disciplina, alunos in historico.items():
        usadas = [a for a in avaliacoes if any(aluno[a] is not None for aluno in alunos)]
        historico[disciplina] = [{a: aluno[a] for a in usadas} for aluno in alunos]
    return historico

