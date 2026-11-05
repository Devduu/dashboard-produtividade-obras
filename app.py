import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Configuração da página
# Define o título da aba do navegador, o ícone e o layout largo

st.set_page_config(
    page_title="Dashboard de Produtividade", page_icon="🏗️", layout="wide"
)


# Leitura dos dados
# @st.cache_data faz o arquivo ser lido só uma vez e guardado na memória
# Isso evita que o Excel seja relido toda vez que o usuário mexe em um filtro
# Mantém só os registros de mão de obra e tira as linhas sem ip_d ou sem obra
# Guarda o total de mão de obra antes do corte para mostrar no aviso do topo

PLANILHA = Path(__file__).parent / "df_diarios.xlsx"

@st.cache_data
def carregar_dados():
    df = pd.read_excel(PLANILHA)
    df = df[df["tipo_insumo"] == "MAO DE OBRA"].copy()
    total_mao_de_obra = len(df)
    df = df.dropna(subset=["ip_d", "nome_obra"])
    return df, total_mao_de_obra


df, total_mao_de_obra = carregar_dados()

# Sidebar com filtros
# A sidebar é o painel lateral esquerdo do dashboard
# Cada selectbox cria um filtro com as opções únicas da coluna

st.sidebar.title("🔧 Filtros")

obras = ["Todas"] + sorted(df["nome_obra"].dropna().unique().tolist())
obra_selecionada = st.sidebar.selectbox("Obra", obras)

cadernos = ["Todos"] + sorted(df["caderno"].dropna().unique().tolist())
caderno_selecionado = st.sidebar.selectbox("Caderno", cadernos)

grupos = ["Todos"] + sorted(df["grupo"].dropna().unique().tolist())
grupo_selecionado = st.sidebar.selectbox("Grupo", grupos)

# Aplicar filtros
# Começa com todos os dados e vai filtrando conforme o usuário seleciona

df_filtrado = df
if obra_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["nome_obra"] == obra_selecionada]
if caderno_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["caderno"] == caderno_selecionado]
if grupo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["grupo"] == grupo_selecionado]

# Proteção: se a combinação de filtros não retornar dados, para o dashboard
# e mostra uma mensagem amigável em vez de travar com erro

if df_filtrado.empty:
    st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados. Tente outra combinação.")
    st.stop()

# Calcula média, mediana, desvio e CV do ip_d de cada obra

def resumir_por_obra(dados):
    return (
        dados.groupby("nome_obra")["ip_d"]
        .agg(
            Media="mean",
            Mediana="median",
            Desvio="std",
            CV=lambda x: x.std() / x.mean() * 100 if x.mean() != 0 else 0,
        )
        .reset_index()
        .round(3)
    )


# Mostra o resumo por obra em uma tabela, com os nomes das colunas legíveis
# Obra com um registro só não tem desvio nem CV, por isso aparece N/A

def mostrar_resumo(resumo):
    tabela = resumo.rename(columns={"nome_obra": "Obra", "Media": "Média"})
    st.dataframe(tabela, width="stretch", placeholder="N/A")


# Corta nomes com mais de 25 caracteres para caberem no eixo do gráfico

def nome_curto(nome):
    return nome[:25] + "..." if len(nome) > 25 else nome


# Título
st.title("🏗️ Dashboard de Produtividade Mão de Obra")
# Aviso explicando por que os dados foram filtrados (requisito do enunciado)
total_formatado = f"{total_mao_de_obra:,}".replace(",", ".")  # 4327 vira 4.327
st.warning(
    "⚠️ Dados filtrados para mão de obra, garantindo comparação coerente de produtividade entre os grupos. "
    f"Só entram os registros com nome de obra ({len(df)} de {total_formatado})."
)

# Abas
# Cria as 5 abas do dashboard
# Cada "aba" é uma variável que usamos no "with aba1:", "with aba2:", etc

aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["📋 Dados", "📐 Estatísticas", "📊 Gráficos", "🔍 Comparações", "❓ Perguntas"]
)

# Aba 1: Dados
# Mostra a tabela com todos os registros filtrados

with aba1:
    st.subheader("Base de dados (Mão de Obra)")
    st.write(f"Total de registros: **{len(df_filtrado)}**")
    st.dataframe(df_filtrado, width="stretch")

# Aba 2: Estatísticas
# Calcula e exibe as medidas de posição central e dispersão do ip_d
# ip_d é o índice de produtividade diário (principal variável da análise)
# ip_d = qntd / qs, ou seja, horas de mão de obra por unidade de serviço
# Quanto menor o ip_d, menos horas por unidade e maior a produtividade

with aba2:
    st.subheader("Estatísticas descritivas do ip_d")

    # Medidas de posição central
    col1, col2, col3 = st.columns(3)
    col1.metric("Média", f"{df_filtrado['ip_d'].mean():.3f}")
    col2.metric("Mediana", f"{df_filtrado['ip_d'].median():.3f}")
    # Proteção: se nenhum valor se repete, mode() devolve todos e não existe moda
    moda = df_filtrado["ip_d"].mode()
    tem_moda = df_filtrado["ip_d"].duplicated().any()
    col3.metric("Moda", f"{moda[0]:.3f}" if tem_moda else "N/A")

    # Medidas de dispersão
    # Proteção: um único registro não tem desvio-padrão nem variância
    desvio = df_filtrado["ip_d"].std()
    variancia = df_filtrado["ip_d"].var()
    col4, col5, col6 = st.columns(3)
    col4.metric("Desvio-padrão", f"{desvio:.3f}" if pd.notna(desvio) else "N/A")
    col5.metric("Variância", f"{variancia:.3f}" if pd.notna(variancia) else "N/A")
    amplitude = df_filtrado["ip_d"].max() - df_filtrado["ip_d"].min()
    col6.metric("Amplitude", f"{amplitude:.3f}")

    # Proteção: evita divisão por zero se a média for 0
    cv = (desvio / df_filtrado["ip_d"].mean()) * 100 if df_filtrado["ip_d"].mean() != 0 else 0
    st.metric("Coeficiente de Variação (CV)", f"{cv:.1f}%" if pd.notna(cv) else "N/A")
    st.info(
        "O CV indica a variabilidade relativa. CV abaixo de 15% = baixa variabilidade. Entre 15% e 30% = média. Acima de 30% = alta."
    )

# Aba 3: Gráficos
# Contém 4 gráficos: histograma, densidade, boxplot e barras por grupo

with aba3:
    st.subheader("Distribuição do ip_d")

    # Histograma: mostra quantas vezes cada valor de ip_d aparece
    fig_hist = px.histogram(
        df_filtrado,
        x="ip_d",
        nbins=50,
        title="Histograma do índice de produtividade diário (ip_d)",
        labels={"ip_d": "ip_d"},
        color_discrete_sequence=["#378ADD"],
    )
    fig_hist.update_traces(
        marker_line_color="black",
        marker_line_width=1,
        hovertemplate="ip_d=%{x}<br>Frequência=%{y}<extra></extra>",
    )
    fig_hist.update_layout(height=500, bargap=0.05, yaxis_title="Frequência")
    st.plotly_chart(fig_hist, width="stretch", key="hist")

    # Curva de densidade: mesma informação do histograma mas em densidade de probabilidade
    # histnorm="probability density" faz a área total das barras somar 1
    fig_dens = px.histogram(
        df_filtrado,
        x="ip_d",
        histnorm="probability density",
        nbins=50,
        title="Curva de densidade do ip_d",
        labels={"ip_d": "ip_d"},
        color_discrete_sequence=["#1D9E75"],
    )
    fig_dens.update_traces(
        opacity=0.7,
        marker_line_color="black",
        marker_line_width=1,
        hovertemplate="ip_d=%{x}<br>Densidade=%{y}<extra></extra>",
    )
    fig_dens.update_layout(height=500, bargap=0.05, yaxis_title="Densidade")
    st.plotly_chart(fig_dens, width="stretch", key="dens")

    # Boxplot: compara a distribuição do ip_d entre as obras
    # A caixa = 50% dos dados / linha no meio = mediana / pontos = outliers
    fig_box = px.box(
        df_filtrado,
        x="nome_obra",
        y="ip_d",
        title="Boxplot do ip_d por Obra",
        labels={"nome_obra": "Obra", "ip_d": "ip_d"},
        color="nome_obra",
    )
    fig_box.update_layout(height=500)
    st.plotly_chart(fig_box, width="stretch", key="box")

    # Gráfico de barras: média do ip_d por grupo de serviço, do maior para o menor
    # Nomes com mais de 25 caracteres são truncados com "..." para caber no gráfico
    df_grupo = (
        df_filtrado.groupby("grupo")["ip_d"]
        .mean()
        .reset_index()
        .sort_values("ip_d", ascending=False)
    )
    fig_bar_grupo = px.bar(
        df_grupo,
        x="grupo",
        y="ip_d",
        title="Média do ip_d por Grupo de Serviço",
        labels={"grupo": "Grupo", "ip_d": "Média do ip_d"},
        color_discrete_sequence=["#BA7517"],
    )
    fig_bar_grupo.update_traces(marker_line_color="black", marker_line_width=1)
    fig_bar_grupo.update_layout(
        height=500,
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=11),
            tickmode="array",
            tickvals=df_grupo["grupo"].tolist(),
            ticktext=[nome_curto(t) for t in df_grupo["grupo"]],
        )
    )
    st.plotly_chart(fig_bar_grupo, width="stretch", key="bar_grupo")

# Aba 4: Comparações
# Tabela e gráfico comparando média, mediana, desvio e CV entre as obras

with aba4:
    st.subheader("Comparação de produtividade por obra")

    # Agrupa os dados por obra e calcula as 4 métricas para cada uma
    resumo = resumir_por_obra(df_filtrado)

    mostrar_resumo(resumo)

    # Gráfico de barras com a média de cada obra
    fig_bar = px.bar(
        resumo,
        x="nome_obra",
        y="Media",
        title="Média do ip_d por Obra",
        labels={"nome_obra": "Obra", "Media": "Média do ip_d"},
        color="nome_obra",
    )
    fig_bar.update_traces(marker_line_color="black", marker_line_width=1)
    fig_bar.update_layout(height=500)
    st.plotly_chart(fig_bar, width="stretch", key="bar_obras")

# Aba 5: Perguntas orientadoras
# Responde as perguntas A, B, C e D do enunciado com gráfico + texto
# ATENÇÃO: esta aba usa "df" (dados completos) e não "df_filtrado"
# Isso é intencional: as respostas mostram sempre todas as obras
# para garantir que a comparação seja completa independente dos filtros

with aba5:
    st.subheader("Perguntas orientadoras")

    # Calcula resumo com todas as obras para usar nas respostas
    resumo_obras = resumir_por_obra(df)

    # Identifica as obras com maior e menor média de ip_d e com menor e maior CV
    obra_maior = resumo_obras.loc[resumo_obras["Media"].idxmax(), "nome_obra"]
    obra_menor = resumo_obras.loc[resumo_obras["Media"].idxmin(), "nome_obra"]
    obra_mais_estavel = resumo_obras.loc[resumo_obras["CV"].idxmin(), "nome_obra"]
    obra_menos_estavel = resumo_obras.loc[resumo_obras["CV"].idxmax(), "nome_obra"]

    # Pergunta A: diferença entre obras
    with st.expander("A) Há diferença de produtividade entre as obras?", expanded=True):
        fig_box_obras = px.box(
            df,
            x="nome_obra",
            y="ip_d",
            color="nome_obra",
            title="Boxplot do ip_d por Obra",
            labels={"nome_obra": "Obra", "ip_d": "ip_d"},
        )
        fig_box_obras.update_layout(height=500)
        st.plotly_chart(fig_box_obras, width="stretch", key="box_obras")
        st.write(
            f"""
        Sim, há diferenças visíveis de produtividade entre as obras.
        A obra que mais consome horas por unidade de serviço, com a maior média de ip_d, é a **{obra_maior}**.
        A que menos consome, com a menor média, é a **{obra_menor}**.
        Essas diferenças podem estar relacionadas ao tipo de serviço executado, ao perfil da equipe
        ou às condições de campo de cada obra.
        """
        )

    # Pergunta B: diferença entre grupos de serviço
    with st.expander("B) Há diferença de produtividade entre grupos de serviço?"):
        resumo_grupos = (
            df.groupby("grupo")["ip_d"]
            .agg(Media="mean", Mediana="median")
            .reset_index()
            .sort_values("Media", ascending=False)
            .round(3)
        )

        fig_bar_b = px.bar(
            resumo_grupos.head(10),
            x="grupo",
            y="Media",
            title="Top 10 grupos com maior média de ip_d",
            labels={"grupo": "Grupo", "Media": "Média ip_d"},
            color_discrete_sequence=["#7F77DD"],
        )
        fig_bar_b.update_traces(marker_line_color="black", marker_line_width=1)
        fig_bar_b.update_layout(
            height=500,
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=11),
                tickmode="array",
                tickvals=resumo_grupos.head(10)["grupo"].tolist(),
                ticktext=[nome_curto(t) for t in resumo_grupos.head(10)["grupo"]],
            )
        )
        st.plotly_chart(fig_bar_b, width="stretch", key="bar_b")
        st.write(
            """
        Sim, o ip_d varia bastante entre os grupos de serviço.
        Como ele mede as horas de mão de obra por unidade de serviço, quanto maior o valor,
        mais horas cada unidade consome. Os grupos do gráfico são os que mais consomem horas por unidade.
        Cada serviço tem a sua própria unidade, como m², m³ ou metro linear, então essa comparação
        também reflete o tipo de serviço, e não só a produtividade da equipe.
        """
        )

    # Pergunta C: relação entre média e mediana
    with st.expander("C) Como está a relação entre média e mediana nos grupos?"):
        mostrar_resumo(resumo_obras)
        st.write(
            """
        Em todas as obras, a **média é maior que a mediana**, o que indica
        que os valores mais altos puxam a média para cima.
        A maioria dos registros diários fica abaixo da média, e os dias com consumo muito alto
        de horas por unidade, ou seja, de baixa produtividade, distorcem esse valor.
        Nesses casos, a **mediana é uma medida mais representativa** da produtividade típica.
        """
        )

    # Pergunta D: previsibilidade por obra (usa o CV: quanto menor, mais previsível)
    with st.expander(
        "D) Quais grupos apresentam produtividade mais e menos previsível?"
    ):
        # Gráfico colorido: verde = mais previsível / vermelho = menos previsível
        fig_cv = px.bar(
            resumo_obras.sort_values("CV"),
            x="nome_obra",
            y="CV",
            title="Coeficiente de Variação (CV) por Obra (quanto menor, mais previsível)",
            labels={"nome_obra": "Obra", "CV": "CV (%)"},
            color="CV",
            color_continuous_scale="RdYlGn_r",
        )
        fig_cv.update_traces(marker_line_color="black", marker_line_width=1)
        fig_cv.update_layout(height=500)
        st.plotly_chart(fig_cv, width="stretch", key="cv")
        st.write(
            f"""
        A obra **{obra_mais_estavel}** apresenta o menor CV, indicando comportamento mais estável
        e previsível, útil para planejamento e orçamento com maior confiança.
        Já a obra **{obra_menos_estavel}** apresenta o maior CV, o que significa alta variabilidade
        no desempenho diário, exigindo maior atenção do gestor e margens de segurança no planejamento.
        """
        )

    # Questão extra: vídeo sobre produtividade
    with st.expander("E) Análise do vídeo sobre produtividade em obras"):
        st.write(
                """
    Pelo que foi apresentado no vídeo, o acompanhamento da produtividade em obras é realizado
    a partir de um índice calculado pela relação entre insumo e produto, como por exemplo
    horas de trabalho em relação à área executada em metros quadrados. A partir das
    apropriações diárias, são obtidos valores de produtividade ao longo do tempo,
    permitindo analisar tanto os resultados diários quanto indicadores agregados,
    como a média e o resultado acumulado. A proposta é identificar o comportamento
    estatístico da produtividade de determinado serviço e, com base nessa distribuição,
    estimar um coeficiente representativo.

    Para isso, são utilizadas medidas estatísticas como a moda do índice de produtividade
    e também valores de referência já existentes em tabelas técnicas, como SINAPI,
    SICRO e SIURB. Esses valores são então combinados por meio de uma média ponderada,
    juntamente com o valor mais representativo dos dados observados, para calcular
    um coeficiente de produtividade sugerido que possa servir como referência em
    análises e planejamentos de obras.

    Uma dúvida que surge na metodologia apresentada está relacionada ao chamado
    gráfico ou critério de suficiência utilizado no acompanhamento da produtividade.
    Esse gráfico parece representar o comportamento do resultado acumulado ao longo
    das apropriações diárias. Conforme novos dados são coletados, o índice acumulado
    tende a convergir e apresentar menor variação ao longo do tempo. A partir desse
    ponto, considera-se que existe uma quantidade suficiente de dados para realizar
    a modelagem estatística da produtividade.

    Entretanto, não fica totalmente claro qual é o critério utilizado para determinar
    essa suficiência. Não se sabe se existe um limite específico de variação percentual,
    algum teste estatístico formal ou se a avaliação é feita apenas pela observação
    visual da estabilização da curva no gráfico. Também permanece a dúvida sobre
    como esse critério considera possíveis variáveis externas ou a presença de
    outliers que possam influenciar significativamente os resultados observados
    durante o período analisado.
    """
            )