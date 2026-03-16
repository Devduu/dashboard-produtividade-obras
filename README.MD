# 🏗️ Dashboard de Produtividade em Obras

Dashboard interativo desenvolvido em Python com Streamlit para análise de produtividade de mão de obra em obras da construção civil.

## 📋 Sobre o projeto

Atividade acadêmica da disciplina de Data Science e Statistical Computing — FIAP.

O dashboard analisa dados diários de apropriação de obras, com foco no índice de produtividade diário (ip_d) da mão de obra. A partir de uma planilha com milhares de registros de campo, o projeto transforma dados brutos em visualizações e análises estatísticas que permitem responder perguntas reais de gestão de obras.

## 🔍 O que o dashboard faz

- Lê e filtra automaticamente os dados de mão de obra da base `df_diarios.xlsx`
- Permite filtrar por obra, caderno e grupo de serviço
- Calcula e exibe estatísticas descritivas: média, mediana, moda, desvio-padrão, variância, amplitude e CV
- Exibe histograma, curva de densidade, boxplot e gráficos de barras
- Compara a produtividade entre as obras e grupos de serviço
- Responde às perguntas orientadoras do enunciado com gráficos e interpretações

## 🛠️ Tecnologias utilizadas

- Python 3.13
- Streamlit
- Pandas
- Plotly

## 🚀 Como rodar

1. Clone o repositório:
```
   git clone https://github.com/InovaLink-Challenge-Fiap/dashboard-produtividade-obras.git
   cd dashboard-produtividade-obras
```

2. Instale as dependências:
```
   pip3 install streamlit pandas openpyxl plotly
```

3. Execute o dashboard:
```
   streamlit run app.py
```

## 📁 Estrutura do projeto
```
dashboard-produtividade-obras/
├── app.py              # código principal do dashboard
├── df_diarios.xlsx     # base de dados de apropriações diárias
├── TAREFAS.md          # status do projeto e tarefas pendentes
└── README.md           # este arquivo
```

## 👥 Equipe

| Nome | RM |
|------|----|
| Eduardo Delorenzo Moraes | 561749 |
| Kauê de Almeida Pena | 564211 |
| Lucas Rowlands Abat | 562994 |
| Ronaldo Aparecido Monteiro Almeida | 565017 |
| William Queiroz | 565032 |
|  |  |
```
