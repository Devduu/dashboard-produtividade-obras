# 🏗️ Dashboard de Produtividade em Obras

Dashboard interativo desenvolvido em Python com Streamlit para análise de produtividade de mão de obra em obras da construção civil.

**Aplicação publicada:** https://dashboard-mao-de-obra.streamlit.app/

![Python](https://img.shields.io/badge/Python-3.13-3987e5?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.66.1-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-3.1.1-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-7.1.0-3F4F75?logo=plotly&logoColor=white)

## 📋 Sobre o projeto

Atividade acadêmica da disciplina de Data Science e Statistical Computing, na FIAP.

O dashboard analisa dados diários de apropriação de obras, com foco no índice de produtividade diário (ip_d) da mão de obra, que mede as horas trabalhadas por unidade de serviço: quanto menor, mais produtivo. A partir de uma planilha com milhares de registros de campo, o projeto transforma dados brutos em visualizações e análises estatísticas que permitem responder perguntas reais de gestão de obras.

## 🔍 O que o dashboard faz

- Lê e filtra automaticamente os dados de mão de obra da base `df_diarios.xlsx`
- Permite filtrar por obra, caderno e grupo de serviço
- Calcula e exibe estatísticas descritivas: média, mediana, moda, desvio-padrão, variância, amplitude e CV
- Exibe histograma, curva de densidade, boxplot e gráficos de barras
- Compara a produtividade entre as obras e grupos de serviço
- Responde às perguntas orientadoras do enunciado com gráficos e interpretações

## 🚀 Como rodar

1. Clone o repositório:
```
   git clone https://github.com/Devduu/dashboard-produtividade-obras.git
   cd dashboard-produtividade-obras
```

2. Instale as dependências:
```
   pip install -r requirements.txt
```

3. Execute o dashboard:
```
   streamlit run app.py
```
