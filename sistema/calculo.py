"""Regras de negocio do sistema historias de usuário 1 a 4."""

MEDIA_APROVACAO = 6.0
NOTA_MAXIMA = 10.0

SITUACAO_APROVADO = "aprovado"
SITUACAO_REPROVADO = "reprovado"
SITUACAO_EM_RISCO = "em risco"

RESULTADO_RECUPERACAO = "Recuperação"
RESULTADO_REPROVADO = "Reprovado"

#Regras de presenca: (nota minima, presenca minima em %), da maior nota para a menor
FAIXAS_PRESENCA = [(8.0, 50), (6.5, 65)]
PRESENCA_PADRAO = 75

#Tolerancia para comparar numeros de ponto flutuante
_EPS = 1e-9


def _atingiu(valor, minimo):
    return valor >= minimo - _EPS


#HISTORIA 1: nota atual
def calcular_nota_atual(notas, regras):
    """H1: soma de (nota x peso) das avaliações ja realizadas. Avaliacoes pendentes nao entram na soma."""
    total = 0.0
    for avaliacao, peso in regras["avaliacoes"].items():
        nota = notas.get(avaliacao)
        if nota is not None:
            total += nota * peso
    return total


def calcular_peso_pendente(notas, regras):
    """Soma dos pesos das avaliacoes que ainda nao foram realizadas."""
    return sum(
        peso
        for avaliacao, peso in regras["avaliacoes"].items()
        if notas.get(avaliacao) is None
    )



#HISTORIA 4: nota necessAria e recuperacao
def calcular_nota_recuperacao(media_final, media_aprovacao=MEDIA_APROVACAO):
    """Nota necessária na recuperação para chegar à média de aprovação, (média + recuperação) / 2"""
    return 2 * media_aprovacao - media_final


def calcular_nota_necessaria(notas, regras):
    """nota que o aluno precisa tirar nas avaliações pendentes."""
    media = regras.get("media_aprovacao", MEDIA_APROVACAO)
    atual = calcular_nota_atual(notas, regras)

    if _atingiu(atual, media):
        return 0.0

    pendente = calcular_peso_pendente(notas, regras)
    if pendente > _EPS:
        necessaria = (media - atual) / pendente
        if necessaria <= NOTA_MAXIMA + _EPS:
            return necessaria

    #Nao da para passar so nas avaliacoes regulares: a recuperacao e possivel
    melhor_media = atual + NOTA_MAXIMA * pendente
    if calcular_nota_recuperacao(melhor_media, media) <= NOTA_MAXIMA + _EPS:
        return RESULTADO_RECUPERACAO
    return RESULTADO_REPROVADO


#Presenca e faltas regras fixas + historia 3
def presenca_minima_percentual(nota):
    for nota_minima, percentual in FAIXAS_PRESENCA:
        if _atingiu(nota, nota_minima):
            return percentual
    return PRESENCA_PADRAO


def presenca_minima(nota):
    return presenca_minima_percentual(nota) / 100


def _validar_aulas_e_faltas(aulas_totais, faltas):
    if aulas_totais <= 0:
        raise ValueError("O total de aulas deve ser maior que zero.")
    if faltas < 0:
        raise ValueError("O número de faltas nao pode ser negativo.")
    if faltas > aulas_totais:
        raise ValueError("O numero de faltas nao pode ser maior que o total de aulas.")


def calcular_presenca(aulas_totais, faltas):
    """Fracao de presença do aluno (0 a 1) com base nas faltas ate agora."""
    _validar_aulas_e_faltas(aulas_totais, faltas)
    return (aulas_totais - faltas) / aulas_totais


def calcular_faltas_permitidas(aulas_totais, faltas, nota_atual):
    """H3: quantas faltas o aluno ainda pode ter sem perder por frequencia."""
    _validar_aulas_e_faltas(aulas_totais, faltas)
    percentual_maximo_de_faltas = 100 - presenca_minima_percentual(nota_atual)
    limite = int(aulas_totais) * percentual_maximo_de_faltas // 100
    return max(0, limite - int(faltas))


#HISTORIA 2: situacao
def _frequencia_suficiente(presenca, nota):
    return _atingiu(presenca, presenca_minima(nota))


def _classificar_com_presenca(atual, pendente, media, presenca):
    if not 0 <= presenca <= 1:
        raise ValueError("A presença deve ser uma fração entre 0 e 1.")

    if _atingiu(atual, media):
        if _frequencia_suficiente(presenca, atual):
            return SITUACAO_APROVADO
        if pendente <= _EPS:
            return SITUACAO_REPROVADO  #tudo realizado e frequencia insuficiente

    #Ainda ha chance de a nota subir e baixar a exigencia de presenca.
    if _frequencia_suficiente(presenca, atual + NOTA_MAXIMA * pendente):
        return SITUACAO_EM_RISCO
    return SITUACAO_REPROVADO


def classificar_situacao(notas, regras, presenca=None):
    """H2: "aprovado", "reprovado" ou "em risco"."""
    if calcular_nota_necessaria(notas, regras) == RESULTADO_REPROVADO:
        return SITUACAO_REPROVADO

    media = regras.get("media_aprovacao", MEDIA_APROVACAO)
    atual = calcular_nota_atual(notas, regras)
    if presenca is None:
        return SITUACAO_APROVADO if _atingiu(atual, media) else SITUACAO_EM_RISCO

    pendente = calcular_peso_pendente(notas, regras)
    return _classificar_com_presenca(atual, pendente, media, presenca)
