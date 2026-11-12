"""Previsao de notas e da chance de aprovação com regressao linear simples.
Regressao simples = uma unica variável de entrada nota prevista = a + b x nota base
Chance de aprovação media final prevista = nota atual + soma(peso x nota prevista) o  "erro padrao" diz quanto a nota real costuma fugir da prevista. 
Supondo erros normais, chance = P(média final >= média de aprovacao).
"""

import math
from dataclasses import dataclass
from statistics import StatisticsError, linear_regression, mean

from sistema.calculo import MEDIA_APROVACAO, NOTA_MAXIMA, calcular_nota_atual

MIN_ALUNOS = 10  #minimo de alunos de turmas passadas para confiar na reta
_TOLERANCIA = 1e-9  #evita que 5,99999 conte como menor que 6


class PrevisaoIndisponivelError(ValueError):
    """Nao eh possível prever"""


@dataclass
class RegressaoSimples:
    """Reta y = intercepto + coeficiente x x e a qualidade do ajuste."""

    intercepto: float
    coeficiente: float
    erro_padrao: float 
    r2: float #0 a 1: quanto da variacao das notas a reta explica

    @classmethod
    def treinar(cls, xs, ys):
        if len(xs) < 3:
            raise PrevisaoIndisponivelError("Sao necessárias ao menos 3 observacoes para a regressao.")
        try:
            coeficiente, intercepto = linear_regression(xs, ys)
        except StatisticsError:  
            raise PrevisaoIndisponivelError(
                "Todos os alunos do historico tiraram a mesma nota base: nao da para ajustar a reta."
            ) from None

        soma_erros = sum((y - (intercepto + coeficiente * x)) ** 2 for x, y in zip(xs, ys))
        soma_total = sum((y - mean(ys)) ** 2 for y in ys)
        return cls(
            intercepto=intercepto,
            coeficiente=coeficiente,
            erro_padrao=math.sqrt(soma_erros / (len(xs) - 2)),
            r2=max(0.0, 1 - soma_erros / soma_total) if soma_total else 0.0,
        )

    def prever(self, x):
        return self.intercepto + self.coeficiente * x


@dataclass
class Predicao:
    base: object                #avaliacao usada como entrada 
    notas_previstas: dict       
    modelos: dict               
    media_final_prevista: float
    desvio_media_final: float
    chance_aprovacao: float     
    n_treino: int = 0          

    @property
    def chance_abaixo_da_media(self):
        """Chance de terminar abaixo da media."""
        return 1 - self.chance_aprovacao


def prever(historico, notas, regras):
    """Preve as avaliacoes pendentes e a chance de aprovacao. historico: lista de {avaliacao: nota | None}, um dict por aluno de turmas
    passadas (saida de carregador.buscar_historico). notas / regras: formato de sistema.calculo, de uma disciplina.
    """
    pesos = regras["avaliacoes"]
    media = regras.get("media_aprovacao", MEDIA_APROVACAO)
    atual = calcular_nota_atual(notas, regras)
    conhecidas = [a for a in pesos if notas.get(a) is not None]
    pendentes = [a for a in pesos if a not in conhecidas]

    if not pendentes:  
        return Predicao(None, {}, {}, atual, 0.0, float(atual >= media - _TOLERANCIA))
    if not conhecidas:
        raise PrevisaoIndisponivelError(
            "informe ao menos uma nota ja obtida: a regressão simples precisa de uma nota de partida."
        )

    base = conhecidas[-1]  

    colunas = [base] + pendentes
    alunos = [l for l in historico if all(l.get(a) is not None for a in colunas)]
    if len(alunos) < MIN_ALUNOS:
        raise PrevisaoIndisponivelError(
            f"o histórico tem só {len(alunos)} aluno(s) com as notas {', '.join(colunas)} "
            f"(mínimo {MIN_ALUNOS})."
        )

    xs = [l[base] for l in alunos]
    modelos = {a: RegressaoSimples.treinar(xs, [l[a] for l in alunos]) for a in pendentes}
    previstas = {a: min(max(modelos[a].prever(notas[base]), 0.0), NOTA_MAXIMA) for a in pendentes}
    media_prevista = atual + sum(pesos[a] * previstas[a] for a in pendentes)

    
    desvio = sum(pesos[a] * modelos[a].erro_padrao for a in pendentes)
    if desvio == 0:
        chance = float(media_prevista >= media - _TOLERANCIA)
    else:  #P(media final >= média de aprovacao), pela curva normal
        chance = 0.5 * math.erfc((media - media_prevista) / desvio / math.sqrt(2))

    return Predicao(base, previstas, modelos, media_prevista, desvio, chance, len(alunos))

