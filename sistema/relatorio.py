"""Monta o relatório de situação e a previsao"""

from dataclasses import dataclass
from typing import Optional

from sistema.calculo import (
    RESULTADO_RECUPERACAO,
    RESULTADO_REPROVADO,
    calcular_faltas_permitidas,
    calcular_nota_atual,
    calcular_nota_necessaria,
    calcular_presenca,
    classificar_situacao,
    presenca_minima,
)
from sistema.carregador import buscar_historico, listar_materias_com_historico
from sistema.predicao import Predicao, PrevisaoIndisponivelError, prever


@dataclass
class RelatorioDisciplina:
    disciplina: str
    nota_atual: float
    situacao: str
    nota_necessaria: object            
    avaliacoes_pendentes: list
    aulas_totais: Optional[int] = None
    faltas: Optional[int] = None
    presenca: Optional[float] = None
    presenca_minima: Optional[float] = None
    faltas_permitidas: Optional[int] = None


def gerar_relatorio(materia):
    """Situação da matéria (histórias 1 a 4). `materia` é um carregador.Materia."""
    atual = calcular_nota_atual(materia.notas, materia.regras)
    freq = materia.frequencia
    presenca = calcular_presenca(**freq) if freq else None

    relatorio = RelatorioDisciplina(
        disciplina=materia.nome,
        nota_atual=atual,
        situacao=classificar_situacao(materia.notas, materia.regras, presenca),
        nota_necessaria=calcular_nota_necessaria(materia.notas, materia.regras),
        avaliacoes_pendentes=[a for a in materia.regras["avaliacoes"] if materia.notas.get(a) is None],
    )
    if freq:
        relatorio.aulas_totais = freq["aulas_totais"]
        relatorio.faltas = freq["faltas"]
        relatorio.presenca = presenca
        relatorio.presenca_minima = presenca_minima(atual)
        relatorio.faltas_permitidas = calcular_faltas_permitidas(
            freq["aulas_totais"], freq["faltas"], atual
        )
    return relatorio


def gerar_previsao(materia, nome_do_arquivo, pasta_historico):
    """Preve as notas pendentes da materia, se houver historico com o mesmo nome do arquivo."""
    historico = buscar_historico(pasta_historico, nome_do_arquivo)
    if historico is None:
        disponiveis = ", ".join(a.stem for a in listar_materias_com_historico(pasta_historico).values())
        raise PrevisaoIndisponivelError(
            f"não há dados de turmas passadas para '{nome_do_arquivo}'. "
            f"Matérias disponíveis: {disponiveis or 'nenhuma'}. "
            "Para prever, o arquivo de notas deve ter o mesmo nome de uma delas."
        )
    return prever(historico, materia.notas, materia.regras)

def formatar_numero(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def formatar_percentual(fracao):
    """Percentual pt-BR; previsões nunca são exibidas como 0% ou 100% exatos
    (só quando o resultado é certo, ou seja, exatamente 0 ou 1)."""
    if 0 < fracao < 0.001:
        return "< 0,1%"
    if 0.999 < fracao < 1:
        return "> 99,9%"
    return f"{formatar_numero(fracao * 100, 1)}%"


def _campo(rotulo, valor):
    """Linha 'Rótulo .......... valor' com a coluna de valores alinhada."""
    return f"{rotulo} ".ljust(26, ".") + f" {valor}"


def _descrever_nota_necessaria(rel):
    nec = rel.nota_necessaria
    if nec == RESULTADO_RECUPERACAO:
        return "acima de 10 nas pendentes -> só a recuperação pode salvar (Recuperação)"
    if nec == RESULTADO_REPROVADO:
        return "nem a recuperação é suficiente (Reprovado)"
    if nec == 0:
        return "0 (já alcançou a média de aprovação)"
    return f"{formatar_numero(nec)} em cada avaliação pendente ({', '.join(rel.avaliacoes_pendentes)})"


def formatar_predicao(predicao, recuo="  "):
    """Linhas de texto com a previsão (equação, notas previstas, média final e chances)."""
    linhas = []
    for avaliacao, nota in predicao.notas_previstas.items():
        m = predicao.modelos[avaliacao]
        linhas.append(
            f"{recuo}{avaliacao} prevista: {formatar_numero(nota)}  (erro típico ±{formatar_numero(m.erro_padrao)})"
        )
        linhas.append(
            f"{recuo}   reta: {avaliacao} = {formatar_numero(m.intercepto)} "
            f"{'+' if m.coeficiente >= 0 else '-'} {formatar_numero(abs(m.coeficiente))} x {predicao.base}"
            f"   [R² {formatar_numero(m.r2)}]"
        )
    if predicao.notas_previstas:
        linhas.append(
            f"{recuo}Média final prevista: {formatar_numero(predicao.media_final_prevista)}"
            f"  (±{formatar_numero(predicao.desvio_media_final)})"
        )
    linhas.append(f"{recuo}Chance de aprovação direta: {formatar_percentual(predicao.chance_aprovacao)}")
    linhas.append(
        f"{recuo}Chance de ficar abaixo da média (recuperação/reprovação): "
        f"{formatar_percentual(predicao.chance_abaixo_da_media)}"
    )
    return linhas


def formatar_relatorio(rel):
    """Texto do relatório de situação de uma matéria."""
    linhas = [
        f"=== {rel.disciplina} ===",
        _campo("Nota atual", formatar_numero(rel.nota_atual)),
        _campo("Situação", rel.situacao.upper()),
        _campo("Nota necessária", _descrever_nota_necessaria(rel)),
    ]
    if rel.faltas_permitidas is not None:
        linhas.append(_campo(
            "Frequência",
            f"{rel.faltas} falta(s) em {rel.aulas_totais} aulas "
            f"(presença {formatar_percentual(rel.presenca)}, "
            f"mínimo exigido {formatar_percentual(rel.presenca_minima)})",
        ))
        linhas.append(_campo("Faltas ainda permitidas", rel.faltas_permitidas))
    return "\n".join(linhas)


def formatar_previsao(materia, predicao):
    """Texto da previsão de uma matéria."""
    linhas = [
        f"=== Previsão: {materia.nome} ===",
        _campo("Nota atual", formatar_numero(calcular_nota_atual(materia.notas, materia.regras))),
    ]
    if not predicao.notas_previstas:
        linhas.append("Nada a prever: todas as avaliações já foram realizadas.")
    else:
        linhas.append(
            f"Previsão (regressão linear simples a partir da {predicao.base}; "
            f"{predicao.n_treino} alunos de turmas passadas):"
        )
        linhas.extend(formatar_predicao(predicao))
    return "\n".join(linhas)

