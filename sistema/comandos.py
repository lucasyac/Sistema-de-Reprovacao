"""Opcoes do menu, usando o padrao Command."""

from pathlib import Path

from sistema.fachada import DadosInvalidosError, PrevisaoIndisponivelError


class Terminal:
    """O que os comandos usam: o sistema, como ler e escrever e os ultimos arquivos."""

    def __init__(self, sistema, entrada, saida):
        self.sistema = sistema
        self.entrada = entrada
        self.saida = saida
        self.ultimos = {}  # para nao digitar os caminhos de novo

    def pedir_caminho(self, pergunta, ultimo):
        """Pede o caminho de um arquivo. Enter reaproveita o ultimo; '0' volta ao menu."""
        dica = f"Enter = usar o último ({Path(ultimo).name}), 0 = voltar" if ultimo else "0 = voltar"
        texto = self.entrada(f"{pergunta} [{dica}]: ").strip().strip("\"'")
        if texto == "0":
            return None
        return texto or ultimo

    def pedir_materia(self):
        """Devolve (Materia, caminho do CSV), ou None se o aluno voltou ou houve erro."""
        self.saida("\nUma matéria por vez. Modelos de arquivo: pasta exemplos/ (calculo1.csv e calculo1.json).")
        csv = self.pedir_caminho("Arquivo CSV com suas notas", self.ultimos.get("csv"))
        if not csv:
            return None
        regras = self.pedir_caminho("Arquivo JSON com as regras da matéria (pesos)", self.ultimos.get("json"))
        if not regras:
            return None
        try:
            materia = self.sistema.carregar_materia(csv, regras)
        except DadosInvalidosError as erro:
            self.saida(f"Erro: {erro}")
            return None
        self.ultimos["csv"], self.ultimos["json"] = csv, regras
        return materia, csv


class Comando:
    """Uma opcao do menu."""

    tecla = ""
    descricao = ""

    def executar(self, terminal):
        """Faz a opcao. Devolve False quando o menu deve fechar."""
        raise NotImplementedError


class ComandoSituacao(Comando):
    tecla = "1"
    descricao = "Ver minha situação em uma matéria"

    def executar(self, terminal):
        carregada = terminal.pedir_materia()
        if carregada:
            materia, _ = carregada
            terminal.saida("\n" + terminal.sistema.relatorio_situacao(materia))
        return True


class ComandoPrevisao(Comando):
    tecla = "2"
    descricao = "Prever minhas notas e a chance de aprovação"

    def executar(self, terminal):
        self.mostrar_disponiveis(terminal)
        carregada = terminal.pedir_materia()
        if carregada:
            materia, csv = carregada
            self.mostrar_previsao(terminal, materia, csv)
        return True

    def mostrar_disponiveis(self, terminal):
        disponiveis = terminal.sistema.materias_com_previsao()
        terminal.saida("\nMatérias com previsão disponível (turmas passadas):")
        for nome in disponiveis:
            terminal.saida(f"  - {nome}")
        if not disponiveis:
            terminal.saida("  (nenhuma: não há arquivos na pasta de histórico)")
        terminal.saida("O seu arquivo CSV de notas deve ter o MESMO NOME da matéria (ex.: calculo1.csv).")

    def mostrar_previsao(self, terminal, materia, csv):
        try:
            texto = terminal.sistema.relatorio_previsao(materia, csv)
        except (PrevisaoIndisponivelError, DadosInvalidosError) as erro:
            terminal.saida(f"Previsão indisponível: {erro}")
            return
        terminal.saida("\n" + texto)


class ComandoSair(Comando):
    tecla = "0"
    descricao = "Sair"

    def executar(self, terminal):
        terminal.saida("Até logo!")
        return False
