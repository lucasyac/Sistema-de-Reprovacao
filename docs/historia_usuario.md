# HISTÓRIAS DE USUÁRIO #

*História de usuário 1:*
Como aluno, quero saber qual é minha nota atual na disciplina, considerando os critérios de avaliação do professor, para saber minha situação.

*Critérios de aceitação 1:*
1. Dado um JSON válido, o sistema considera o critério de avaliação do professor para realizar os cálculos.
2. Dado um CSV válido, o sistema utiliza os critérios de avaliação do professor para retornar a nota atual da disciplina.
3. Avaliações pendentes não entram na soma.
4. A nota atual é a soma de (nota x peso) de cada avaliação já realizada.

*História de usuário 2:*
Como aluno, quero saber se estou aprovado, reprovado ou em risco em cada disciplina, para direcionar melhor meus estudos.

*Critérios de aceitação 2:*
1. O aluno é aprovado quando a nota atual é maior ou igual a necessária para aprovação.
2. O aluno é reprovado se não houver possibilidade de alcançar média 6 nem com atividade de recuperação.
3. O aluno está em risco quando sua nota está abaixo da média necessária para aprovação, mas ainda é possível alcançá-la.
4. O sistema leva em consideração as regras fixas em relação a nota/presença para calcular a situação atual.

*História de usuário 3:*
Como aluno, quero saber quantas faltas eu tenho na disciplina, para saber quantas vezes posso faltar ainda.

*Critérios de aceitação 3:*
1. O aluno deve informar quantas aulas totais serão dadas e quantas faltas ele tem.
2. O aluno deve informar a nota atual dele na disciplina, para que o sistema retorne com exatidão seu limite de faltas atual.
3. O cálculo leva em consideração as regras fixas do sistema em relação a nota/presença.
4. O sistema retorna a quantidade de faltas permitidas, considerando que o aluno seja aprovado com nota 6, o que diz respeito ao mínimo de presença que ele deve ter.

*História de usuário 4:*
Como aluno, quero saber que nota preciso alcançar nas próximas avaliações, para direcionar melhor meus estudos.

*Critérios de aceitação 4:*
1. A nota necessária nas próximas avaliações é (média necessária para aprovação - nota atual) / (peso das notas pendentes).
2. Se o aluno já está aprovado na disciplina (nota atual >= 6), a nota necessária nas próximas avaliações é 0.
3. Se a nota necessária nas próximas avaliações é maior que 10, o sistema calcula se é possível realizar recuperação. Caso seja possível realizar recuperação, retorna 'Recuperação', caso não, retorna 'Reprovado'.
4. Se a nota necessária for maior que 10 e a nota necessária na recuperação for maior que 10, o sistema retorna 'Reprovado'.

*Regras fixas do sistema:*
1. Para aprovação, é necessária média final >= 6 e presença mínima de 75%.
2. Caso (6.5 <= média final < 8), o aluno será aprovado com presença mínima exigida de 65%.
3. Caso a média final seja maior ou igual a 8, o aluno será aprovado com presença mínima exigida de 50%.
4. Caso o aluno não alcance nota 6 nas avaliações regulares, será permitido que seja realizado uma atividade de recuperação definida pelo professor.
5. Caso o aluno não alcance nota 6 após realizar a atividade de recuperação, ele será reprovado.

*Definições:*
1. Nota atual: nota que o aluno alcançou com as atividades já realizadas.
2. Média necessária para aprovação: 6.
3. Média final: nota que o aluno alcançou ao fim do semestre após realizar todas as atividades, incluindo exame.
