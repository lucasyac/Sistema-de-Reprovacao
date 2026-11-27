# Sistema de Reprovação
O sistema ajuda estudantes universitários a acompanhar sua situação nas disciplinas ao longo do semestre, seguindo as regras de avaliação definidas por cada professor. O aluno fornece ao sistema um CSV com suas notas e faltas e um JSON com as regras de cada disciplina, conforme o plano de ensino. O sistema valida os dados, calcula as médias e a frequência, e retorna um relatório com o desempenho do aluno, com nota mínima necessária nas próximas avaliações e o número de faltas ainda permitidas, além de prever a chance de reprovação do aluno.

# Equipe
- Eduardo Moscatelli Martinho
- Lucas Youssif Abdallah Catore
- Ryan Henrique Escandelari Marcato

# Entrada e Saída
Entrada
- "arquivo.csv": notas e faltas do aluno por disciplina
- "regras.json": regras de cada disciplina

Saída
- Relatório por disciplina com a situação do aluno, a nota mínima necessária nas avaliações restantes, as faltas ainda permitidas e a chance de reprovação

# Como executar
Precisa de Python 3.10 ou mais novo. O sistema usa só a biblioteca padrão.

```
python -m sistema
```

No menu, a opção 1 mostra a situação e a opção 2 faz a previsão. Para testar, use os arquivos `exemplos/calculo1.csv` e `exemplos/calculo1.json`.

# Testes
```
pip install pytest
python -m pytest
```

# Estrutura
```
dados/historico/    notas de turmas passadas (usadas na previsão)
docs/               histórias de usuário, diagramas e padrões de projeto
entrega/            PDF e zip da entrega final
exemplos/           modelos de CSV e JSON
sistema/
├── calculo.py      regras de negócio
├── carregador.py   valida os dados e monta a matéria
├── cli.py          menu do terminal
├── comandos.py     opções do menu (Command)
├── fachada.py      ponto de acesso ao sistema (Facade)
├── leitores.py     leitura dos arquivos (Template Method)
├── predicao.py     modelo de regressão linear
└── relatorio.py    geração do relatório
test/               testes
```

# Documentação
- [Histórias de usuário](docs/historia_usuario.md)
- [Testes e critérios de aceitação](docs/testes_e_criterios.md)
- [Padrões de projeto](docs/padroes_de_projeto.md)
- [Diagrama da arquitetura](docs/arquitetura.png)

# Referência
SILVA, Andréa Ferreira da; ALMEIDA, Aléssio Tony Cavalcanti de; RAMALHO, Hilton Martins de Brito. Predição do Risco de Reprovação no Ensino Superior Usando Algoritmos de Machine Learning. Teoria e Prática em Administração, v. 10, n. 2, p. 58-80, jul.-dez. 2020. DOI: 10.21714/2238-104X2020v10i2-51124.
Disponível em: http://dx.doi.org/10.21714/2238-104X2020v10i2-51124

## Resumo da pesquisa
O artigo trata da previsão de reprovação no ensino superior. Os autores ligam a reprovação à retenção e à evasão e citam o Censo da Educação Superior de 2017, em que a taxa de conclusão fica em torno de 37% nas instituições públicas e de 36% nas privadas. Prever cedo quem corre risco permite agir antes do fim do semestre.

Foram usados registros da Universidade Federal da Paraíba (UFPB) e dados da Plataforma Lattes sobre os professores, de 2010 a 2016, na disciplina de Cálculo Diferencial e Integral I. São 6.342 matrículas, das quais 3.109 (49%) terminaram em reprovação. Os dados foram divididos em 70% para treino e 30% para teste, e foram comparados onze métodos de aprendizado de máquina, com informações do aluno, do professor, da turma e do curso.

Os modelos escolhidos foram Ridge, Regressão Logística, LASSO e Elastic Net, sem diferença estatística entre eles. No conjunto de teste, acertaram a situação de cerca de 67% dos alunos e identificaram 65% dos que reprovaram. As notas do vestibular, inclusive a de matemática, estão entre as informações mais importantes.

A pesquisa sustenta a relevância do nosso sistema porque mostra que a reprovação é frequente (quase metade das matrículas em Cálculo I no período) e que dados que já existem ajudam a estimar o risco com antecedência. O artigo olha o problema pelo lado da instituição. Nosso sistema leva a ideia para o aluno de um jeito bem mais simples, com regressão linear sobre notas de turmas passadas, além de calcular a nota necessária e as faltas permitidas.
