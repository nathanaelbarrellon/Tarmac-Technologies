import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Tarmac Data Analysis",
    page_icon="✈️",
    layout="wide"
)

@st.cache_data
def load_data():
    xls = pd.ExcelFile("Case - Tarmac Technologies - Nathanael.xlsx")
    df = pd.read_excel(xls, sheet_name="Data")
    # Nettoyage minimal
    df['adc'] = pd.to_datetime(df['adc'], errors='coerce')
    df['adct'] = pd.to_datetime(df['adct'], errors='coerce')
    df['task_updated_at'] = pd.to_datetime(df['task_updated_at'], errors='coerce')
    df['actual_start'] = pd.to_datetime(df['actual_start'], errors='coerce')
    df['actual_end'] = pd.to_datetime(df['actual_end'], errors='coerce')
    df['planning_start'] = pd.to_datetime(df['planning_start'], errors='coerce')
    df['planning_end'] = pd.to_datetime(df['planning_end'], errors='coerce')
    return df

df = load_data()

st.title("Interface d’analyse des opérations")
st.markdown("Les principaux KPI que j'ai jugé intéressants sont :")

# =============================
# BARRE LATÉRALE
# =============================

st.sidebar.header("🔍 Filtres")

airports = st.sidebar.multiselect(
    "Aéroport",
    sorted(df["airport_iata_code"].unique()),
    default=df["airport_iata_code"].unique()
)

aircrafts = st.sidebar.multiselect(
    "Type d’avion",
    sorted(df["aircraft"].unique()),
    default=df["aircraft"].unique()
)

official_tasks = [
    "Agent at Gate", "Bag at Aircraft", "Bag Delivery", "Boarding", "Briefing",
    "Cargo at Aircraft", "Cargo Delivery", "Check-In", "Cleaning", "Decomp Panel",
    "Disembark Pax", "Flight File", "FZFW", "Last Pax at Aircraft", "LDS", "LIR",
    "Loading", "NOTOC", "Offloading", "Pre-Boarding", "Pre-Flight", "Pushback Ready",
    "PWD Arrival", "PWD Departure", "Transit Check-in", "TRC-Pilots-brief"
]

tasks = st.sidebar.multiselect(
    "Type de tâche",
    sorted(official_tasks),
    default=official_tasks
)

# Application des filtres
filtered_df = df[
    df["airport_iata_code"].isin(airports) &
    df["aircraft"].isin(aircrafts) &
    df["task_name"].isin(tasks)
]

filtered_df2 = filtered_df

if len(aircrafts) == 0:
    st.error("Ajoutez au moins un avion.")

elif len(airports) == 0:
    st.error("Ajoutez au moins un aéroport.")

elif len(tasks) == 0:
    st.error("Ajoutez au moins une tâche.")

elif filtered_df.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

else:
    # =============================
    # KPI PRINCIPAUX
    # =============================

    col1, col2, col3, col4, col5,col6 = st.columns(6)

    punctuality_rate = filtered_df["is_punctual"].mean() * 100
    avg_duration = (filtered_df["actual_end"] - filtered_df["actual_start"]).dt.total_seconds().mean() / 60
    #avg_late = (filtered_df["actual_end"] - filtered_df["actual_start"]).dt.total_seconds().mean() / 60 - (filtered_df["planning_end"] - filtered_df["planning_start"]).dt.total_seconds().mean() / 60
    task_count = len(filtered_df)
    unique_turnarounds = filtered_df["turnaround_id"].nunique()
    punctuality_std = filtered_df["is_punctual"].std() * 100


    col1.metric("Taux de ponctualité", f"{punctuality_rate:.1f} %")
    col2.metric("Durée moyenne des tâches", f"{avg_duration:.1f} min")
    col3.metric("Nombre de tâches", f"{task_count:,}")
    col4.metric("Nombre de turnarounds distincts", f"{unique_turnarounds:,}")
    col5.metric("Variabilité ponctualité", f"{punctuality_std:.1f} %")



    st.write("Tous les KPI ci-dessus sont sont calculés à partir de toutes les tâches sélectionnées dans les filtres")
    st.markdown("""
<div style='font-size:14px; color:#ccc; line-height:1.6'>
<ul>
<li><b>Taux de ponctualité :</b> Pourcentage moyen des tâches réalisées dans les temps.</li>
<li><b>Durée moyenne des tâches :</b> Temps moyen d’exécution, utile pour détecter les tâches longues ou inefficaces.</li>
<li><b>Nombre de tâches :</b> Nombre total d’opérations enregistrées.</li>
<li><b>Nombre de turnarounds distincts :</b> Nombre de turnaround uniques observées dans les données sélectionnées.</li>
<li><b>Variabilité ponctualité :</b> dispersion des performances, permet de voir la stabilité ou l’hétérogénéité opérationnelle. Si cette dernière est élevée cela peut signifier qu'il y a certains sites, tâches qui posent problème.</li>
</ul>
</div>
""", unsafe_allow_html=True)
    
    st.markdown("<hr style='border:1px solid #333; margin:20px 0;'>", unsafe_allow_html=True)

    # =============================
    # VISUALISATIONS
    # =============================

    st.subheader("📊 Répartition des tâches")

    fig_tasks = px.histogram(
        filtered_df,
        x="task_name",
        color="is_punctual",
        barmode="group",
        title="Nombre de tâches",
        labels={"is_punctual": "Ponctuelle"},
        color_discrete_map={
            True: "#00C2FF",   # bleu = ponctuel
            False: "#4C7FFF"}   # rouge = en retard
    )
    st.plotly_chart(fig_tasks, use_container_width=True)

    st.write("L’histogramme montre le nombre de répétitions de chaque tâche et sa ponctualité associée pour les filtres sélectionnés. En passant le curseur sur une barre du graphique, on peut lire la valeur exacte du nombre d’occurrences de la tâche. Cela permet de cibler les tâches non ponctuelles les plus fréquentes afin de les corriger.")

    st.markdown("<hr style='border:1px solid #333; margin:20px 0;'>", unsafe_allow_html=True)

    st.subheader("🕓 Évolution temporelle")

    # Crée une colonne "date" propre
    filtered_df["date"] = filtered_df["task_updated_at"].dt.date

    # Moyenne du taux de ponctualité par jour
    df_time = (
        filtered_df.groupby("date")["is_punctual"]
        .mean()
        .reset_index()
        .sort_values("date")
    )

    fig_time = px.line(
        df_time,
        x="date",
        y="is_punctual",
        title="Taux de ponctualité au fil du temps",
        markers=True,
    )

    fig_time.update_traces(
        line=dict(color="#00C2FF", width=3),
        marker=dict(size=7, color="#FFFFFF", line=dict(width=2, color="#00C2FF"))
    )

    fig_time.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E0E0", size=13),
        xaxis_title="Date",
        yaxis_title="Taux de ponctualité",
        xaxis=dict(
            showgrid=False,
            tickmode="array",
            tickvals=df_time["date"],
            ticktext=[d.strftime("%d %b %Y") for d in df_time["date"]],
            tickangle=45,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            range=[0, 1],
            tickformat=".0%",
            gridcolor="rgba(255,255,255,0.1)",
            title_font=dict(size=15, color="#E0E0E0"),
        ),
        hovermode="x unified",
    )

    st.plotly_chart(fig_time, use_container_width=True)

    st.write("Ce graphique permet de suivre la ponctualité pour les différents aéroports et les différentes tâches choisies dans les filtres. Il offre une vision temporelle utile pour vérifier si un processus d’amélioration d’une tâche est (ou non) une réussite. On peut remarquer, en jouant avec les données sélerionnées, que dans l'ensemble il y a une hausse de la ponctualité au cours du temps (ce qui peut téloigner d'une volonté d'améliorer les process des tâches). ")

    st.markdown("<hr style='border:1px solid #333; margin:20px 0;'>", unsafe_allow_html=True)

     # =============================
    # ⏱️ ANALYSE DES ÉCARTS PLANIFIÉ / RÉEL
    # =============================

    st.subheader("⏱️ Analyse des écarts planifié / réel")


    # Calcul des durées planifiées et réelles
    filtered_df["durée_planifiée_min"] = (
        (filtered_df["planning_end"] - filtered_df["planning_start"])
        .dt.total_seconds() / 60
    )
    filtered_df["durée_réelle_min"] = (
        (filtered_df["actual_end"] - filtered_df["actual_start"])
        .dt.total_seconds() / 60
    )

    # Supprime les lignes avec des valeurs manquantes
    filtered_df = filtered_df.dropna(subset=["durée_planifiée_min", "durée_réelle_min"])

    # Calcul de l’écart (réel - planifié)
    filtered_df["écart_min"] = filtered_df["durée_réelle_min"] - filtered_df["durée_planifiée_min"]

    # Moyenne de l’écart par tâche
    df_ecart = (
        filtered_df.groupby("task_name")["écart_min"]
        .mean()
        .reset_index()
        .sort_values("écart_min", ascending=True)
    )


    if df_ecart.empty:
        st.warning("⚠️ Aucune donnée disponible pour les filtres sélectionnés.")
    else:
        fig_ecart = px.bar(
            df_ecart,
            x="task_name",
            y="écart_min",
            title="Écart moyen planifié / réel par tâche (en minutes)",
            color="écart_min",
            color_continuous_scale="RdYlGn_r",
            text_auto=".1f",
        )

        fig_ecart.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E0E0", size=13),
            xaxis_title="Type de tâche",
            yaxis_title="Écart moyen (min)",
            title_font=dict(size=18, color="#E0E0E0"),
            yaxis=dict(
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="#FFFFFF"
            ),
        )
        

        st.plotly_chart(fig_ecart, use_container_width=True)

    st.write("""
    Ce graphique montre l'écart moyen entre les durées planifiées et les durées réelles pour chaque tâche.
    - Une valeur **positive** → les tâches durent plus longtemps que prévu (retard).
    - Une valeur **négative** → elles sont plus rapides que prévu (avance).
    """)
    st.write("Certaines tâches, bien que sélectionnées dans le filtre, ne sont pas présenets car dans l'excel des valeurs sont manquantes dans les colonnes planifiées et réelles. Ce graphique reste tout de même intéressant pour trouver les tâches les plus en retard afin de se focaliser dessus. ")

    # =============================
    # 📊 ANALYSE PAR DIMENSION
    # =============================


    st.markdown("---")
    st.subheader(" Analyse par dimension")

    # Sélecteur de dimension d'analyse
    dimension = st.selectbox(
        "Choisir la dimension à analyser :",
        ["Aéroport", "Type d’avion", "Type de tâche"]
    )

    # Mapping pour choisir la bonne colonne
    dim_mapping = {
        "Aéroport": "airport_iata_code",
        "Type d’avion": "aircraft",
        "Type de tâche": "task_name"
    }
    dim_col = dim_mapping[dimension]

    # Calcul du taux de ponctualité moyen selon la dimension choisie
    df_dim = (
        filtered_df2.groupby(dim_col)["is_punctual"]
        .mean()
        .reset_index()
        .sort_values("is_punctual", ascending=False)
    )

    # Création du graphique
    fig_dim = px.bar(
        df_dim,
        x=dim_col,
        y="is_punctual",
        title=f"Ponctualité moyenne par {dimension.lower()}",
        text_auto=".1%",
        color="is_punctual",
        color_continuous_scale="Blues"
    )

    fig_dim.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E0E0", size=13),
        yaxis=dict(tickformat=".0%"),
        xaxis_title=dimension,
        yaxis_title="Taux de ponctualité",
        title_font=dict(size=18, color="#E0E0E0"),
    )

    st.plotly_chart(fig_dim, use_container_width=True)



    # Texte d’analyse dynamique
    st.write(f"Ce graphique présente la ponctualité moyenne par **{dimension.lower()}** selon les filtres appliqués.")
    st.write("Il permet d’identifier les segments présentant des retards fréquents et d’orienter les efforts d’amélioration en conséquence.")





    # =============================
    # TABLEAU DÉTAILLÉ
    # =============================
    st.markdown("<hr style='border:1px solid #333; margin:20px 0;'>", unsafe_allow_html=True)

    st.subheader("📋 Données filtrées")

    st.dataframe(
        filtered_df[
            ["airport_iata_code", "aircraft", "task_name",
             "actual_start", "actual_end", "custom_label", "information_type"]
        ].sort_values("actual_start")
    )
    st.write("L’affichage des données permet de retrouver rapidement une tâche spécifique grâce à la fonctionnalité de recherche. Si une tâche a été repérée dans les graphiques, ce tableau permet de la visualiser en détail.")

    st.markdown("<hr style='border:1px solid #333; margin:20px 0;'>", unsafe_allow_html=True)

    st.markdown("**Interprétation globale**")
    st.write("Cet Excel permet d’avoir un suivi pertinent dans les différents aéroports :")
    st.markdown("""
        - du taux de ponctualité, qui donne une idée claire de la performance opérationnelle ;
        - des tâches les plus fréquentes ou les plus souvent en retard, afin de les prioriser pour une amélioration.
    """)
    st.write("L'avantage avec Streamlit est que l'on peut afficher de plusieurs façons des données afin de mieux les analyser (c'est d'ailleurs ce que j'ai fait ici). On constate à travers les différentes analyses que les taux de ponctualité restent globalement trop faibles, ce qui souligne l’intérêt de mettre en place des systèmes comme ceux proposés par Tarmac Technologies pour cibler les tâches à risque et a fortiori améliorer les processus.")
    

st.caption("Nathanaël Barrellon – Tarmac Technologies – Novembre 2025")
