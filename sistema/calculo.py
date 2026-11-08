#Regras de negocio do sistema (historias de usuario 1 a 4).


MEDIA_APROVACAO = 6.0
NOTA_MAXIMA = 10.0

SITUACAO_APROVADO = "aprovado"
SITUACAO_REPROVADO = "reprovado"
SITUACAO_EM_RISCO = "em risco"

RESULTADO_RECUPERACAO = "Recuperação"
RESULTADO_REPROVADO = "Reprovado"

#tolerancia para comparar numeros de ponto flutuante (ex.: 0.1 + 0.2).
_EPS = 1e-9



#HISTORIA 1: nota atual
def calcular_nota_atual(notas, regras):
    """H1: soma de (nota x peso) das avaliações ja realizadas avaliacoes pendentes nao entram na soma."""
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

#HISTORIA 4: nota necessária e recuperação
def calcular_nota_recuperacao(media_final, media_aprovacao=MEDIA_APROVACAO):
    """Nota necessaria na recuperacao para chegar a aprovacao a media final com recuperacao e (média + recuperação) / 2, logo recuperação = 2 x media_aprovação - media."""
    return 2 * media_aprovacao - media_final

def calcular_nota_necessaria(notas, regras):
    """nota que o aluno precisa tirar nas avaliações pendentes."""
    media = regras.get("media_aprovacao", MEDIA_APROVACAO)
    atual = calcular_nota_atual(notas, regras)

    if atual >= media - _EPS:
        return 0.0

    pendente = calcular_peso_pendente(notas, regras)
    if pendente > _EPS:
        necessaria = (media - atual) / pendente
        if necessaria <= NOTA_MAXIMA + _EPS:
            return necessaria

    #Nao da para passar so nas avaliações regulares: a recuperação eh possivel
    #se, no melhor cenario (10 em tudo que falta), ela exigir no máximo 10.
    melhor_media = atual + NOTA_MAXIMA * pendente
    if calcular_nota_recuperacao(melhor_media, media) <= NOTA_MAXIMA + _EPS:
        return RESULTADO_RECUPERACAO
    return RESULTADO_REPROVADO

#PRESENCA E FALTAS(regras fixas + história 3)
def presenca_minima_percentual(nota):
    """Regras fixas: nota < 6.5 -> 75%; 6.5 <= nota < 8 -> 65%; nota >= 8 -> 50%."""
    if nota >= 8.0 - _EPS:
        return 50
    if nota >= 6.5 - _EPS:
        return 65
    return 75

def presenca_minima(nota):
    return presenca_minima_percentual(nota) / 100

def _validar_aulas_e_faltas(aulas_totais, faltas):
    if aulas_totais <= 0:
        raise ValueError("O total de aulas deve ser maior que zero.")
    if faltas < 0:
        raise ValueError("O número de faltas não pode ser negativo.")
    if faltas > aulas_totais:
        raise ValueError("O número de faltas não pode ser maior que o total de aulas.")

def calcular_presenca(aulas_totais, faltas):
    """Fracao de presenca do aluno (0 a 1) com base nas faltas ate agora."""
    _validar_aulas_e_faltas(aulas_totais, faltas)
    return (aulas_totais - faltas) / aulas_totais

def calcular_faltas_permitidas(aulas_totais, faltas, nota_atual):
    """H3: quantas faltas o aluno ainda pode ter sem perder por frequencia."""
    _validar_aulas_e_faltas(aulas_totais, faltas)
    percentual_maximo_de_faltas = 100 - presenca_minima_percentual(nota_atual)
    limite = int(aulas_totais) * percentual_maximo_de_faltas // 100
    return max(0, limite - int(faltas))

# HISTORIA 2: situacao
def classificar_situacao(notas, regras, presenca=None):
    """H2: "aprovado", "reprovado" ou "em risco"."""
    media = regras.get("media_aprovacao", MEDIA_APROVACAO)
    atual = calcular_nota_atual(notas, regras)
    pendente = calcular_peso_pendente(notas, regras)
    nota_maxima_possivel = atual + NOTA_MAXIMA * pendente

    if calcular_nota_necessaria(notas, regras) == RESULTADO_REPROVADO:
        return SITUACAO_REPROVADO

    aprovado_por_nota = atual >= media - _EPS
    if presenca is None:
        return SITUACAO_APROVADO if aprovado_por_nota else SITUACAO_EM_RISCO

    if not 0 <= presenca <= 1:
        raise ValueError("A presença deve ser uma fração entre 0 e 1.")

    if aprovado_por_nota and presenca >= presenca_minima(atual) - _EPS:
        return SITUACAO_APROVADO
    if aprovado_por_nota and pendente <= _EPS:
        return SITUACAO_REPROVADO  # tudo realizado e frequencia insuficiente

    # Ainda a chance de a nota subir e baixar a exigencia de presença.
    if presenca >= presenca_minima(nota_maxima_possivel) - _EPS:
        return SITUACAO_EM_RISCO
    return SITUACAO_REPROVADO

