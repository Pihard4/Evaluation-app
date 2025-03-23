import pandas as pd
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import streamlit as st
import openpyxl
import time  # For progress bar

# Dictionnaire pour la traduction
TRANSLATIONS = {
    "VANF": {"fr": "Valeur Actuelle Nette Financière", "en": "Financial Net Present Value"},
    "TRIF": {"fr": "Taux de Rendement Interne Financier", "en": "Financial Internal Rate of Return"},
    "DRC": {"fr": "Délai de Récupération du Capital", "en": "Capital Recovery Period"},
    "VANE": {"fr": "Valeur Actuelle Nette Économique", "en": "Economic Net Present Value"},
    "TRIE": {"fr": "Taux de Rendement Interne Économique", "en": "Economic Internal Rate of Return"},
    "RCA": {"fr": "Rendement du Capital Ajusté", "en": "Adjusted Capital Yield"}
}

def financial_evaluation(data, discount_rate):
    """Évalue les indicateurs financiers."""
    try:
        cash_flows = data['Revenues'] - data['Total_Costs']
        npv_f = npf.npv(discount_rate, cash_flows)
        irr_f = npf.irr(cash_flows)
        drc = (cash_flows < 0).sum()
        return npv_f, irr_f, drc
    except Exception as e:
        st.error(f"Erreur dans l'évaluation financière : {e}")
        return None, None, None

def economic_evaluation(data, discount_rate):
    """Évalue les indicateurs économiques."""
    try:
        cash_flows = data['Corrected_Revenues'] - data['Corrected_Costs'] + data['Externalities']
        npv_e = npf.npv(discount_rate, cash_flows)
        irr_e = npf.irr(cash_flows)
        rca = npv_e / data['Corrected_Costs'].sum()
        return npv_e, irr_e, rca
    except Exception as e:
        st.error(f"Erreur dans l'évaluation économique : {e}")
        return None, None, None

def main():
    st.title("📊 Évaluation Financière et Économique")
    st.sidebar.header("Paramètres")
    language = st.sidebar.selectbox("Choisissez une langue", ["fr", "en"])
    uploaded_file = st.sidebar.file_uploader("Glissez-déposez un fichier Excel", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
            sheets = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}
            sheet_name = st.sidebar.selectbox("Sélectionnez une feuille", xls.sheet_names)
            data = sheets[sheet_name]
            data.fillna(0, inplace=True)
            st.success("Fichier chargé avec succès !")
            st.write("### Aperçu des données")
            st.dataframe(data)
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier : {e}")
            return
        
        discount_rate = st.sidebar.number_input("Taux d'actualisation (%)", min_value=0.0, max_value=100.0, value=8.0) / 100.0
        
        if st.sidebar.button("Générer l'évaluation"):
            progress = st.progress(0)
            results = []
            
            for i in range(1, 101, 20):  # Simulating progress
                time.sleep(0.1)
                progress.progress(i)
            
            has_financial = {'Year', 'Total_Costs', 'Revenues', 'Residual_Value'}.issubset(data.columns)
            has_economic = {'Corrected_Costs', 'Corrected_Revenues', 'Externalities'}.issubset(data.columns)
            
            if has_financial:
                npv_f, irr_f, drc = financial_evaluation(data, discount_rate)
                if npv_f is not None:
                    results.append({'Indicateur': TRANSLATIONS['VANF'][language], 'Valeur': npv_f})
                if irr_f is not None:
                    results.append({'Indicateur': TRANSLATIONS['TRIF'][language], 'Valeur': irr_f})
                if drc is not None:
                    results.append({'Indicateur': TRANSLATIONS['DRC'][language], 'Valeur': drc})
            
            if has_economic:
                npv_e, irr_e, rca = economic_evaluation(data, discount_rate)
                if npv_e is not None:
                    results.append({'Indicateur': TRANSLATIONS['VANE'][language], 'Valeur': npv_e})
                if irr_e is not None:
                    results.append({'Indicateur': TRANSLATIONS['TRIE'][language], 'Valeur': irr_e})
                if rca is not None:
                    results.append({'Indicateur': TRANSLATIONS['RCA'][language], 'Valeur': rca})
            
            progress.progress(100)
            
            results_df = pd.DataFrame(results)
            st.write("### Résultats de l'analyse")
            st.write(results_df)
            
            if not results_df.empty:
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['blue', 'red', 'green', 'purple', 'orange', 'cyan']
                bars = ax.bar(results_df['Indicateur'], results_df['Valeur'], color=colors)
                ax.set_xticklabels(results_df['Indicateur'], rotation=45, ha="right", fontsize=12)
                ax.set_xlabel("Indicateurs", fontsize=14)
                ax.set_ylabel("Valeur", fontsize=14)
                ax.set_title("Analyse Financière et Économique", fontsize=16)
                legend_patches = [plt.Rectangle((0,0),1,1, color=color) for color in colors]
                ax.legend(legend_patches, TRANSLATIONS.keys(), loc="upper right")
                st.pyplot(fig)
            
if __name__ == "__main__":
    main()