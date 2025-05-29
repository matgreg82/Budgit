
import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime

st.set_page_config(page_title="Budget personnel", layout="wide")
st.title("💼 Suivi budgétaire personnel")

st.sidebar.header("🔧 Paramètres mensuels")

# Revenus
st.sidebar.subheader("Revenus")
revenu_salaire = st.sidebar.number_input("Salaire net mensuel", min_value=0.0, value=3000.0)
revenu_autre = st.sidebar.number_input("Autres revenus (dividendes, etc.)", min_value=0.0, value=0.0)

# Dépenses fixes mensuelles
st.sidebar.subheader("Dépenses fixes")
loyer = st.sidebar.number_input("Loyer / Hypothèque", min_value=0.0, value=1000.0)
factures = st.sidebar.number_input("Factures (internet, électricité, etc.)", min_value=0.0, value=250.0)
abonnements = st.sidebar.number_input("Abonnements (Netflix, etc.)", min_value=0.0, value=40.0)
epargne = st.sidebar.number_input("Épargne automatique", min_value=0.0, value=300.0)

total_revenus = revenu_salaire + revenu_autre
total_fixes = loyer + factures + abonnements + epargne

st.sidebar.markdown("---")
st.sidebar.metric("Revenus fixes", f"${total_revenus:,.2f}")
st.sidebar.metric("Dépenses fixes", f"${total_fixes:,.2f}")
st.sidebar.metric("Prévision disponible", f"${(total_revenus - total_fixes):,.2f}")

st.subheader("📄 Téléverser un relevé PDF pour suivre les dépenses réelles")
uploaded_file = st.file_uploader("Fichier PDF", type="pdf")

def extract_pdf_transactions(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # Regex basique pour extraire les transactions
    pattern = r"(\d{2} \d{2}) [A-Z0-9\*\-\'\.\#\(\)\s]+ ([\d\.]+)"
    matches = re.findall(pattern, text)

    data = []
    for date, amount in matches:
        try:
            montant = float(amount)
            data.append((date, montant))
        except:
            continue

    df = pd.DataFrame(data, columns=["Date", "Montant"])
    df["Date"] = pd.to_datetime(df["Date"] + " 2025", format="%m %d %Y", errors="coerce")
    return df

if uploaded_file:
    st.markdown("### 💳 Dépenses réelles extraites")
    df_depenses = extract_pdf_transactions(uploaded_file)
    st.dataframe(df_depenses)

    total_reel = df_depenses["Montant"].sum()
    budget_restant = total_revenus - total_fixes - total_reel

    st.markdown("### 🧾 Résumé budgétaire du mois")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total dépenses fixes", f"${total_fixes:,.2f}")
    col2.metric("Total dépenses réelles", f"${total_reel:,.2f}")
    col3.metric("Reste à vivre", f"${budget_restant:,.2f}", delta=f"{budget_restant - 0:.2f}")

    st.markdown("### 📈 Dépenses journalières")
    journalier = df_depenses.groupby("Date")["Montant"].sum()
    st.line_chart(journalier)
else:
    st.info("Veuillez téléverser un relevé PDF pour voir vos dépenses réelles.")
