import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página 
# Define o título da aba do navegador, o ícone e o layout largo

st.set_page_config(
    page_title="Dashboard de Produtividade", page_icon="🏗️", layout="wide"
)


# Leitura dos dados 
# @st.cache_data faz o arquivo ser lido só uma vez e guardado na memória
# Isso evita que o Excel seja relido toda vez que o usuário mexe em um filtro

@st.cache_data
def carregar_dados():
    df = pd.read_excel("df_diarios.xlsx")
    # Filtra apenas os registros de mão de obra — requisito do enunciado
    df = df[df["tipo_insumo"] == "MAO DE OBRA"].copy()
    # Remove linhas sem ip_d ou sem nome_obra para evitar erros nos gráficos
    df = df.dropna(subset=["ip_d", "nome_obra"])
    return df


df = carregar_dados()

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

df_filtrado = df.copy()
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

# Título 
st.title("🏗️ Dashboard de Produtividade Mão de Obra")
# Aviso explicando por que os dados foram filtrados (requisito do enunciado)
st.warning(
    "⚠️ Dados filtrados para mão de obra, garantindo comparação coerente de produtividade entre os grupos."
)

# Abas
# Cria as 5 abas do dashboard
# Cada "aba" é uma variável que usamos no "with aba1:", "with aba2:", etc

aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["📋 Dados", "📐 Estatísticas", "📊 Gráficos", "🔍 Comparações", "❓ Perguntas"]
)

# Aba 1: Dados 
# Mostra a tabela com todos os registros filtrados
# TODO: FALTA ADICIONAR a tabela classificando as colunas da planilha
# (qualitativa nominal, quantitativa contínua, etc) (requisito etapa 1)
# TODO: FALTA ADICIONAR a lista de perguntas de um gestor de obras
# — requisito etapa 3 do enunciado

with aba1:
    st.subheader("Base de dados (Mão de Obra)")
    st.write(f"Total de registros: **{len(df_filtrado)}**")
    st.dataframe(df_filtrado, use_container_width=True)

# Aba 2: Estatísticas 
# Calcula e exibe as medidas de posição central e dispersão do ip_d
# ip_d é o índice de produtividade diário (principal variável da análise)
# ip_d = 1 significa que a equipe produziu exatamente o esperado
# ip_d > 1 = produziu mais que o esperado / ip_d < 1 = produziu menos

with aba2:
    st.subheader("Estatísticas descritivas do ip_d")

    # ── Medidas de posição central ──
    col1, col2, col3 = st.columns(3)
    col1.metric("Média", f"{df_filtrado['ip_d'].mean():.3f}")
    col2.metric("Mediana", f"{df_filtrado['ip_d'].median():.3f}")
    # Proteção: mode() pode retornar vazio se não houver moda definida
    moda = df_filtrado["ip_d"].mode()
    col3.metric("Moda", f"{moda[0]:.3f}" if not moda.empty else "N/A")

    # ── Medidas de dispersão ──
    col4, col5, col6 = st.columns(3)
    col4.metric("Desvio-padrão", f"{df_filtrado['ip_d'].std():.3f}")
    col5.metric("Variância", f"{df_filtrado['ip_d'].var():.3f}")
    amplitude = df_filtrado["ip_d"].max() - df_filtrado["ip_d"].min()
    col6.metric("Amplitude", f"{amplitude:.3f}")

    # Proteção: evita divisão por zero se a média for 0
    cv = (df_filtrado["ip_d"].std() / df_filtrado["ip_d"].mean()) * 100 if df_filtrado["ip_d"].mean() != 0 else 0
    st.metric("Coeficiente de Variação (CV)", f"{cv:.1f}%")
    st.info(
        "O CV indica a variabilidade relativa. CV abaixo de 15% = baixa variabilidade. Entre 15% e 30% = média. Acima de 30% = alta."
    )
    # TODO: FALTA ADICIONAR texto explicando quando usar média, mediana e moda
    # — requisito etapa 4 do enunciado
    # TODO: FALTA ADICIONAR texto explicando o que desvio, variância, amplitude
    # e CV significam na prática para produtividade — requisito etapa 5

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
        labels={"ip_d": "ip_d", "count": "Frequência"},
        color_discrete_sequence=["#378ADD"],
    )
    fig_hist.update_traces(marker_line_color="black", marker_line_width=1)
    fig_hist.update_layout(height=500, bargap=0.05)
    st.plotly_chart(fig_hist, use_container_width=True, key="hist")

    # Curva de densidade: mesma informação do histograma mas em probabilidade
    # histnorm="probability density" normaliza o eixo Y de 0 a 1
    fig_dens = px.histogram(
        df_filtrado,
        x="ip_d",
        histnorm="probability density",
        nbins=50,
        title="Curva de densidade do ip_d",
        labels={"ip_d": "ip_d"},
        color_discrete_sequence=["#1D9E75"],
    )
    fig_dens.update_traces(opacity=0.7, marker_line_color="black", marker_line_width=1)
    fig_dens.update_layout(height=500, bargap=0.05)
    st.plotly_chart(fig_dens, use_container_width=True, key="dens")

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
    st.plotly_chart(fig_box, use_container_width=True, key="box")

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
            ticktext=[t[:25] + "..." if len(t) > 25 else t for t in df_grupo["grupo"].tolist()]
        )
    )
    st.plotly_chart(fig_bar_grupo, use_container_width=True, key="bar_grupo")

# Aba 4: Comparações 
# Tabela e gráfico comparando média, mediana, desvio e CV entre as obras

with aba4:
    st.subheader("Comparação de produtividade por obra")

    # Agrupa os dados por obra e calcula as 4 métricas para cada uma
    resumo = (
        df_filtrado.groupby("nome_obra")["ip_d"]
        .agg(
            Media="mean",
            Mediana="median",
            Desvio="std",
            CV=lambda x: x.std() / x.mean() * 100 if x.mean() != 0 else 0,
        )
        .reset_index()
        .round(3)
    )

    st.dataframe(resumo, use_container_width=True)

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
    st.plotly_chart(fig_bar, use_container_width=True, key="bar_obras")

# Aba 5: Perguntas orientadoras 
# Responde as perguntas A, B, C e D do enunciado com gráfico + texto
# ATENÇÃO: esta aba usa "df" (dados completos) e não "df_filtrado"
# Isso é intencional — as respostas mostram sempre todas as obras
# para garantir que a comparação seja completa independente dos filtros

with aba5:
    st.subheader("Perguntas orientadoras")

    # Calcula resumo com todas as obras para usar nas respostas
    resumo_obras = (
        df.groupby("nome_obra")["ip_d"]
        .agg(
            Media="mean",
            Mediana="median",
            Desvio="std",
            CV=lambda x: x.std() / x.mean() * 100 if x.mean() != 0 else 0,
        )
        .reset_index()
        .round(3)
    )

    # Identifica automaticamente as obras mais/menos produtivas e estáveis
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
        st.plotly_chart(fig_box_obras, use_container_width=True, key="box_obras")
        # TODO: reescrever este texto com as palavras do grupo — requisito do enunciado
        st.write(
            f"""
        Sim, há diferenças visíveis de produtividade entre as obras.
        A obra com maior média de ip_d é a **{obra_maior}**, enquanto a com menor média é a **{obra_menor}**.
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
                ticktext=[t[:25] + "..." if len(t) > 25 else t for t in resumo_grupos.head(10)["grupo"].tolist()]
            )
        )
        st.plotly_chart(fig_bar_b, use_container_width=True, key="bar_b")
        # TODO: reescrever este texto com as palavras do grupo (requisito do enunciado)
        st.write(
            """
        Sim, a produtividade varia bastante entre os diferentes grupos de serviço.
        Serviços mais padronizados e repetitivos tendem a apresentar maior produtividade,
        enquanto serviços mais complexos ou que dependem de condições específicas apresentam
        maior variabilidade e menor ip_d médio.
        """
        )

    # Pergunta C: relação entre média e mediana
    with st.expander("C) Como está a relação entre média e mediana nos grupos?"):
        st.dataframe(resumo_obras, use_container_width=True)
        # TODO: reescrever este texto com as palavras do grupo (requisito do enunciado)
        st.write(
            f"""
        Em praticamente todas as obras, a **média é maior que a mediana**, o que indica
        a presença de valores extremos (outliers) que puxam a média para cima.
        Isso sugere que a maioria dos registros diários apresenta produtividade baixa a moderada,
        mas existem dias ou equipes com desempenho excepcionalmente alto que distorcem a média.
        Nesses casos, a **mediana é uma medida mais representativa** da produtividade típica.
        """
        )

    # Pergunta D: previsibilidade por obra (usa CV quanto menor, mais previsível)
    with st.expander(
        "D) Quais grupos apresentam produtividade mais e menos previsível?"
    ):
        # Gráfico colorido: verde = mais previsível / vermelho = menos previsível
        fig_cv = px.bar(
            resumo_obras.sort_values("CV"),
            x="nome_obra",
            y="CV",
            title="Coeficiente de Variação (CV) por Obra (quanto menor mais previsível)",
            labels={"nome_obra": "Obra", "CV": "CV (%)"},
            color="CV",
            color_continuous_scale="RdYlGn_r",
        )
        fig_cv.update_traces(marker_line_color="black", marker_line_width=1)
        fig_cv.update_layout(height=500)
        st.plotly_chart(fig_cv, use_container_width=True, key="cv")
        # TODO: reescrever este texto com as palavras do grupo (requisito do enunciado)
        st.write(
            f"""
        A obra **{obra_mais_estavel}** apresenta o menor CV, indicando comportamento mais estável
        e previsível — útil para planejamento e orçamento com maior confiança.
        Já a obra **{obra_menos_estavel}** apresenta o maior CV, o que significa alta variabilidade
        no desempenho diário, exigindo maior atenção do gestor e margens de segurança no planejamento.
        """
        )

    # Criar uma aba6 com anotações sobre o vídeo
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