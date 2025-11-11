# ============================================
# ✈️ TARMAC DATA ANALYSIS DASHBOARD
# Author: Nathanaël Barrellon
# ============================================

import pandas as pd
import streamlit as st
import plotly.express as px

# =============================
# CONFIGURATION DE L'APPLICATION
# =============================

st.set_page_config(
    page_title="Tarmac Data Analysis",
    page_icon="✈️",
    layout="wide"
)

# =============================
# CHARGEMENT DES DONNÉES
# =============================

@st.cache_data
def load_data():
    xls = pd.ExcelFile("Case - Tarmac Technologies - Nathanael.xlsx")
    df = pd.read_excel(xls, sheet_name="Data")
    df['adc'] = pd.to_datetime(df['adc'], errors='coerce')
    df['adct'] = pd.to_datetime(df['adct'], errors='coerce')
    df['task_updated_at'] = pd.to_datetime(df['task_updated_at'], errors='coerce')
    df['actual_start'] = pd.to_datetime(df['actual_start'], errors='coerce')
    df['actual_end'] = pd.to_datetime(df['actual_end'], errors='coerce')
    return df

df = load_data()

st.title("TARMAC Technologies")
st.markdown("---")

st.subheader("📂 Structure du fichier Excel")

st.markdown("""
Le fichier contient **2 onglets principaux :**
- **Intro** → description du contexte du cas.
- **Data** → base principale, avec **5564 lignes et 24 colonnes**, contenant des informations opérationnelles.

**Champs importants de la feuille “Data” :**
""") 

data_overview = pd.DataFrame({
    "Catégorie": [
        "✈️ Vols / Turnaround",
        "🕓 Temps",
        "🧩 Tâches",
        "📑 Informations",
        "👷‍♂️ Suivi"
    ],
    "Exemples de colonnes": [
        "aircraft, airport_iata_code, turnaround_id",
        "std, atd, sta, ata, adc, adct",
        "task_name, task_is_applicable, is_punctual",
        "custom_label, information_type, checkbox_value, text_value",
        "task_updated_at, actual_start, actual_end"
    ],
    "Description": [
        "Identifiants de turnaround (TRC)",
        "Heures planifiées et réelles",
        "Liste des actions effectuées au sol",
        "Données ou remarques associées",
        "Historique d’exécution"
    ]
})

# Affichage du tableau
st.dataframe(
    data_overview,
    hide_index=True,
    use_container_width=True
)

st.write("")
st.write("")
st.write("Avant d’analyser les données, j'ai jugé important de chercher à comprendre la signification de chaque colonne (en recherchant ou en déduisant avec les valeurs). Le tableau ci-dessous en présente une synthèse, dans l’ordre d’apparition dans le fichier Excel fourni :")

data_dict = pd.DataFrame({
    "Colonne": [
        "aircraft", "std", "atd", "sta", "ata", "adc", "adct",
        "task_name", "task_is_applicable", "is_punctual",
        "planning_start", "actual_start", "planning_end", "actual_end",
        "custom_label", "addinfo_is_applicable", "information_type",
        "checkbox_value", "text_value", "datetime_value", "number_value",
        "airport_iata_code", "turnaround_id", "task_updated_at"
    ],
    "Signification": [
        "Type d’avion concerné par le turnaround",
        "Heure planifiée de départ du vol",
        "Heure réelle de départ du vol",
        "Heure planifiée d’arrivée du vol",
        "Heure réelle d’arrivée du vol",
        "Heure réelle de fermeture de toutes les portes",
        "Heure planifiée de fermeture de toutes les portes",
        "Nom de la tâche (ex : Boarding, Cleaning, Bag Delivery)",
        "Indique si la tâche est applicable pour ce turnaround",
        "Indique si la tâche a été effectuée dans le délai prévu",
        "Heure planifiée de début de la tâche",
        "Heure réelle de début de la tâche",
        "Heure planifiée de fin de la tâche",
        "Heure réelle de fin de la tâche",
        "Libellé personnalisé ou information associée à la tâche",
        "Indique si des informations additionnelles sont présentes pour la tâche",
        "Type de donnée enregistrée (texte, nombre, date, case à cocher)",
        "Booléen",
        "Valeur textuelle saisie (commentaire, nom, note, etc.)",
        "Valeur de type date/heure saisie",
        "Valeur numérique saisie (quantité, durée, numéro tel, etc.)",
        "Code IATA de l’aéroport",
        "Identifiant unique du cycle sol (rotation avion)",
        "Date et heure de la dernière mise à jour de la tâche"
    ]
})

st.dataframe(
    data_dict,
    hide_index=True,
    use_container_width=True
)


st.markdown("---")
st.subheader("🧮 Ce que l’on peut analyser")

st.write("")
st.markdown("""
En découvrant cet Excel, j’ai tout de suite été interpellé par l’aspect temporel et la notion de ponctualité des tâches, qui semblent d’ailleurs être cohérent avec la démarche de Tarmac Technologies qui vise à favoriser des opérations plus fluides.
En travaillant sur l'excel fourni, l'interface permet donc de :
- Visualiser le **taux de ponctualité global et par type de tâche**,  
- Mesurer les **durées moyennes des opérations**,  
- Comparer la **performance entre aéroports**,  
- Explorer **chaque tâche en détail** (type, durée, statut).

L’ensemble est entièrement **interactif et filtrable** par :
- Aéroport (`airport_iata_code`)  
- Type d’avion (`aircraft`)  
- Type de tâche (`task_name`)

Cela permet d'avoir un apercu personnalisable en fonction des besoins de l'utilisateur du dashboard.
""")

st.info("""
👉 Pour accéder à la partie interactive, cliquer sur **"Analyse"** dans le menu de gauche.
""")

st.markdown("---")
st.caption("Nathanaël Barrellon – Tarmac Technologies – Novembre 2025")
