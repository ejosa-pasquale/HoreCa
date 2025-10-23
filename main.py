import streamlit as st
import pandas as pd
import plotly.express as px
import math 
from typing import Dict, Any, Union

# ==============================================================================
# 0. FUNZIONE DI TRADUZIONE MOCK (DA SOSTITUIRE CON LA TUA VERA IMPLEMENTAZIONE)
#    Ho mantenuto il dizionario per rendere il codice immediatamente eseguibile.
# ==============================================================================

def get_text(key: str) -> str:
    """Funzione Mock per la traduzione dei testi. SOSTITUISCI CON LA TUA IMPLEMENTAZIONE."""
    texts = {
        # -- TITOLI PRINCIPALI --
        "performance_eval_header": "Valutazione del Rendimento del Punto di Ricarica 🔋",
        "performance_eval_intro": "Analizza la fattibilità economica e la capacità operativa della tua infrastruttura di ricarica.",
        "calculate_performance_spinner": "Analisi delle performance in corso...",
        "performance_analysis_complete": "Analisi delle performance completata!",
        "configure_and_calculate_point": "Configura i parametri e premi 'Calcola Performance' per avviare l'analisi.",
        "optimization_recommendations": "💡 Raccomandazioni e Ottimizzazione",
        
        # -- INPUT SEZIONE A: PREVISIONE DOMANDA --
        "demand_forecast_header": "A. Previsione della Domanda e Uso (Base)",
        "expected_daily_cars": "Auto Previste al Giorno (Media)",
        "avg_energy_per_car": "Energia Media Richiesta per Auto (kWh)",
        "avg_charge_time": "Tempo Medio di Ricarica (h)",
        "turnover_time": "Tempo di Turnover/Setup (h)", # NEW: Tempo per parcheggio/spostamento
        
        # -- INPUT SEZIONE B: CONFIGURAZIONE OPERATIVA --
        "operational_config_header": "B. Configurazione Operativa e Disponibilità",
        "daily_op_hours": "Ore Operative Giornaliere (h)",
        "annual_op_days": "Giorni Attivi Annuali",
        "infra_utilization_prob": "Affidabilità/Efficienza Impianto (%)",

        # -- INPUT SEZIONE C: CONFIGURAZIONE HARDWARE (CAPEX) --
        "charger_point_config": "C. Configurazione Hardware (Colonnine e Potenza)",
        "select_quantify_chargers": "Seleziona e Quantifica i Caricatori",
        "ac22_chargers_eval": "Colonnine AC 22 kW", "dc20_chargers_eval": "Colonnine DC 20 kW",
        "dc30_chargers_eval": "Colonnine DC 30 kW", "dc40_chargers_eval": "Colonnine DC 40 kW",
        "dc60_chargers_eval": "Colonnine DC 60 kW", "dc90_chargers_eval": "Colonnine DC 90 kW",
        
        # -- INPUT SEZIONE D: PARAMETRI FINANZIARI (RICAVI/OPEX/CAPEX) --
        "financial_params_header": "D. Parametri Finanziari e Costi Annuali",
        "energy_sale_price": "Prezzo di Vendita (Eur/kWh)",
        "energy_purchase_cost": "Costo di Acquisto Energia (Eur/kWh)",
        "max_initial_investment": "Budget Massima Iniziale (€)",
        "useful_life_years": "Vita Utile Attesa (Anni)",
        "annual_charger_maintenance_cost": "Costo Manutenzione Annuale (€)",
        "annual_software_cost": "Costo Software/Piattaforma Annuale (€)",
        "annual_insurance_cost": "Costo Assicurazione Annuale (€)",
        "annual_land_cost": "Costo Affitto/Terreno Annuale (€)",
        
        # -- OUTPUT METRICHE BASE --
        "charging_point_summary": "Riepilogo Operativo",
        "total_installed_power": "Potenza Totale Installata",
        "estimated_annual_energy_delivered": "Energia Erogata Annua (Stimata)",
        "daily_cars_served": "Auto Servite Giornaliere",
        "plug_utilization_rate": "Tasso di Utilizzo Posti/Stalli", # NEW METRIC
        "key_economic_indicators": "Indicatori Economici Chiave",
        "estimated_annual_revenue": "Ricavo Annuo Stimato",
        "total_system_cost_capex": "Costo Totale Investimento (CapEx)",
        "annual_operating_cost_opex": "Costo Operativo Annuo (OpEx Totale)",
        "estimated_annual_net_profit": "Profitto Netto Annuo Stimato",
        "within_budget": "✅ Nel Budget", "over_budget": "❌ Oltre Budget",
        "roi_test": "ROI Annuale (Netto)",
        "payback_period": "Tempo di Ritorno (Payback)",
        "infinite_payback": "Infinito (> Vita Utile)", "years_label": "anni",

        # -- OUTPUT TABELLE/GRAFICI --
        "detailed_financial_analysis": "Analisi Finanziaria Dettagliata",
        "detailed_visualization_tab": "Visualizzazione Operativa",
        "financial_summary_tab": "Riepilogo Economico",
        "payback_trend_tab": "Andamento Payback",
        "investment_distribution_tab": "Distribuzione Investimento (CapEx)",
        "operational_cost_breakdown_tab": "Dettaglio Costi Operativi (OpEx)", 
        "cars_served_vs_not_served": "Auto Servite vs. Non Servite (Giornaliere)",
        "served_cars": "Auto Servite", "not_served_cars": "Auto Non Servite",
        "estimated_monthly_energy_delivered": "Energia Erogata Mensile (KWh)",
        "month_label": "Mese", "energy_kwh_label": "Energia (kWh)",
        "annual_financial_summary": "Riepilogo Finanziario Annuale",
        "revenue_label": "Ricavi", "cost_label_short": "Costi", "profit_label_short": "Profitto",
        "financial_summary_category_label": "Voce di Bilancio", "financial_summary_value_label": "Valore (€)",
        "cumulative_net_profit_trend": "Andamento Profitto Netto Cumulativo",
        "payback_not_calculable": "Il Payback non è calcolabile (Profitto Netto Annuo non positivo).",
        "year_label": "Anno", "cumulative_net_profit_label": "Profitto Netto Cumulativo (€)",
        "payback_line": "Ritorno sull'Investimento a {years:.1f} anni",
        "charger_cost_component": "Costo Colonnine (Hardware)", "installation_cost_component": "Costo Installazione/Opere",
        "annual_cost_breakdown_header": "Dettaglio Costi Operativi Totali Annuali (OpEx)",
        "energy_cost_line": "Costo Energia Acquistata", "amortization_cost_line": "Costo Ammortamento (CapEx)",
        "maintenance_cost_line": "Costo Manutenzione", "software_cost_line": "Costo Software/Piattaforma",
        "insurance_cost_line": "Costo Assicurazione", "land_cost_line": "Costo Terreno/Affitto",
        "total_opex_line": "Totale Costi Operativi (OpEx)",
        "calculate_point_performance": "Calcola Performance e ROI",
        # -- RACCOMANDAZIONI --
        "highly_utilized_infra": "⚠️ L'infrastruttura è altamente utilizzata o satura.",
        "underutilized_infra": "ℹ️ L'infrastruttura sembra essere sottoutilizzata.",
        "cars_not_served_warning": "⚠️ Non tutte le auto sono state servite! ({count} auto non servite/giorno).",
        "add_more_chargers_rec": "Considera l'aggiunta di ulteriori stalli/colonnine o un aumento della potenza.",
        "reduce_chargers_rec": "Se il Payback è negativo, valuta la riduzione del CapEx.",
        "negative_net_profit_warning": "❌ Profitto Netto Annuale Non Positivo. L'investimento non è sostenibile.",
        "investment_over_budget": "🛑 Il costo totale di investimento (CapEx) è superiore al budget massimo impostato.",

        # ... (Mantieni solo le chiavi usate per brevità)
    }
    return texts.get(key, f"_{key}_")

# ==============================================================================
# 1. LOGICA DI CALCOLO (MIGLIORATA CON CAPACITÀ DI SERVIZIO)
# ==============================================================================

GIORNI_ANNUI_TAB3 = 260 # Default value

def calculate_charging_point_performance(params: Dict[str, Union[int, float]]) -> Dict[str, Any]:
    """
    Calcola il rendimento e il ROI di un punto di ricarica,
    considerando sia la capacità energetica che la capacità di servizio (sessioni).
    """
    
    # 1. CONFIGURAZIONE HARDWARE E CAPEX
    potenza_totale_kw = (
        params['ac_22'] * 22 + params['dc_20'] * 20 + params['dc_30'] * 30 +
        params['dc_40'] * 40 + params['dc_60'] * 60 + params['dc_90'] * 90
    )
    costo_colonnine = (
        params['ac_22'] * 1000 + params['dc_20'] * 8000 + params['dc_30'] * 12000 +
        params['dc_40'] * 15000 + params['dc_60'] * 18000 + params['dc_90'] * 25000
    )
    costo_installazione = potenza_totale_kw * 150 # Stima 150€/kW
    costo_totale_investimento = costo_colonnine + costo_installazione

    # 2. CAPACITÀ OPERATIVA (I due colli di bottiglia)
    
    # Capacità 1: Basata sull'Energia Massima Erogabile
    energia_massima_capacita = potenza_totale_kw * params['ore_disponibili'] * (params['utilizzo_percentuale'] / 100)

    # Capacità 2: Basata sul Numero Massimo di Sessioni (Tempo di Occupazione)
    tempo_totale_slot = params['tempo_ricarica_media'] + params['tempo_turnover']
    num_totale_colonnine = params['ac_22'] + params['dc_20'] + params['dc_30'] + params['dc_40'] + params['dc_60'] + params['dc_90']
    
    if tempo_totale_slot > 0 and num_totale_colonnine > 0:
        sessioni_massime_giorno = (num_totale_colonnine * params['ore_disponibili']) / tempo_totale_slot
        energia_massima_sessioni = sessioni_massime_giorno * params['kwh_per_auto']
    else:
        sessioni_massime_giorno = 0
        energia_massima_sessioni = 0

    # 3. ENERGIA EROGATA EFFETTIVA E METRICHE DI SERVIZIO

    energia_richiesta_totale_giorno = params['num_auto_giorno'] * params['kwh_per_auto']
    
    # Energia Erogata = Il minimo tra Domanda, Capacità Energetica e Capacità di Servizio
    energia_erogata_giorno = min(
        energia_richiesta_totale_giorno, 
        energia_massima_capacita,
        energia_massima_sessioni
    )
    
    energia_erogata_annuo = energia_erogata_giorno * params['giorni_attivi']

    # Auto Servite e Metriche di Utilizzo
    auto_servite = math.floor(energia_erogata_giorno / params['kwh_per_auto']) if params['kwh_per_auto'] > 0 else 0
    auto_non_servite = max(0, params['num_auto_giorno'] - auto_servite)

    tasso_utilizzo_plug = (auto_servite / sessioni_massime_giorno) * 100 if sessioni_massime_giorno > 0 else 0
    tasso_utilizzo_energetico = (energia_erogata_giorno / energia_massima_capacita) * 100 if energia_massima_capacita > 0 else 0

    # 4. CONTO ECONOMICO (ANNUO)
    
    # Ricavi
    guadagno_annuo = energia_erogata_annuo * params['prezzo_vendita']

    # Costi Operativi (OpEx)
    costo_operativo_energia_annuo = energia_erogata_annuo * params['costo_acquisto_energia_kwh']
    
    # Ammortamento (lineare sul CapEx)
    costo_ammortamento_annuo = (
        costo_totale_investimento / params['vita_utile_anni'] 
        if params['vita_utile_anni'] > 0 
        else costo_totale_investimento
    )

    costo_operativo_totale_annuo = (
        costo_operativo_energia_annuo +
        params['costo_manutenzione_annuale'] +
        params['costo_software_annuale'] +
        params['costo_assicurazione_annuale'] +
        params['costo_terreno_annuale'] +
        costo_ammortamento_annuo
    )

    # Profitto e ROI
    profitto_netto_annuo = guadagno_annuo - costo_operativo_totale_annuo
    
    ROI = (profitto_netto_annuo / costo_totale_investimento) * 100 if costo_totale_investimento > 0 else 0
    
    payback_period = costo_totale_investimento / profitto_netto_annuo if profitto_netto_annuo > 0 else float('inf')
    
    if payback_period > params['vita_utile_anni']:
        payback_period = float('inf')

    # 5. RISULTATI
    return {
        'potenza_totale_kw': potenza_totale_kw,
        'energia_erogata_annuo': energia_erogata_annuo,
        'auto_servite': auto_servite,
        'auto_non_servite': auto_non_servite,
        'guadagno_annuo': guadagno_annuo,
        'costo_totale_investimento': costo_totale_investimento,
        'costo_operativo_totale_annuo': costo_operativo_totale_annuo,
        'profitto_netto_annuo': profitto_netto_annuo,
        'ROI': ROI,
        'payback_period': payback_period,
        'entro_budget': costo_totale_investimento <= params['budget'],
        'tasso_utilizzo_energetico': tasso_utilizzo_energetico,
        'tasso_utilizzo_plug': tasso_utilizzo_plug,
        
        # Dettagli per la visualizzazione
        'costo_operativo_energia_annuo': costo_operativo_energia_annuo,
        'costo_ammortamento_annuo': costo_ammortamento_annuo,
        'costo_colonnine': costo_colonnine, 
        'costo_installazione': costo_installazione, 
    }

# ==============================================================================
# 2. INTERFACCIA UTENTE STREAMLIT (CON STRUTTURA UX MIGLIORATA)
# ==============================================================================

# Simula l'ambiente 'with tab3:' del tuo codice originale
with st.container(): 
    st.header(get_text("performance_eval_header"))
    st.markdown(get_text("performance_eval_intro"))

    if 'risultati_tab3' not in st.session_state:
        st.session_state.risultati_tab3 = None

    # --- A. PREVISIONE DOMANDA E USO (BASE) ---
    st.subheader(get_text("demand_forecast_header"))
    with st.expander(get_text("demand_forecast_header"), expanded=True):
        col_domanda1, col_domanda2 = st.columns(2)
        
        with col_domanda1:
            num_auto_giorno_tab3 = st.number_input(get_text("expected_daily_cars"), 1, 1000, 50, step=5, key="tab3_num_auto")
            kwh_per_auto_tab3 = st.number_input(get_text("avg_energy_per_car"), 5, 100, 30, step=5, key="tab3_kwh_auto")
        
        with col_domanda2:
            tempo_ricarica_media_tab3 = st.number_input(get_text("avg_charge_time"), 0.5, 12.0, 2.0, step=0.1, key="tab3_tempo_ric")
            tempo_turnover_tab3 = st.number_input(get_text("turnover_time"), 0.0, 1.0, 0.25, step=0.05, key="tab3_tempo_turnover")

    # --- B. CONFIGURAZIONE OPERATIVA E DISPONIBILITÀ ---
    st.subheader(get_text("operational_config_header"))
    with st.expander(get_text("operational_config_header"), expanded=False):
        col_op1, col_op2 = st.columns(2)
        with col_op1:
            ore_disponibili_tab3 = st.slider(get_text("daily_op_hours"), 1, 24, 8, step=1, key="tab3_ore_op")
            giorni_attivi_tab3 = st.slider(get_text("annual_op_days"), 1, 365, GIORNI_ANNUI_TAB3, step=5, key="tab3_giorni_op")
        with col_op2:
            utilizzo_percentuale_tab3 = st.slider(get_text("infra_utilization_prob"), 10, 100, 85, step=5, key="tab3_utilizzo")
            
    # --- C. CONFIGURAZIONE HARDWARE (CAPEX) ---
    st.subheader(get_text("charger_point_config"))
    with st.expander(get_text("select_quantify_chargers"), expanded=True):
        cols_chargers_tab3 = st.columns(3)
        with cols_chargers_tab3[0]:
            ac_22_tab3 = st.number_input(get_text("ac22_chargers_eval"), 0, 50, 2, key="tab3_ac22")
            dc_20_tab3 = st.number_input(get_text("dc20_chargers_eval"), 0, 20, 0, key="tab3_dc20")
        with cols_chargers_tab3[1]:
            dc_30_tab3 = st.number_input(get_text("dc30_chargers_eval"), 0, 20, 0, key="tab3_dc30")
            dc_40_tab3 = st.number_input(get_text("dc40_chargers_eval"), 0, 20, 0, key="tab3_dc40")
        with cols_chargers_tab3[2]:
            dc_60_tab3 = st.number_input(get_text("dc60_chargers_eval"), 0, 20, 0, key="tab3_dc60")
            dc_90_tab3 = st.number_input(get_text("dc90_chargers_eval"), 0, 20, 0, key="tab3_dc90")

    # --- D. PARAMETRI FINANZIARI E COSTI ANNUALI (RICAVI/OPEX) ---
    st.subheader(get_text("financial_params_header"))
    with st.expander(get_text("financial_params_header"), expanded=False):
        col_fin1, col_fin2 = st.columns(2)
        
        with col_fin1:
            prezzo_vendita_tab3 = st.number_input(get_text("energy_sale_price"), 0.10, 1.00, 0.25, step=0.05, key="tab3_prezzo")
            costo_acquisto_energia_kwh_tab3 = st.number_input(get_text("energy_purchase_cost"), 0.05, 0.50, 0.15, step=0.01, key="tab3_costo_acquisto_energia")
            budget_tab3 = st.number_input(get_text("max_initial_investment"), 0, 500000, 20000, step=1000, key="tab3_budget")
            vita_utile_anni_tab3 = st.number_input(get_text("useful_life_years"), 1, 30, 10, step=1, key="tab3_vita_utile")
        
        with col_fin2:
            costo_manutenzione_annuale_tab3 = st.number_input(get_text("annual_charger_maintenance_cost"), 0, 50000, 500, step=100, key="tab3_manutenzione_annuale")
            costo_software_annuale_tab3 = st.number_input(get_text("annual_software_cost"), 0, 20000, 1000, step=100, key="tab3_software_annuale")
            costo_assicurazione_annuale_tab3 = st.number_input(get_text("annual_insurance_cost"), 0, 10000, 200, step=50, key="tab3_assicurazione_annuale")
            costo_terreno_annuale_tab3 = st.number_input(get_text("annual_land_cost"), 0, 50000, 0, step=100, key="tab3_terreno_annuale")
            
    # Bottone di Calcolo
    if st.button(get_text("calculate_point_performance"), key="tab3_calcola", type="primary"):
        params_tab3 = {
            'num_auto_giorno': num_auto_giorno_tab3, 'kwh_per_auto': kwh_per_auto_tab3,
            'tempo_ricarica_media': tempo_ricarica_media_tab3, 'tempo_turnover': tempo_turnover_tab3,
            'ore_disponibili': ore_disponibili_tab3, 'giorni_attivi': giorni_attivi_tab3,
            'prezzo_vendita': prezzo_vendita_tab3, 'costo_acquisto_energia_kwh': costo_acquisto_energia_kwh_tab3,
            'utilizzo_percentuale': utilizzo_percentuale_tab3, 'budget': budget_tab3,
            'ac_22': ac_22_tab3, 'dc_20': dc_20_tab3, 'dc_30': dc_30_tab3, 
            'dc_40': dc_40_tab3, 'dc_60': dc_60_tab3, 'dc_90': dc_90_tab3,
            'costo_manutenzione_annuale': costo_manutenzione_annuale_tab3,
            'costo_software_annuale': costo_software_annuale_tab3,
            'costo_assicurazione_annuale': costo_assicurazione_annuale_tab3,
            'costo_terreno_annuale': costo_terreno_annuale_tab3,
            'vita_utile_anni': vita_utile_anni_tab3
        }

        with st.spinner(get_text("calculate_performance_spinner")):
            risultati_tab3_temp = calculate_charging_point_performance(params_tab3)
            st.session_state.risultati_tab3 = risultati_tab3_temp 
        st.success(get_text("performance_analysis_complete"))
    
    # --- RISULTATI E OUTPUT ---
    
    if st.session_state.risultati_tab3 is not None:
        risultati_tab3 = st.session_state.risultati_tab3
        st.divider()

        # RIEPILOGO OPERATIVO
        st.subheader(get_text("charging_point_summary"))
        col1_tab3, col2_tab3, col3_tab3, col4_tab3 = st.columns(4)
        
        col1_tab3.metric(get_text("total_installed_power"), f"{risultati_tab3['potenza_totale_kw']} kW")
        col2_tab3.metric(get_text("estimated_annual_energy_delivered"), f"{(risultati_tab3['energia_erogata_annuo']/1000):,.1f} MWh") # Convertito in MWh
        col3_tab3.metric(get_text("daily_cars_served"), f"{risultati_tab3['auto_servite']}/{num_auto_giorno_tab3}")
        col4_tab3.metric(get_text("plug_utilization_rate"), f"{risultati_tab3['tasso_utilizzo_plug']:.1f}%")

        # RIEPILOGO FINANZIARIO CHIAVE
        st.subheader(get_text("key_economic_indicators"))
        col5_tab3, col6_tab3, col7_tab3 = st.columns(3)
        col5_tab3.metric(get_text("total_system_cost_capex"), f"€{risultati_tab3['costo_totale_investimento']:,.0f}", 
                         get_text("within_budget") if risultati_tab3['entro_budget'] else get_text("over_budget"))
        col6_tab3.metric(get_text("estimated_annual_revenue"), f"€{risultati_tab3['guadagno_annuo']:,.0f}")
        col7_tab3.metric(get_text("annual_operating_cost_opex"), f"€{risultati_tab3['costo_operativo_totale_annuo']:,.0f}")

        st.divider()
        st.subheader(get_text("detailed_financial_analysis"))

        # RISULTATI FINANZIARI PROFONDI
        col_profit, col_roi, col_payback = st.columns(3)
        col_profit.metric(get_text("estimated_annual_net_profit"), f"€{risultati_tab3['profitto_netto_annuo']:,.0f}")
        col_roi.metric(get_text("roi_test"), f"{risultati_tab3['ROI']:.1f}%")
        
        payback_display = f"{risultati_tab3['payback_period']:.1f} {get_text('years_label')}" if risultati_tab3['payback_period'] != float('inf') else get_text('infinite_payback')
        col_payback.metric(get_text("payback_period"), payback_display)

        # TABELLE E GRAFICI
        tab3_1, tab3_2, tab3_3, tab3_4, tab3_5 = st.tabs([
            get_text("detailed_visualization_tab"), 
            get_text("financial_summary_tab"), 
            get_text("payback_trend_tab"), 
            get_text("investment_distribution_tab"),
            get_text("operational_cost_breakdown_tab")
        ])

        with tab3_1: # Visualizzazione Operativa
            st.markdown(f"#### {get_text('cars_served_vs_not_served')}")
            df_auto = pd.DataFrame({"Category": [get_text("served_cars"), get_text("not_served_cars")], "Value": [risultati_tab3['auto_servite'], risultati_tab3['auto_non_servite']]})
            st.plotly_chart(px.pie(df_auto, values="Value", names="Category", title=get_text("cars_served_vs_not_served"), template="plotly_white"), use_container_width=True)

            st.markdown(f"#### {get_text('estimated_monthly_energy_delivered')}")
            months = list(range(1, 13))
            # Stagionalità per realismo
            monthly_energy = [risultati_tab3['energia_erogata_annuo'] / 12 * (1 + 0.1 * math.sin(2 * math.pi * (i - 4) / 12)) for i in months] 
            df_monthly = pd.DataFrame({"Mese": months, "EnergiaKWh": monthly_energy})
            fig = px.line(df_monthly, x="Mese", y="EnergiaKWh", title=get_text("estimated_monthly_energy_delivered"), markers=True, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)


        with tab3_2: # Riepilogo Economico (Waterfall Chart)
            st.markdown(f"#### {get_text('annual_financial_summary')}")
            df_financial_summary = pd.DataFrame({
                "Category": [get_text("estimated_annual_revenue"), get_text("annual_operating_cost_opex"), get_text("estimated_annual_net_profit")],
                "Value": [risultati_tab3['guadagno_annuo'], -risultati_tab3['costo_operativo_totale_annuo'], risultati_tab3['profitto_netto_annuo']],
                "Type": [get_text("revenue_label"), get_text("cost_label_short"), get_text("profit_label_short")]
            })
            fig_financial_summary = px.bar(df_financial_summary, x="Category", y="Value", color="Type", 
                                            color_discrete_map={get_text("revenue_label"): "green", get_text("cost_label_short"): "red", get_text("profit_label_short"): "blue"},
                                            title=get_text("annual_financial_summary"), template="plotly_white")
            st.plotly_chart(fig_financial_summary, use_container_width=True)

        with tab3_3: # Andamento Payback
            st.markdown(f"#### {get_text('cumulative_net_profit_trend')}")
            if risultati_tab3['profitto_netto_annuo'] > 0 and risultati_tab3['payback_period'] != float('inf'):
                max_years = min(15, math.ceil(risultati_tab3['payback_period']) + 3)
                years = list(range(1, max_years + 1))
                cumulative_profit = [risultati_tab3['profitto_netto_annuo'] * y for y in years]
                
                df_payback = pd.DataFrame({"Anno": years, "Profitto Netto Cumulativo (€)": cumulative_profit, "Investimento Iniziale": [risultati_tab3['costo_totale_investimento']] * len(years)})

                fig_payback = px.line(df_payback, x="Anno", y=["Profitto Netto Cumulativo (€)", "Investimento Iniziale"], title=get_text("cumulative_net_profit_trend"), markers=True, color_discrete_map={"Profitto Netto Cumulativo (€)": "green", "Investimento Iniziale": "red"}, template="plotly_white")
                
                if risultati_tab3['payback_period'] > 0:
                    fig_payback.add_vline(x=risultati_tab3['payback_period'], line_width=2, line_dash="dash", line_color="blue", annotation_text=get_text("payback_line").format(years=risultati_tab3['payback_period']), annotation_position="top right")
                st.plotly_chart(fig_payback, use_container_width=True)
            else:
                st.info(get_text("payback_not_calculable"))

        with tab3_4: # Distribuzione Investimento (CapEx)
            st.markdown(f"#### {get_text('initial_investment_cost_distribution')}")
            df_investment_breakdown = pd.DataFrame({"Component": [get_text("charger_cost_component"), get_text("installation_cost_component")], "Cost": [risultati_tab3['costo_colonnine'], risultati_tab3['costo_installazione']]})
            st.plotly_chart(px.pie(df_investment_breakdown, values="Cost", names="Component", title=get_text("initial_investment_cost_distribution"), color_discrete_sequence=px.colors.qualitative.Set2, template="plotly_white"), use_container_width=True)
            
        with tab3_5: # Dettaglio Costi Operativi (OpEx)
            st.markdown(f"#### {get_text('annual_cost_breakdown_header')}")
            df_opex_breakdown = pd.DataFrame({
                get_text("financial_summary_category_label"): [get_text("energy_cost_line"), get_text("amortization_cost_line"), get_text("maintenance_cost_line"), get_text("software_cost_line"), get_text("insurance_cost_line"), get_text("land_cost_line")],
                "Valore Grezzo": [risultati_tab3['costo_operativo_energia_annuo'], risultati_tab3['costo_ammortamento_annuo'], costo_manutenzione_annuale_tab3, costo_software_annuale_tab3, costo_assicurazione_annuale_tab3, costo_terreno_annuale_tab3]
            })
            df_opex_breakdown[get_text("financial_summary_value_label")] = df_opex_breakdown["Valore Grezzo"].apply(lambda x: f"€{x:,.0f}")

            total_row = pd.DataFrame({get_text("financial_summary_category_label"): [get_text("total_opex_line")], get_text("financial_summary_value_label"): [f"€{risultati_tab3['costo_operativo_totale_annuo']:,.0f}"]})
            df_opex_breakdown = pd.concat([df_opex_breakdown.drop(columns="Valore Grezzo"), total_row], ignore_index=True)
            
            st.table(df_opex_breakdown)


        # RACCOMANDAZIONI
        with st.expander(get_text("optimization_recommendations"), expanded=True):
            if st.session_state.risultati_tab3:
                risultati_tab3 = st.session_state.risultati_tab3
                
                if risultati_tab3['profitto_netto_annuo'] <= 0:
                    st.error(get_text("negative_net_profit_warning"))
                
                if risultati_tab3['auto_non_servite'] > 0:
                    st.warning(get_text("cars_not_served_warning").format(count=risultati_tab3['auto_non_servite']))

                # Utilizzo Plug (migliore indicatore di saturazione)
                if risultati_tab3['tasso_utilizzo_plug'] > 90:
                    st.warning(get_text("highly_utilized_infra"))
                    st.markdown(get_text("add_more_chargers_rec"))
                elif risultati_tab3['tasso_utilizzo_plug'] < 50 and risultati_tab3['profitto_netto_annuo'] < 0:
                    st.info(get_text("underutilized_infra"))
                    st.markdown(get_text("reduce_chargers_rec"))
                    
                if not risultati_tab3['entro_budget']:
                    st.error(get_text("investment_over_budget"))
            else:
                st.info("Esegui l'analisi per visualizzare le raccomandazioni.")
