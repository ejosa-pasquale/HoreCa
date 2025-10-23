import streamlit as st
import pandas as pd
import plotly.express as px
from math import ceil, floor
from datetime import datetime, timedelta
from collections import defaultdict

# Page configuration
st.set_page_config(page_title="AI-JoSa", layout="wide", page_icon="⚡")

# --- Custom Streamlit Theming Suggestion (Cannot be directly applied by me) ---
# To set a global background color (e.g., green/blue shades), you would typically create a file:
# .streamlit/config.toml
# And add content like this:
# [theme]
# primaryColor="#4CAF50"  # A shade of green
# backgroundColor="#E0F2F7" # A light blue/green background
# secondaryBackgroundColor="#F0F8FF" # Another light shade
# textColor="#2E4053" # Darker text
# font="sans serif"

# Alternatively, you can inject CSS using st.markdown:
st.markdown("""
<style>
    .stApp {
        background-color: #E0F2F7; /* Light blue/green background */
        color: #2E4053; /* Darker text for contrast */
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px; /* Reduce gap between tabs */
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #A9D9D0; /* Light green for inactive tabs */
        border-radius: 5px 5px 0 0;
        margin-right: 2px;
        padding: 10px 15px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #6CBAB7; /* Darker green for active tab */
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1A5276; /* Dark blue for headers */
    }
    .stButton>button {
        background-color: #3498DB; /* Blue for buttons */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #2874A6;
    }
    .stSlider [data-testid="stTickBarMinMax"] {
        color: #1A5276; /* Dark blue for slider ticks */
    }
    .stSlider .stSlider-thumb {
        background-color: #3498DB; /* Blue for slider thumb */
    }
    .stSlider .stSlider-track {
        background-color: #6CBAB7; /* Green for slider track */
    }
    .stNumberInput {
        background-color: #F8F9FA;
        border-radius: 5px;
        padding: 5px;
    }
    .stMetric label {
        font-size: 1.1em;
        font-weight: bold;
        color: #1A5276;
    }
    .stMetric .stMetric-value {
        font-size: 2.2em;
        color: #2874A6;
    }
    .stMetric .stMetric-delta {
        color: #2ECC71; /* Green for positive delta */
    }
</style>
""", unsafe_allow_html=True)
# --- End of Custom Theming Suggestion ---

# --- Language Selection ---
# Dictionary for translations
translations = {
    "it": {
        "app_title": "⚡ AI-JoSa ⚡",
        "tab1_title": "🔌 Ottimizzatore Colonnine ⚙️",
        "tab2_title": "📊 Testa la Tua Infrastruttura Esistente",
        "tab3_title": "📈 Valuta Il Rendimento di un Punto di Ricarica",
        "optimizer_header": "🔌 Ottimizzatore Infrastruttura Colonnine",
        "optimizer_intro": "Questa sezione ti aiuta a trovare la configurazione ottimale di colonnine di ricarica per il tuo parco veicoli, tenendo conto del tuo budget e della potenza massima disponibile. L'algoritmo mira a massimizzare l'energia caricata internamente e l'efficienza complessiva.",
        "sidebar_config_params": "⚙️ Parametri di Configurazione",
        "sidebar_config_intro": "Definisci il budget e i costi per l'ottimizzazione dell'infrastruttura.",
        "economic_tech_params": "Parametri Economici e Tecnici",
        "budget_available": "Budget disponibile (€)",
        "budget_help": "Costo massimo totale per colonnine e installazione.",
        "max_power_kw": "Potenza Massima Totale Impianto (kW)",
        "max_power_help": "La potenza massima complessiva che l'impianto può supportare (es. limite fornitore).",
        "alpha_weight": "Peso efficienza temporale (α)",
        "alpha_help": "Bilancia l'importanza tra l'utilizzo delle colonnine (tempo) e l'energia erogata. 0=solo energia, 1=solo tempo.",
        "ac_turns": "Turnazioni giornaliere colonnine AC",
        "ac_turns_help": "Numero medio di veicoli che ogni colonnina AC può caricare in un giorno (considera tempi di ricarica e sosta).",
        "dc_turns": "Turnazioni giornaliere colonnine DC",
        "dc_turns_help": "Numero medio di veicoli che ogni colonnina DC può caricare in un giorno (considera tempi di ricarica più brevi).",
        "energy_costs": "Costi Energia",
        "private_charge_cost": "Costo kWh ricarica interna (€)",
        "private_charge_help": "Costo dell'energia elettrica per la ricarica in sede.",
        "public_charge_cost": "Costo kWh ricarica pubblica (€)",
        "public_charge_help": "Costo stimato dell'energia se i veicoli ricaricano presso stazioni pubbliche.",
        "gas_comparison_params": "Parametri di Confronto con Benzina",
        "gas_comparison_info": "Questi parametri servono per stimare il risparmio rispetto a un veicolo a benzina.",
        "gas_cost_km": "Costo benzina (€/km)",
        "gas_cost_help": "Costo medio per km di un veicolo a benzina.",
        "ev_consumption_eq": "Consumo equivalente EV (kWh/km)",
        "ev_consumption_help": "Consumo medio di energia per km per un veicolo elettrico.",
        "modify_charger_costs": "⚡ Modifica Costi Colonnine",
        "modify_charger_intro": "Puoi personalizzare i costi per ogni tipo di colonnina.",
        "unit_cost": "Costo unità (€)",
        "unit_cost_help": "Costo di acquisto per una singola colonnina {type}.",
        "installation_cost": "Costo installazione (€)",
        "installation_cost_help": "Costo stimato per l'installazione di una colonnina {type}.",
        "annual_maintenance_cost": "Costo manutenzione annuale (€)",
        "annual_maintenance_cost_help": "Costo di manutenzione annuale per una colonnina {type}.",
        "vehicle_config": "🚗 Configurazione Veicoli",
        "vehicle_config_intro": "Definisci il tuo parco veicoli. Puoi inserire singoli veicoli o gruppi con caratteristiche simili.",
        "input_mode": "Modalità inserimento veicoli",
        "single_vehicles": "Singoli veicoli",
        "vehicle_groups": "Gruppi di veicoli",
        "input_mode_help": "Scegli se inserire i veicoli uno per uno o raggrupparli per tipologia.",
        "num_single_vehicles": "Numero veicoli singoli",
        "num_single_vehicles_help": "Quanti veicoli singoli vuoi configurare?",
        "single_vehicle": "Veicolo singolo {i}",
        "vehicle_name": "Nome veicolo {i}",
        "daily_km": "Km giornalieri",
        "daily_km_help": "Chilometri percorsi in un giorno lavorativo.",
        "consumption_kwh_km": "Consumo (kWh/km)",
        "consumption_kwh_km_help": "Consumo medio di energia per chilometro.",
        "stop_start_time": "Ora inizio sosta (h)",
        "stop_start_time_help": "Ora di arrivo del veicolo (formato 24h).",
        "stop_end_time": "Ora fine sosta (h)",
        "stop_end_time_help": "Ora di partenza del veicolo (formato 24h).",
        "num_vehicle_groups": "Numero gruppi veicoli",
        "num_vehicle_groups_help": "Quanti gruppi di veicoli vuoi configurare?",
        "vehicle_group": "Gruppo veicoli {i}",
        "group_name": "Nome gruppo {i}",
        "group_quantity": "Quantità veicoli nel gruppo",
        "group_quantity_help": "Numero di veicoli in questo gruppo.",
        "group_daily_km": "Km giornalieri (per veicolo)",
        "group_daily_km_help": "Chilometri percorsi in un giorno per veicolo nel gruppo.",
        "group_consumption": "Consumo (kWh/km per veicolo)",
        "group_consumption_help": "Consumo medio di energia per chilometro per veicolo nel gruppo.",
        "group_stop_start": "Ora inizio sosta (h)",
        "group_stop_start_help": "Ora di arrivo dei veicoli del gruppo (formato 24h).",
        "group_stop_end": "Ora fine sosta (h)",
        "group_stop_end_help": "Ora di partenza dei veicoli del gruppo (formato 24h).",
        "calculate_optimization": "🔍 Calcola Ottimizzazione Infrastruttura",
        "add_vehicle_warning": "Per favore, aggiungi almeno un veicolo per avviare l'ottimizzazione.",
        "analysis_in_progress": "Analisi in corso, potrebbe richiedere alcuni secondi...",
        "no_solution_found": "❌ Nessuna soluzione trovata che rispetti il budget o la potenza massima specificata. Prova ad aumentare il budget o i parametri di sosta dei veicoli, o ridurre le potenze richieste.",
        "optimization_results": "📊 Risultati Ottimizzazione",
        "selected_solution": "✅ Soluzione Selezionata",
        "current_config_display": "Configurazione attualmente visualizzata:",
        "chargers_label": "Colonnine {type}",
        "total_chargers": "Totale Colonnine",
        "total_chargers_help": "Configurazione: {config_str}",
        "kpi_header": "Indicatori di Performance Chiave (KPI) - Selezionati",
        "total_initial_cost": "Costo Totale Iniziale",
        "budget_percentage": "{percent:.1f}% del budget",
        "internal_energy_charged": "Energia Caricata Internamente",
        "total_request_percentage": "{percent:.1f}% della richiesta totale",
        "estimated_annual_savings": "Risparmio Annuo Stimato",
        "vs_public_charges": "rispetto a ricariche pubbliche",
        "combined_efficiency": "Efficienza Combinata (Tempo & Energia)",
        "combined_efficiency_help": "Temporale: {temp_eff:.1f}% | Energetica: {energy_eff:.1f}%",
        "estimated_external_charge_cost": "Costo Ricarica Esterna Stimato (Giornaliero) - Selezionato",
        "avg_daily_external_cost": "Costo Medio Giornaliero per Energia Esterna",
        "external_cost_help": "Questa è l'energia che i veicoli non hanno potuto caricare presso la tua infrastruttura e dovranno ottenere esternamente al costo di €{cost:.2f}/kWh.",
        "partial_charge_warning": "⚠️ **Attenzione:** Questa configurazione non riesce a caricare completamente tutti i veicoli internamente. Energia da caricare esternamente: {energy:.1f} kWh.",
        "full_charge_success": "✅ Tutti i veicoli possono essere caricati completamente con questa configurazione.",
        "detailed_planning_tab": "Pianificazione Dettagliata",
        "vehicle_summary_tab": "Riepilogo Veicoli",
        "all_configs_tab": "Tutte le Configurazioni",
        "detailed_optimization_analysis_tab": "Analisi Dettagliata Ottimizzazione",
        "gantt_intro": "Visualizza la pianificazione delle ricariche su ciascuna colonnina. Ogni barra rappresenta una sessione di ricarica.",
        "gantt_warning": "⚠️ **Attenzione:** La visualizzazione Gantt potrebbe diventare meno leggibile con un numero elevato di veicoli o ricariche. Per un'analisi dettagliata, fare riferimento alla tabella 'Dettaglio Ricariche'.",
        "charge_details": "📅 Dettaglio Ricariche",
        "no_actual_charges": "Nessuna ricarica effettiva è stata pianificata per le colonnine.",
        "no_chargers_configured": "Nessuna colonnina configurata o nessuna ricarica pianificata.",
        "vehicle_charge_summary": "🚗 Riepilogo Stato Ricarica Veicoli",
        "vehicle_charge_summary_intro": "Questa tabella riassume l'energia richiesta e quella caricata internamente per ogni veicolo o gruppo di veicoli.",
        "type_col": "Tipo",
        "name_col": "Nome",
        "energy_req_col": "Energia Richiesta (kWh)",
        "internal_energy_col": "Energia Interna (kWh)",
        "external_energy_col": "Energia Esterna (kWh)",
        "charge_status_col": "Stato Ricarica",
        "coverage_detail_col": "Dettaglio Copertura",
        "complete_status": "✅ Completo",
        "partial_status": "⚠️ Parziale",
        "complete_count": "{charged}/{total} completi",
        "charge_count": "{count} ricariche",
        "no_charge": "Nessuna ricarica",
        "all_tested_configs": "⚙️ Tutte le configurazioni testate",
        "configs_evaluated": "Configurazioni valutate: **{count}**",
        "configs_order_info": "Le configurazioni sono ordinate per: 1) % Energia Interna (max) 2) Potenza Impegnata (min) 3) Costo Totale (min) 4) Efficienza Combinata (max) 5) Numero Colonnine (min).",
        "cost_analysis_selected_solution": "📈 Analisi Costi della Soluzione Selezionata",
        "charger_cost_pie": "Costo Colonnine",
        "installation_cost_pie": "Costo Installazione",
        "maintenance_cost_pie": "Costo Manutenzione (10 anni)",
        "cost_distribution_title": "Distribuzione Costi Iniziali e Manutenzione (Configurazione Selezionata)",
        "no_config_to_analyze": "Nessuna configurazione da analizzare per i costi.",
        "detailed_optimization_analysis": "Analisi Dettagliata Ottimizzazione",
        "detailed_opt_intro": "Questa sezione fornisce ulteriori grafici per comprendere meglio i risultati dell'ottimizzazione.",
        "energy_charged_by_type": "Energia Caricata per Tipo di Colonnina",
        "no_energy_charged": "Nessuna energia caricata dalle colonnine in questa configurazione.",
        "vehicle_charge_status": "Stato di Ricarica dei Veicoli",
        "fully_charged": "Completamente Caricati",
        "partially_charged": "Parzialmente Caricati",
        "not_charged": "Non Caricati",
        "charge_status_distribution": "Distribuzione dello Stato di Ricarica dei Veicoli",
        "energy_req_vs_charged_top10": "Energia Richiesta vs. Caricata per Veicolo (Top 10)",
        "no_vehicle_data_for_chart": "Nessun dato sui veicoli per questo grafico.",
        "detailed_partial_charge_explanation": "Spiegazione Dettagliata per un Veicolo Specifico (Ricarica Parziale)",
        "partial_charge_intro": "Se un veicolo non è stato caricato completamente, questa sezione ti aiuta a capire il perché.",
        "analysis_for_partial_vehicle": "Analisi per il veicolo parzialmente caricato: **{name}**",
        "analysis_for_unassigned_vehicle": "Analisi per il veicolo non caricato: **{name}**",
        "all_vehicles_fully_charged": "Tutti i veicoli sono stati caricati completamente in questa configurazione. Non è necessaria una spiegazione per ricariche parziali.",
        "vehicle_needs_energy_time": "Il veicolo **{name}** necessita di **{energy:.1f} kWh** e ha un tempo di sosta disponibile di **{time:.1f} ore**.",
        "vehicle_charged_for": "È stato caricato per **{energy:.1f} kWh**.",
        "reasons_for_partial_charge": "##### Motivi della Ricarica Parziale/Non Completa:",
        "insufficient_stop_time": "- **Tempo di sosta insufficiente:** Anche con la colonnina più potente ({max_power} kW), il veicolo avrebbe richiesto più di {available_time:.1f} ore per caricare {energy_needed:.1f} kWh. Tempo minimo richiesto: {min_time_needed:.1f} ore.",
        "no_charger_available": "- **Nessuna colonnina disponibile:** Non è stato trovato uno slot libero su nessuna colonnina durante il periodo di sosta del veicolo.",
        "charger_not_powerful_enough": "- **Colonnina assegnata non sufficientemente potente:** La colonnina assegnata ({assigned_power} kW) non era abbastanza potente da fornire {energy_needed:.1f} kWh in {available_time:.1f} ore. Avrebbe richiesto {time_needed_on_assigned:.1f} ore.",
        "scheduling_conflicts": "- **Conflitti di pianificazione/slot non disponibili:** Sebbene la colonnina assegnata fosse teoricamente in grado di caricare completamente il veicolo, non sono stati trovati slot continui o sufficientemente lunghi a causa di altre prenotazioni o intervalli minimi tra le ricariche.",
        "assignment_logic": "- **Logica di assegnazione:** Il sistema ha scelto di assegnare una ricarica parziale per ottimizzare l'utilizzo delle colonnine o per servire più veicoli, dato che una ricarica completa non era la priorità assoluta o non era possibile con le risorse disponibili in quel momento.",
        "to_ensure_full_charge": "Per garantire una ricarica completa, si potrebbe:",
        "increase_stop_time": "- Aumentare il tempo di sosta disponibile per il veicolo.",
        "add_more_powerful_chargers": "- Aggiungere colonnine con maggiore potenza.",
        "optimize_scheduling": "- Ottimizzare ulteriormente la pianificazione per ridurre i tempi morti.",
        "vehicle_fully_charged": "Il veicolo è stato caricato completamente.",
        "no_optimization_results": "Nessun risultato di ottimizzazione disponibile per la visualizzazione dettagliata del veicolo. Esegui prima l'ottimizzazione.",
        "configure_and_calculate": "Configura i parametri e i veicoli nella sidebar, poi clicca su 'Calcola Ottimizzazione Infrastruttura'.",
        "infrastructure_test_header": "📊 Testa la Tua Infrastruttura Esistente",
        "infrastructure_test_intro": "Questa sezione ti permette di simulare le performance della tua infrastruttura di ricarica attuale rispetto alle esigenze del tuo parco auto. Scopri quanta energia puoi erogare internamente e quali costi potresti affrontare per le ricariche esterne.",
        "test_params_vehicle_fleet": "Parametri Parco Auto",
        "num_ev_vehicles": "Numero veicoli elettrici",
        "num_ev_vehicles_help": "Quanti veicoli elettrici hai nel tuo parco?",
        "single_vehicle_test": "Veicolo {i}",
        "daily_km_test": "Km giornalieri",
        "daily_km_test_help": "Distanza media percorsa al giorno.",
        "avg_consumption_test": "Consumo medio (kWh/100km)",
        "avg_consumption_test_help": "Consumo di energia per 100 km.",
        "available_stop_hours_test": "Ore di sosta disponibili (per ricarica)",
        "available_stop_hours_test_help": "Ore in cui il veicolo è disponibile per la ricarica in sede.",
        "existing_infra_config": "Configurazione Infrastruttura di Ricarica Esistente",
        "existing_infra_intro": "Inserisci il numero di colonnine di ciascun tipo che possiedi.",
        "ac_11_chargers": "Colonnine AC_11 (11 kW)",
        "ac_11_chargers_help": "Numero di colonnine in Corrente Alternata da 11 kW.",
        "ac_22_chargers": "Colonnine AC_22 (22 kW)",
        "ac_22_chargers_help": "Numero di colonnine in Corrente Alternata da 22 kW.",
        "dc_30_chargers": "Colonnine DC_30 (30 kW)",
        "dc_30_chargers_help": "Numero di colonnine in Corrente Continua da 30 kW.",
        "dc_60_chargers": "Colonnine DC_60 (60 kW)",
        "dc_60_chargers_help": "Numero di colonnine in Corrente Continua da 60 kW.",
        "dc_90_chargers": "Colonnine DC_90 (90 kW)",
        "dc_90_chargers_help": "Numero di colonnine in Corrente Continua da 90 kW.",
        "daily_charger_hours": "Ore giornaliere disponibili per la ricarica (colonnine)",
        "daily_charger_hours_help": "Ore al giorno in cui le colonnine sono operative e accessibili.",
        "economic_investment_params": "Parametri Economici e Investimento",
        "economic_investment_intro": "Definisci i costi dell'energia e l'investimento iniziale.",
        "internal_energy_cost_test": "Costo energia interna (€/kWh)",
        "internal_energy_cost_test_help": "Costo dell'energia (approvvigionamento) per kWh quando ricarichi presso la tua infrastruttura.",
        "external_energy_price_test": "Prezzo energia esterna (€/kWh)",
        "external_energy_price_test_help": "Costo per kWh se i veicoli ricaricano all'esterno.",
        "charger_purchase_costs": "Costi di acquisto/installazione per tipo di colonnina (stima)",
        "investment_ac11": "Investimento AC_11 (€)",
        "investment_ac11_help": "Costo stimato per l'acquisto e l'installazione di una colonnina AC 11kW.",
        "investment_ac22": "Investimento AC_22 (€)",
        "investment_ac22_help": "Costo stimato per l'acquisto e l'installazione di una colonnina AC 22kW.",
        "investment_dc30": "Investimento DC_30 (€)",
        "investment_dc30_help": "Costo stimato per l'acquisto e l'installazione di una colonnina DC 30kW.",
        "investment_dc60": "Investimento DC_60 (€)",
        "investment_dc60_help": "Costo stimato per l'acquisto e l'installazione di una colonnina DC 60kW.",
        "investment_dc90": "Investimento DC_90 (€)",
        "investment_dc90_help": "Costo stimato per l'acquisto e l'installazione di una colonnina DC 90kW.",
        "run_infra_analysis": "🔄 Esegui Analisi Infrastruttura",
        "add_vehicle_warning_analysis": "Per favor, aggiungi almeno un veicolo per eseguire l'analisi.",
        "analysis_execution": "Esecuzione analisi...",
        "analysis_complete_success": "Analisi completata con successo!",
        "performance_summary": "Riepilogo Performance",
        "total_energy_requested": "Energia totale richiesta",
        "total_energy_requested_help": "L'energia complessiva che tutti i veicoli del parco auto necessitano giornalmente.",
        "internal_energy_charged_test": "Energia caricata internamente",
        "internal_energy_charged_test_help": "L'energia che è stata effettivamente caricata dalla tua infrastruttura.",
        "external_energy_to_charge": "Energia da caricare esternamente",
        "external_energy_to_charge_help": "L'energia che i veicoli dovranno ottenere da stazioni di ricarica pubbliche.",
        "estimated_time_lost": "Tempo stimato perso (ricariche esterne)",
        "estimated_time_lost_help": "Stima del tempo che i veicoli impiegheranno per ricaricare esternamente (include tempi di spostamento e attesa).",
        "daily_external_charge_cost": "Costo giornaliero ricariche esterne",
        "daily_external_charge_cost_help": "Costo economico stimato per le ricariche effettuate al di fuori della tua infrastruttura.",
        "avg_charger_utilization_rate": "Tasso di utilizzo medio colonnine",
        "avg_charger_utilization_rate_help": "Percentuale di tempo in cui le colonnine sono effettivamente utilizzate per la ricarica.",
        "fully_charged_cars": "Auto Caricate Completamente",
        "fully_charged_cars_help": "Numero di veicoli che hanno completato la loro ricarica richiesta tramite la tua infrastruttura.",
        "internal_operating_cost": "Costo Operativo Interno",
        "internal_operating_cost_help": "Costo giornaliero per l'energia erogata tramite la tua infrastruttura.",
        "estimated_annual_savings_test": "Risparmio Annuo Stimato",
        "estimated_annual_savings_test_help": "Il risparmio annuo stimato derivante dalla ricarica interna rispetto alla ricarica esterna.",
        "roi_test": "ROI (Return on Investment)",
        "roi_test_help": "Il ritorno sull'investimento, calcolato come rapporto tra risparmio annuo e costo totale di investimento iniziale.",
        "charger_utilization_details": "Dettaglio Utilizzo Colonnine",
        "vehicle_charge_status_test": "Stato Ricarica Veicoli",
        "energy_req_vs_charged_test": "Energia Richiesta vs Caricata",
        "operating_costs_analysis_test": "Analisi Costi Operativi",
        "hourly_utilization_details": "Visualizza l'utilizzo orario per ciascun tipo di colonnina configurata.",
        "hourly_utilization_chart_title": "Ore di Utilizzo per Tipo di Colonnina",
        "no_chargers_configured_analysis": "Nessuna colonnina configurata per l'analisi.",
        "gantt_planning_details": "Pianificazione Dettaglio Ricariche (Gantt Chart)",
        "gantt_planning_intro": "Questa è una visualizzazione semplificata delle prenotazioni delle colonnine.",
        "no_charges_recorded": "Nessuna ricarica registrata per la configurazione attuale. Prova a modificare i parametri.",
        "vehicle_charge_status_chart_title": "Distribuzione dello Stato di Ricarica dei Veicoli",
        "run_analysis_to_view_status": "Esegui l'analisi per visualizzare lo stato di ricarica dei veicoli.",
        "energy_comparison_chart_title": "Confronto Energia Richiesta e Caricata per Veicolo",
        "run_analysis_to_view_comparison": "Esegui l'analisi per visualizzare il confronto energia richiesta vs. caricata.",
        "operating_costs_analysis_chart_title": "Analisi Costi Operativi (Interni vs Esterni)",
        "operating_costs_distribution_chart_title": "Distribuzione Costi Operativi Giornalieri",
        "run_analysis_to_view_costs": "Esegui l'analisi per visualizzare l'analisi dei costi operativi.",
        "optimization_suggestions": "Suggerimenti di ottimizzazione",
        "improvement_opportunity": "🔄 **Opportunità di Miglioramento:** Una parte significativa dell'energia richiesta (circa {energy:.1f} kWh) deve essere caricata esternamente. Considera di aggiungere colonnine o aumentare la potenza di quelle esistenti per ridurre questa dipendenza.",
        "fleet_coverage": "🚗 **Copertura del Parco Auto:** Solo {charged} su {total} veicoli sono stati caricati completamente. Valuta se la tua infrastruttura è sufficiente per l'intero parco o se alcuni veicoli hanno tempi di sosta troppo brevi per le colonnine disponibili.",
        "high_utilization_warning": "⚠️ **Attenzione:** Le colonnine sono ben utilizzate, con un tasso medio del {utilization:.1f}%. Se prevedi una crescita del parco auto, potrebbe essere il momento di espandere l'infrastruttura per evitare colli di bottiglia.",
        "low_utilization_info": "ℹ️ **Valuta l'Efficienza:** Il tasso di utilizzo delle colonnine è del {utilization:.1f}%, indicando una possibile sottoutilizzazione. Potresti considerare di ridurre il numero di colonnine, attrarre più veicoli, o esplorare modelli di business aggiuntivi (es. ricarica pubblica) per massimizzare il ritorno sull'investimento.",
        "well_balanced_utilization": "✅ **Ben Bilanciato:** L'utilizzo delle colonnine è ben bilanciato per il tuo attuale parco auto.",
        "good_roi_success": "💰 **Ottimo Ritorno sull'Investimento:** Con un ROI del {roi:.1f}% annuo, l'investimento nella tua infrastruttura di ricarica si sta dimostrando molto vantaggioso. Considera ulteriori espansioni!",
        "positive_roi_info": "📈 **Investimento Profittevole:** Il tuo investimento sta generando un ROI positivo del {roi:.1f}%. Monitora l'andamento e considera come ottimizzare ulteriormente.",
        "negative_roi_error": "📉 **Rivedi l'Investimento:** Attualmente, il ROI è negativo ({roi:.1f}%). È fondamentale analizzare i costi e i benefici per capire come migliorare la redditività dell'infrastruttura. Potresti aver bisogno di più veicoli, ottimizzare l'uso delle colonnine, o rinegoziare i costi dell'energia.",
        "roi_not_calculable": "ℹ️ **ROI non calcolabile:** Non è stato specificato un investimento iniziale per le colonnine, quindi il ROI non è calcolabile. Inserisci i costi di investimento per una valutazione completa.",
        "run_analysis_to_view_suggestions": "Esegui l'analisi per visualizzare i suggerimenti di ottimizzazione.",
        "performance_eval_header": "📈 Valutazione Rendimento di un Punto di Ricarica",
        "performance_eval_intro": "Questa sezione ti aiuta a stimare il potenziale guadagno e il ritorno sull'investimento (ROI) di un punto di ricarica basandosi sul numero di auto previste, i costi e i prezzi di vendita dell'energia.",
        "charging_point_usage_params": "Parametri di Utilizzo del Punto di Ricarica",
        "base_usage_params": "Parametri Base di Utilizzo",
        "expected_daily_cars": "Auto previste in ricarica al giorno",
        "expected_daily_cars_help": "Numero medio di veicoli che si prevede ricarichino ogni giorno.",
        "avg_energy_per_car": "Energia media richiesta per auto (kWh)",
        "avg_energy_per_car_help": "Energia media che ciascun veicolo richiede per una ricarica.",
        "avg_charge_time": "Tempo medio di ricarica per auto (ore)",
        "avg_charge_time_help": "Tempo medio di permanenza per una ricarica (non direttamente usato nel calcolo ma utile per contesto).",
        "operational_time_config": "Configurazione Temporale Operativa",
        "daily_op_hours": "Ore operative al giorno",
        "daily_op_hours_help": "Ore al giorno in cui il punto di ricarica è disponibile.",
        "annual_op_days": "Giorni operativi all'anno",
        "annual_op_days_help": "Numero di giorni all'anno in cui il punto di ricarica è attivo.",
        "economic_utilization_params": "Parametri Economici e di Utilizzo",
        "energy_sale_price": "Prezzo di vendita energia (€/kWh)",
        "energy_sale_price_help": "Il prezzo al quale l'energia viene venduta ai clienti.",
        "energy_purchase_cost": "Costo acquisto energia (€/kWh)",
        "energy_purchase_cost_help": "Il costo al quale acquisti l'energia per le colonnine.",
        "infra_utilization_prob": "Probabilità di utilizzo dell'infrastruttura (%)",
        "infra_utilization_prob_help": "Percentuale del tempo in cui le colonnine sono effettivamente occupate, dato dalla domanda e dalla disponibilità.",
        "max_initial_investment": "Investimento Iniziale Massima (€)",
        "max_initial_investment_help": "Budget massimo per l'acquisto e l'installazione delle colonnine.",
        "additional_annual_op_costs": "Costi Operativi Aggiuntivi (Annuali)",
        "annual_charger_maintenance_cost": "Costo Manutenzione Annuale Colonnine (€)",
        "annual_charger_maintenance_cost_help": "Costo annuale stimato per la manutenzione di tutte le colonnine.",
        "annual_software_cost": "Costo Software/Gestione Annuale (€)",
        "annual_software_cost_help": "Costo annuale per software di gestione, connettività, ecc.",
        "annual_insurance_cost": "Costo Assicurazione Annuale (€)",
        "annual_insurance_cost_help": "Costo annuale dell'assicurazione per l'infrastruttura.",
        "annual_land_cost": "Costo Affitto/Uso Terreno Annuale (€)",
        "annual_land_cost_help": "Costo annuale per l'affitto o l'uso del terreno (se applicabile).",
        "useful_life_years": "Vita Utile Impianto (anni)",
        "useful_life_years_help": "Anni di vita utile stimata dell'impianto per il calcolo dell'ammortamento.",
        "charger_point_config": "Configurazione delle Colonnine per il Punto di Ricarica",
        "select_quantify_chargers": "Seleziona e Quantifica le Colonnine",
        "ac22_chargers_eval": "AC_22 (22 kW)",
        "ac22_chargers_eval_help": "Numero di colonnine AC da 22 kW.",
        "dc20_chargers_eval": "DC_20 (20 kW)",
        "dc20_chargers_eval_help": "Numero di colonnine DC da 20 kW.",
        "dc30_chargers_eval": "DC_30 (30 kW)",
        "dc30_chargers_eval_help": "Numero di colonnine DC da 30 kW.",
        "dc40_chargers_eval": "DC_40 (40 kW)",
        "dc40_chargers_eval_help": "Numero di colonnine DC da 40 kW.",
        "dc60_chargers_eval": "DC_60 (60 kW)",
        "dc60_chargers_eval_help": "Numero di colonnine DC da 60 kW.",
        "dc90_chargers_eval": "DC_90 (90 kW)",
        "dc90_chargers_eval_help": "Numero di colonnine DC da 90 kW.",
        "calculate_point_performance": "📊 Calcola Rendimento Punto di Ricarica",
        "calculate_performance_spinner": "Calcolo rendimento...",
        "performance_analysis_complete": "Analisi di rendimento completata!",
        "charging_point_summary": "Riepilogo del Punto di Ricarica",
        "total_installed_power": "Potenza totale installata",
        "total_installed_power_help": "La somma delle potenze di tutte le colonnine installate.",
        "estimated_annual_energy_delivered": "Energia erogata annuale stimata",
        "estimated_annual_energy_delivered_help": "La quantità totale di energia che si prevede sarà erogata dal punto di ricarica in un anno.",
        "daily_cars_served": "Auto servite giornaliere",
        "daily_cars_served_help": "Il numero di auto che si prevede saranno servite completamente ogni giorno.",
        "key_economic_indicators": "Indicatori Economici Chiave",
        "estimated_annual_revenue": "Ricavo annuo stimato",
        "estimated_annual_revenue_help": "Il ricavo lordo annuale basato sull'energia erogata e il prezzo di vendita.",
        "total_system_cost_capex": "Costo totale impianto (CAPEX)",
        "within_budget": "Entro budget",
        "over_budget": "Sopra budget",
        "total_system_cost_capex_help": "The total cost for purchasing and installing chargers (Capital Expenditure).",
        "annual_operating_cost_opex": "Annual Operating Cost (OPEX)",
        "annual_operating_cost_opex_help": "The total annual management cost, including energy, maintenance, software, etc.",
        "detailed_financial_analysis": "Detailed Financial Analysis",
        "estimated_annual_net_profit": "Estimated Annual Net Profit",
        "estimated_annual_net_profit_help": "The net annual profit after deducting all operating costs and depreciation.",
        "payback_period": "Payback Period",
        "payback_period_help": "The estimated time required to recover the initial investment through net revenues generated.",
        "infinite_payback": "Infinite",
        "detailed_visualization_tab": "Visualizzazione Dettagliata",
        "financial_summary_tab": "Riepilogo Finanziario",
        "payback_trend_tab": "Andamento Payback",
        "investment_distribution_tab": "Distribuzione Investimento",
        "cars_served_vs_not_served": "Distribuzione Auto Servite vs Non Servite",
        "served_cars": "Auto servite",
        "not_served_cars": "Auto non servite",
        "estimated_monthly_energy_delivered": "Energia Erogata Mensile Stimata (con stagionalità)",
        "annual_financial_summary": "Riepilogo Finanziario Annuale (Ricavi vs Costi)",
        "revenue": "Ricavo",
        "cost": "Costo",
        "profit": "Profitto",
        "cumulative_net_profit_trend": "Andamento del Profitto Netto Cumulativo e Payback Period",
        "cumulative_net_profit": "Profitto Netto Cumulativo (€)",
        "initial_investment": "Investimento Iniziale (€)",
        "payback_line": "Payback: {years:.1f} anni",
        "payback_not_calculable": "Il periodo di payback non è calcolabile o il profitto netto è negativo. Non è possibile generare il grafico.",
        "initial_investment_cost_distribution": "Distribuzione Costi di Investimento Iniziale",
        "charger_cost_component": "Costo Colonnine",
        "installation_cost_component": "Costo Installazione",
        "run_analysis_to_view_investment": "Esegui l'analisi per visualizzare la distribuzione dei costi di investimento.",
        "optimization_recommendations": "Raccomandazioni per l'Ottimizzazione",
        "highly_utilized_infra": "⚠️ **L'infrastruttura è altamente utilizzata.** Per massimizzare i ricavi e la soddisfazione dei clienti, considera:",
        "add_more_chargers_rec": "- **Aggiungere più colonnine:** Se la domanda supera l'offerta.",
        "increase_installed_power_rec": "- **Aumentare la potenza installata:** Per ricariche più rapide, se possibile.",
        "extend_op_hours_rec": "- **Estendere le ore operative:** Per coprire una fascia oraria più ampia.",
        "underutilized_infra": "ℹ️ **L'infrastruttura è sottoutilizzata.** Per migliorare il rendimento, potresti:",
        "reduce_chargers_rec": "- **Ridurre il numero di colonnine:** Se il costo supera il beneficio.",
        "attract_more_customers_rec": "- **Cercare di attrarre più clienti:** Attraverso marketing o partnership.",
        "offer_promo_rates_rec": "- **Offrire tariffe promozionali:** Per incentivare l'utilizzo fuori orario di punta.",
        "investment_over_budget": "❌ **L'investimento supera il budget.** Per rientrare nei limiti, valuta:",
        "review_charger_mix_rec": "- **Rivedere il mix di colonnine:** Preferendo colonnine AC a minor costo rispetto a quelle DC ad alta potenza.",
        "phase_investment_rec": "- **Frazionare l'investimento:** Pianificando l'installazione in più fasi.",
        "seek_funding_rec": "- **Cercare finanziamenti o incentivi:** Per coprire parte dei costi.",
        "cars_not_served_warning": "🔌 **{count} auto al giorno non possono essere servite.** Questo comporta una perdita di potenziale ricavo e insoddisfazione. Considera:",
        "increase_charger_power_rec": "- **Aumentare la potenza delle colonnine:** Per ridurre i tempi di ricarica e servire più veicoli.",
        "optimize_charge_times_rec": "- **Ottimizzare i tempi di ricarica:** Educando gli utenti o implementando politiche di sosta massima.",
        "implement_booking_system_rec": "- **Implementare un sistema di prenotazione:** Per gestire meglio il flusso e ridurre i tempi morti.",
        "negative_net_profit_warning": "📉 **Attenzione: Profitto Netto Negativo!** Il tuo punto di ricarica non sembra essere redditizio con i parametri attuali. Considera di:",
        "increase_sale_price_rec": "- **Aumentare il prezzo di vendita dell'energia.**",
        "reduce_op_costs_rec": "- **Ridurre i costi operativi:** Negoziando prezzi migliori per l'energia o la manutenzione.",
        "increase_utilization_rec": "- **Aumentare il tasso di utilizzo:** Attrarre più clienti o estendere le ore operative.",
        "review_initial_investment_rec": "- **Rivedere l'investimento iniziale:** Se è troppo elevato per i ricavi attesi.",
        "run_analysis_to_view_recommendations": "Esegui l'analisi per visualizzare le raccomandazioni per l'ottimizzazione.",
        "configure_and_calculate_point": "Configura i parametri del punto di ricarica e le colonnine, poi clicca su 'Calcola Rendimento Punto di Ricarica'.",
        "footer_text": "Suite AI-Josa by EV Field Service - Strumenti completi per la pianificazione e ottimizzazione di infrastrutture di ricarica per veicoli elettrici",
        "colonnina_label": "Colonnina",
        "vehicle_label": "Veicolo",
        "start_time_label": "Ora Inizio",
        "end_time_label": "Ora Fine",
        "charge_time_label": "Tempo Ricarica",
        "energy_kwh_label": "Energia (kWh)",
        "charger_type_label": "Tipo Colonnina",
        "hours_used_label": "Ore utilizzate",
        "category_label": "Categoria",
        "value_label": "Valore",
        "month_label": "Mese",
        "component_label": "Componente",
        "cost_label": "Costo (€)",
        "year_label": "Anno",
        "cumulative_net_profit_label": "Profitto Netto Cumulativo (€)",
        "initial_investment_label": "Investimento Iniziale (€)",
        "financial_summary_category_label": "Categoria",
        "financial_summary_value_label": "Valore (€)",
        "financial_summary_type_label": "Tipo",
        "revenue_label": "Ricavo",
        "cost_label_short": "Costo",
        "profit_label_short": "Profitto",
        "power": "Potenza",
        "kw": "kW",
        "cost_unit": "Costo Unità",
        "euro": "€",
        "charger_type": "Tipo colonnina",
        "hour_of_day": "Ora del Giorno",
        "charger": "Colonnina",
        "no_charge_gantt": "Nessuna ricarica",
        "gantt_chart_title": "Pianificazione Ricariche",
        "day_label": "giorno",
        "single_label": "Singolo",
        "group_label": "Gruppo",
        "num_vehicles_label": "Numero Veicoli",
        "config_label": "Configurazione",
        "total_initial_cost_label": "Costo Iniziale Totale", # New translation key for consistency
        "budget_utilization_label": "Utilizzo Budget",
        "vehicles_served_percentage": "% Veicoli Serviti",
        "num_chargers_label": "Num. Colonnine",
        "temporal_efficiency_label": "Efficienza Temporale",
        "energy_efficiency_label": "Efficienza Energetica",
        "combined_efficiency_label": "Efficienza Combinata",
        "daily_external_cost_label": "Costo Esterno Giornaliero",
        "years_label": "anni",
        "total_installed_power_label": "Potenza Totale Installata (kW)" # New translation key
    },
    "en": {
        "app_title": "⚡ Ai-JoSa ⚡",
        "tab1_title": "🔌 Charging Station Optimizer ⚙️",
        "tab2_title": "📊 Test Your Existing Infrastructure",
        "tab3_title": "📈 Evaluate Charging Point Performance",
        "optimizer_header": "🔌 Charging Station Infrastructure Optimizer",
        "optimizer_intro": "This section helps you find the optimal charging station configuration for your vehicle fleet, considering your budget and maximum available power. The algorithm aims to maximize internally charged energy and overall efficiency.",
        "sidebar_config_params": "⚙️ Configuration Parameters",
        "sidebar_config_intro": "Define the budget and costs for infrastructure optimization.",
        "economic_tech_params": "Economic and Technical Parameters",
        "budget_available": "Available Budget (€)",
        "budget_help": "Maximum total cost for charging stations and installation.",
        "max_power_kw": "Maximum Total System Power (kW)",
        "max_power_help": "The overall maximum power the system can support (e.g., supplier limit).",
        "alpha_weight": "Temporal efficiency weight (α)",
        "alpha_help": "Balances the importance between charger utilization (time) and energy delivered. 0=energy only, 1=time only.",
        "ac_turns": "Daily AC charger turns",
        "ac_turns_help": "Average number of vehicles each AC charger can charge in a day (considers charging and parking times).",
        "dc_turns": "Daily DC charger turns",
        "dc_turns_help": "Average number of vehicles each DC charger can charge in a day (considers shorter charging times).",
        "energy_costs": "Energy Costs",
        "private_charge_cost": "Internal kWh charging cost (€)",
        "private_charge_help": "Cost of electricity for on-site charging.",
        "public_charge_cost": "Public kWh charging cost (€)",
        "public_charge_help": "Estimated cost of energy if vehicles charge at public stations.",
        "gas_comparison_params": "Gasoline Comparison Parameters",
        "gas_comparison_info": "These parameters are used to estimate savings compared to a gasoline vehicle.",
        "gas_cost_km": "Gasoline cost (€/km)",
        "gas_cost_help": "Average cost per km for a gasoline vehicle.",
        "ev_consumption_eq": "EV equivalent consumption (kWh/km)",
        "ev_consumption_help": "Average energy consumption per km for an electric vehicle.",
        "modify_charger_costs": "⚡ Modify Charger Costs",
        "modify_charger_intro": "You can customize the costs for each charger type.",
        "unit_cost": "Unit Cost (€)",
        "unit_cost_help": "Purchase cost for a single {type} charger.",
        "installation_cost": "Installation Cost (€)",
        "installation_cost_help": "Estimated cost for installing a {type} charger.",
        "annual_maintenance_cost": "Annual Maintenance Cost (€)",
        "annual_maintenance_cost_help": "Annual maintenance cost for a {type} charger.",
        "vehicle_config": "🚗 Vehicle Configuration",
        "vehicle_config_intro": "Define your vehicle fleet. You can enter individual vehicles or groups with similar characteristics.",
        "input_mode": "Vehicle input mode",
        "single_vehicles": "Single vehicles",
        "vehicle_groups": "Vehicle groups",
        "input_mode_help": "Choose whether to enter vehicles one by one or group them by type.",
        "num_single_vehicles": "Number of single vehicles",
        "num_single_vehicles_help": "How many single vehicles do you want to configure?",
        "single_vehicle": "Single vehicle {i}",
        "vehicle_name": "Vehicle name {i}",
        "daily_km": "Daily km",
        "daily_km_help": "Kilometers traveled on a working day.",
        "consumption_kwh_km": "Consumption (kWh/km)",
        "consumption_kwh_km_help": "Average energy consumption per kilometer.",
        "stop_start_time": "Stop start time (h)",
        "stop_start_time_help": "Vehicle arrival time (24h format).",
        "stop_end_time": "Stop end time (h)",
        "stop_end_time_help": "Vehicle departure time (24h format).",
        "num_vehicle_groups": "Number of vehicle groups",
        "num_vehicle_groups_help": "How many vehicle groups do you want to configure?",
        "vehicle_group": "Vehicle group {i}",
        "group_name": "Group name {i}",
        "group_quantity": "Quantity of vehicles in group",
        "group_quantity_help": "Number of vehicles in this group.",
        "group_daily_km": "Daily km (per vehicle)",
        "group_daily_km_help": "Kilometers traveled per day per vehicle in the group.",
        "group_consumption": "Consumption (kWh/km per vehicle)",
        "group_consumption_help": "Average energy consumption per kilometer per vehicle in the group.",
        "group_stop_start": "Stop start time (h)",
        "group_stop_start_help": "Arrival time of vehicles in the group (24h format).",
        "group_stop_end": "Stop end time (h)",
        "group_stop_end_help": "Departure time of vehicles in the group (24h format).",
        "calculate_optimization": "🔍 Calculate Infrastructure Optimization",
        "add_vehicle_warning": "Please add at least one vehicle to start the optimization.",
        "analysis_in_progress": "Analysis in progress, this may take a few seconds...",
        "no_solution_found": "❌ No solution found that respects the budget or maximum power specified. Try increasing the budget or vehicle stop parameters, or reducing the required power.",
        "optimization_results": "📊 Optimization Results",
        "selected_solution": "✅ Selected Solution",
        "current_config_display": "Currently displayed configuration:",
        "chargers_label": "Chargers {type}",
        "total_chargers": "Total Chargers",
        "total_chargers_help": "Configuration: {config_str}",
        "kpi_header": "Key Performance Indicators (KPIs) - Selected",
        "total_initial_cost": "Total Initial Cost",
        "budget_percentage": "{percent:.1f}% of budget",
        "internal_energy_charged": "Internal Energy Charged",
        "total_request_percentage": "{percent:.1f}% of total request",
        "estimated_annual_savings": "Estimated Annual Savings",
        "vs_public_charges": "vs. public charges",
        "combined_efficiency": "Combined Efficiency (Time & Energy)",
        "combined_efficiency_help": "Temporal: {temp_eff:.1f}% | Energy: {energy_eff:.1f}%",
        "estimated_external_charge_cost": "Estimated External Charging Cost (Daily) - Selected",
        "avg_daily_external_cost": "Average Daily Cost for External Energy",
        "external_cost_help": "This is the energy that vehicles could not charge at your infrastructure and will need to obtain externally at a cost of €{cost:.2f}/kWh.",
        "partial_charge_warning": "⚠️ **Warning:** This configuration cannot fully charge all vehicles internally. Energy to be charged externally: {energy:.1f} kWh.",
        "full_charge_success": "✅ All vehicles can be fully charged with this configuration.",
        "detailed_planning_tab": "Detailed Planning",
        "vehicle_summary_tab": "Vehicle Summary",
        "all_configs_tab": "All Configurations",
        "detailed_optimization_analysis_tab": "Detailed Optimization Analysis",
        "gantt_intro": "View the charging schedule for each station. Each bar represents a charging session.",
        "gantt_warning": "⚠️ **Warning:** The Gantt visualization may become less readable with a high number of vehicles or charges. For detailed analysis, refer to the 'Charge Details' table.",
        "charge_details": "📅 Charge Details",
        "no_actual_charges": "No actual charges were planned for the charging stations.",
        "no_chargers_configured": "No chargers configured or no charges planned.",
        "vehicle_charge_summary": "🚗 Vehicle Charge Status Summary",
        "vehicle_charge_summary_intro": "This table summarizes the energy requested and internally charged for each vehicle or group of vehicles.",
        "type_col": "Type",
        "name_col": "Name",
        "energy_req_col": "Energy Requested (kWh)",
        "internal_energy_col": "Internal Energy (kWh)",
        "external_energy_col": "External Energy (kWh)",
        "charge_status_col": "Charge Status",
        "coverage_detail_col": "Coverage Detail",
        "complete_status": "✅ Complete",
        "partial_status": "⚠️ Partial",
        "complete_count": "{charged}/{total} complete",
        "charge_count": "{count} charges",
        "no_charge": "No charge",
        "all_tested_configs": "⚙️ All Tested Configurations",
        "configs_evaluated": "Configurations evaluated: **{count}**",
        "configs_order_info": "Configurations are ordered by: 1) % Internal Energy (max) 2) Total Installed Power (min) 3) Total Cost (min) 4) Combined Efficiency (max) 5) Number of Chargers (min).",
        "cost_analysis_selected_solution": "📈 Cost Analysis of Selected Solution",
        "charger_cost_pie": "Charger Cost",
        "installation_cost_pie": "Installation Cost",
        "maintenance_cost_pie": "Maintenance Cost (10 years)",
        "cost_distribution_title": "Distribution of Initial and Maintenance Costs (Selected Configuration)",
        "no_config_to_analyze": "No configuration to analyze for costs.",
        "detailed_optimization_analysis": "Detailed Optimization Analysis",
        "detailed_opt_intro": "This section provides additional charts to better understand the optimization results.",
        "energy_charged_by_type": "Energy Charged by Charger Type",
        "no_energy_charged": "No energy charged by the chargers in this configuration.",
        "vehicle_charge_status": "Vehicle Charging Status",
        "fully_charged": "Fully Charged",
        "partially_charged": "Partially Charged",
        "not_charged": "Not Charged",
        "charge_status_distribution": "Distribution of Vehicle Charging Status",
        "energy_req_vs_charged_top10": "Energy Requested vs. Charged per Vehicle (Top 10)",
        "no_vehicle_data_for_chart": "No vehicle data for this chart.",
        "detailed_partial_charge_explanation": "Detailed Explanation for a Specific Vehicle (Partial Charge)",
        "partial_charge_intro": "If a vehicle was not fully charged, this section helps you understand why.",
        "analysis_for_partial_vehicle": "Analysis for partially charged vehicle: **{name}**",
        "analysis_for_unassigned_vehicle": "Analysis for uncharged vehicle: **{name}**",
        "all_vehicles_fully_charged": "All vehicles were fully charged in this configuration. No explanation for partial charges is needed.",
        "vehicle_needs_energy_time": "Vehicle **{name}** needs **{energy:.1f} kWh** and has an available stop time of **{time:.1f} hours**.",
        "vehicle_charged_for": "It was charged for **{energy:.1f} kWh**.",
        "reasons_for_partial_charge": "##### Reasons for Partial/Incomplete Charging:",
        "insufficient_stop_time": "- **Insufficient stop time:** Even with the most powerful charger ({max_power} kW), the vehicle would have required more than {available_time:.1f} hours to charge {energy_needed:.1f} kWh. Minimum time required: {min_time_needed:.1f} hours.",
        "no_charger_available": "- **No charger available:** No free slot was found on any charger during the vehicle's stop period.",
        "charger_not_powerful_enough": "- **Assigned charger not powerful enough:** The assigned charger ({assigned_power} kW) was not powerful enough to provide {energy_needed:.1f} kWh in {available_time:.1f} hours. It would have required {time_needed_on_assigned:.1f} hours.",
        "scheduling_conflicts": "- **Scheduling conflicts/unavailable slots:** Although the assigned charger was theoretically capable of fully charging the vehicle, no continuous or sufficiently long slots were found due to other bookings or minimum intervals between charges.",
        "assignment_logic": "- **Assignment logic:** The system chose to assign a partial charge to optimize charger utilization or to serve more vehicles, given that a full charge was not the absolute priority or was not possible with the available resources at that time.",
        "to_ensure_full_charge": "To ensure a full charge, you could:",
        "increase_stop_time": "- Increase the available stop time for the vehicle.",
        "add_more_powerful_chargers": "- Add more powerful chargers.",
        "optimize_scheduling": "- Further optimize scheduling to reduce idle times.",
        "vehicle_fully_charged": "The vehicle was fully charged.",
        "no_optimization_results": "No optimization results available for detailed vehicle visualization. Please run the optimization first.",
        "configure_and_calculate": "Configure the parameters and vehicles in the sidebar, then click 'Calculate Infrastructure Optimization'.",
        "infrastructure_test_header": "📊 Test Your Existing Infrastructure",
        "infrastructure_test_intro": "This section allows you to simulate the performance of your current charging infrastructure against the needs of your vehicle fleet. Find out how much energy you can deliver internally and what costs you might face for external charging.",
        "test_params_vehicle_fleet": "Vehicle Fleet Parameters",
        "num_ev_vehicles": "Number of electric vehicles",
        "num_ev_vehicles_help": "How many electric vehicles do you have in your fleet?",
        "single_vehicle_test": "Vehicle {i}",
        "daily_km_test": "Daily km",
        "daily_km_test_help": "Average distance traveled per day.",
        "avg_consumption_test": "Average consumption (kWh/100km)",
        "avg_consumption_test_help": "Energy consumption per 100 km.",
        "available_stop_hours_test": "Available stop hours (for charging)",
        "available_stop_hours_test_help": "Hours when the vehicle is available for on-site charging.",
        "existing_infra_config": "Existing Charging Infrastructure Configuration",
        "existing_infra_intro": "Enter the number of chargers of each type you own.",
        "ac_11_chargers": "AC_11 Chargers (11 kW)",
        "ac_11_chargers_help": "Number of 11 kW AC chargers.",
        "ac_22_chargers": "AC_22 Chargers (22 kW)",
        "ac_22_chargers_help": "Number of 22 kW AC chargers.",
        "dc_30_chargers": "DC_30 Chargers (30 kW)",
        "dc_30_chargers_help": "Number of 30 kW DC chargers.",
        "dc_60_chargers": "DC_60 Chargers (60 kW)",
        "dc_60_chargers_help": "Number of 60 kW DC chargers.",
        "dc_90_chargers": "DC_90 Chargers (90 kW)",
        "dc_90_chargers_help": "Number of 90 kW DC chargers.",
        "daily_charger_hours": "Daily available charging hours (chargers)",
        "daily_charger_hours_help": "Hours per day when chargers are operational and accessible.",
        "economic_investment_params": "Economic and Investment Parameters",
        "economic_investment_intro": "Define energy costs and initial investment.",
        "internal_energy_cost_test": "Internal energy cost (€/kWh)",
        "internal_energy_cost_test_help": "Cost of energy (procurement) per kWh when charging at your infrastructure.",
        "external_energy_price_test": "External energy price (€/kWh)",
        "external_energy_price_test_help": "Cost per kWh if vehicles charge externally.",
        "charger_purchase_costs": "Charger purchase/installation costs (estimate)",
        "investment_ac11": "AC_11 Investment (€)",
        "investment_ac11_help": "Estimated cost for purchasing and installing an 11kW AC charger.",
        "investment_ac22": "AC_22 Investment (€)",
        "investment_ac22_help": "Estimated cost for purchasing and installing a 22kW AC charger.",
        "investment_dc30": "DC_30 Investment (€)",
        "investment_dc30_help": "Estimated cost for purchasing and installing a 30kW DC charger.",
        "investment_dc60": "DC_60 Investment (€)",
        "investment_dc60_help": "Estimated cost for purchasing and installing a 60kW DC charger.",
        "investment_dc90": "DC_90 Investment (€)",
        "investment_dc90_help": "Estimated cost for purchasing and installing a 90kW DC charger.",
        "run_infra_analysis": "🔄 Run Infrastructure Analysis",
        "add_vehicle_warning_analysis": "Please add at least one vehicle to run the analysis.",
        "analysis_execution": "Running analysis...",
        "analysis_complete_success": "Analysis completed successfully!",
        "performance_summary": "Performance Summary",
        "total_energy_requested": "Total energy requested",
        "total_energy_requested_help": "The total energy all vehicles in the fleet need daily.",
        "internal_energy_charged_test": "Internal energy charged",
        "internal_energy_charged_test_help": "The energy actually charged by your infrastructure.",
        "external_energy_to_charge": "Energy to be charged externally",
        "external_energy_to_charge_help": "The energy vehicles will need to obtain from public charging stations.",
        "estimated_time_lost": "Estimated time lost (external charges)",
        "estimated_time_lost_help": "Estimate of the time vehicles will spend charging externally (includes travel and waiting times).",
        "daily_external_charge_cost": "Daily external charging cost",
        "daily_external_charge_cost_help": "Estimated economic cost for charges made outside your infrastructure.",
        "avg_charger_utilization_rate": "Average charger utilization rate",
        "avg_charger_utilization_rate_help": "Percentage of time chargers are actually used for charging.",
        "fully_charged_cars": "Fully Charged Cars",
        "fully_charged_cars_help": "Number of vehicles that have completed their requested charge through your infrastructure.",
        "internal_operating_cost": "Internal Operating Cost",
        "internal_operating_cost_help": "Daily cost for energy supplied through your infrastructure.",
        "estimated_annual_savings_test": "Estimated Annual Savings",
        "estimated_annual_savings_test_help": "The estimated annual savings from internal charging compared to external charging.",
        "roi_test": "ROI (Return on Investment)",
        "roi_test_help": "The return on investment, calculated as the ratio of annual savings to total initial investment cost.",
        "charger_utilization_details": "Dettaglio Utilizzo Colonnine",
        "vehicle_charge_status_test": "Stato Ricarica Veicoli",
        "energy_req_vs_charged_test": "Energia Richiesta vs Caricata",
        "operating_costs_analysis_test": "Analisi Costi Operativi",
        "hourly_utilization_details": "Visualizza l'utilizzo orario per ciascun tipo di colonnina configurata.",
        "hourly_utilization_chart_title": "Ore di Utilizzo per Tipo di Colonnina",
        "no_chargers_configured_analysis": "Nessuna colonnina configurata per l'analisi.",
        "gantt_planning_details": "Pianificazione Dettaglio Ricariche (Gantt Chart)",
        "gantt_planning_intro": "Questa è una visualizzazione semplificata delle prenotazioni delle colonnine.",
        "no_charges_recorded": "Nessuna ricarica registrata per la configurazione attuale. Prova a modificare i parametri.",
        "vehicle_charge_status_chart_title": "Distribuzione dello Stato di Ricarica dei Veicoli",
        "run_analysis_to_view_status": "Esegui l'analisi per visualizzare lo stato di ricarica dei veicoli.",
        "energy_comparison_chart_title": "Confronto Energia Richiesta e Caricata per Veicolo",
        "run_analysis_to_view_comparison": "Esegui l'analisi per visualizzare il confronto energia richiesta vs. caricata.",
        "operating_costs_analysis_chart_title": "Analisi Costi Operativi (Interni vs Esterni)",
        "operating_costs_distribution_chart_title": "Distribuzione Costi Operativi Giornalieri",
        "run_analysis_to_view_costs": "Esegui l'analisi per visualizzare l'analisi dei costi operativi.",
        "optimization_suggestions": "Suggerimenti di ottimizzazione",
        "improvement_opportunity": "🔄 **Opportunità di Miglioramento:** Una parte significativa dell'energia richiesta (circa {energy:.1f} kWh) deve essere caricata esternamente. Considera di aggiungere colonnine o aumentare la potenza di quelle esistenti per ridurre questa dipendenza.",
        "fleet_coverage": "🚗 **Copertura del Parco Auto:** Solo {charged} su {total} veicoli sono stati caricati completamente. Valuta se la tua infrastruttura è sufficiente per l'intero parco o se alcuni veicoli hanno tempi di sosta troppo brevi per le colonnine disponibili.",
        "high_utilization_warning": "⚠️ **Attenzione:** Le colonnine sono ben utilizzate, con un tasso medio del {utilization:.1f}%. Se prevedi una crescita del parco auto, potrebbe essere il momento di espandere l'infrastruttura per evitare colli di bottiglia.",
        "low_utilization_info": "ℹ️ **Valuta l'Efficienza:** Il tasso di utilizzo delle colonnine è del {utilization:.1f}%, indicando una possibile sottoutilizzazione. Potresti considerare di ridurre il numero di colonnine, attrarre più veicoli, o esplorare modelli di business aggiuntivi (es. ricarica pubblica) per massimizzare il ritorno sull'investimento.",
        "well_balanced_utilization": "✅ **Ben Bilanciato:** L'utilizzo delle colonnine è ben bilanciato per il tuo attuale parco auto.",
        "good_roi_success": "💰 **Ottimo Ritorno sull'Investimento:** Con un ROI del {roi:.1f}% annuo, l'investimento nella tua infrastruttura di ricarica si sta dimostrando molto vantaggioso. Considera ulteriori espansioni!",
        "positive_roi_info": "📈 **Investimento Profittevole:** Il tuo investimento sta generando un ROI positivo del {roi:.1f}%. Monitora l'andamento e considera come ottimizzare ulteriormente.",
        "negative_roi_error": "📉 **Rivedi l'Investimento:** Attualmente, il ROI è negativo ({roi:.1f}%). È fondamentale analizzare i costi e i benefici per capire come migliorare la redditività dell'infrastruttura. Potresti aver bisogno di più veicoli, ottimizzare l'uso delle colonnine, o rinegoziare i costi dell'energia.",
        "roi_not_calculable": "ℹ️ **ROI non calcolabile:** Non è stato specificato un investimento iniziale per le colonnine, quindi il ROI non è calcolabile. Inserisci i costi di investimento per una valutazione completa.",
        "run_analysis_to_view_suggestions": "Esegui l'analisi per visualizzare i suggerimenti di ottimizzazione.",
        "performance_eval_header": "📈 Valutazione Rendimento di un Punto di Ricarica",
        "performance_eval_intro": "Questa sezione ti aiuta a stimare il potenziale guadagno e il ritorno sull'investimento (ROI) di un punto di ricarica basandosi sul numero di auto previste, i costi e i prezzi di vendita dell'energia.",
        "charging_point_usage_params": "Parametri di Utilizzo del Punto di Ricarica",
        "base_usage_params": "Parametri Base di Utilizzo",
        "expected_daily_cars": "Auto previste in ricarica al giorno",
        "expected_daily_cars_help": "Numero medio di veicoli che si prevede ricarichino ogni giorno.",
        "avg_energy_per_car": "Energia media richiesta per auto (kWh)",
        "avg_energy_per_car_help": "Energia media che ciascun veicolo richiede per una ricarica.",
        "avg_charge_time": "Tempo medio di ricarica per auto (ore)",
        "avg_charge_time_help": "Tempo medio di permanenza per una ricarica (non direttamente usato nel calcolo ma utile per contesto).",
        "operational_time_config": "Configurazione Temporale Operativa",
        "daily_op_hours": "Ore operative al giorno",
        "daily_op_hours_help": "Ore al giorno in cui il punto di ricarica è disponibile.",
        "annual_op_days": "Giorni operativi all'anno",
        "annual_op_days_help": "Numero di giorni all'anno in cui il punto di ricarica è attivo.",
        "economic_utilization_params": "Parametri Economici e di Utilizzo",
        "energy_sale_price": "Prezzo di vendita energia (€/kWh)",
        "energy_sale_price_help": "Il prezzo al quale l'energia viene venduta ai clienti.",
        "energy_purchase_cost": "Costo acquisto energia (€/kWh)",
        "energy_purchase_cost_help": "Il costo al quale acquisti l'energia per le colonnine.",
        "infra_utilization_prob": "Probabilità di utilizzo dell'infrastruttura (%)",
        "infra_utilization_prob_help": "Percentuale del tempo in cui le colonnine sono effettivamente occupate, dato dalla domanda e dalla disponibilità.",
        "max_initial_investment": "Investimento Iniziale Massima (€)",
        "max_initial_investment_help": "Budget massimo per l'acquisto e l'installazione delle colonnine.",
        "additional_annual_op_costs": "Costi Operativi Aggiuntivi (Annuali)",
        "annual_charger_maintenance_cost": "Costo Manutenzione Annuale Colonnine (€)",
        "annual_charger_maintenance_cost_help": "Costo annuale stimato per la manutenzione di tutte le colonnine.",
        "annual_software_cost": "Costo Software/Gestione Annuale (€)",
        "annual_software_cost_help": "Costo annuale per software di gestione, connettività, ecc.",
        "annual_insurance_cost": "Costo Assicurazione Annuale (€)",
        "annual_insurance_cost_help": "Costo annuale dell'assicurazione per l'infrastruttura.",
        "annual_land_cost": "Costo Affitto/Uso Terreno Annuale (€)",
        "annual_land_cost_help": "Costo annuale per l'affitto o l'uso del terreno (se applicabile).",
        "useful_life_years": "Vita Utile Impianto (anni)",
        "useful_life_years_help": "Estimated useful life of the system for depreciation calculation.",
        "charger_point_config": "Configurazione delle Colonnine per il Punto di Ricarica",
        "select_quantify_chargers": "Seleziona e Quantifica le Colonnine",
        "ac22_chargers_eval": "AC_22 (22 kW)",
        "ac22_chargers_eval_help": "Numero di colonnine AC da 22 kW.",
        "dc20_chargers_eval": "DC_20 (20 kW)",
        "dc20_chargers_eval_help": "Numero di colonnine DC da 20 kW.",
        "dc30_chargers_eval": "DC_30 (30 kW)",
        "dc30_chargers_eval_help": "Numero di colonnine DC da 30 kW.",
        "dc40_chargers_eval": "DC_40 (40 kW)",
        "dc40_chargers_eval_help": "Numero di colonnine DC da 40 kW.",
        "dc60_chargers_eval": "DC_60 (60 kW)",
        "dc60_chargers_eval_help": "Numero di colonnine DC da 60 kW.",
        "dc90_chargers_eval": "DC_90 (90 kW)",
        "dc90_chargers_eval_help": "Numero di colonnine DC da 90 kW.",
        "calculate_point_performance": "📊 Calcola Rendimento Punto di Ricarica",
        "calculate_performance_spinner": "Calcolo rendimento...",
        "performance_analysis_complete": "Analisi di rendimento completata!",
        "charging_point_summary": "Riepilogo del Punto di Ricarica",
        "total_installed_power": "Potenza totale installata",
        "total_installed_power_help": "La somma delle potenze di tutte le colonnine installate.",
        "estimated_annual_energy_delivered": "Energia erogata annuale stimata",
        "estimated_annual_energy_delivered_help": "La quantità totale di energia che si prevede sarà erogata dal punto di ricarica in un anno.",
        "daily_cars_served": "Auto servite giornaliere",
        "daily_cars_served_help": "Il numero di auto che si prevede saranno servite completamente ogni giorno.",
        "key_economic_indicators": "Indicatori Economici Chiave",
        "estimated_annual_revenue": "Ricavo annuo stimato",
        "estimated_annual_revenue_help": "Il ricavo lordo annuale basato sull'energia erogata e il prezzo di vendita.",
        "total_system_cost_capex": "Costo totale impianto (CAPEX)",
        "within_budget": "Within budget",
        "over_budget": "Over budget",
        "total_system_cost_capex_help": "The total cost for purchasing and installing chargers (Capital Expenditure).",
        "annual_operating_cost_opex": "Annual Operating Cost (OPEX)",
        "annual_operating_cost_opex_help": "The total annual management cost, including energy, maintenance, software, etc.",
        "detailed_financial_analysis": "Detailed Financial Analysis",
        "estimated_annual_net_profit": "Estimated Annual Net Profit",
        "estimated_annual_net_profit_help": "The net annual profit after deducting all operating costs and depreciation.",
        "payback_period": "Payback Period",
        "payback_period_help": "The estimated time required to recover the initial investment through net revenues generated.",
        "infinite_payback": "Infinite",
        "detailed_visualization_tab": "Detailed Visualization",
        "financial_summary_tab": "Financial Summary",
        "payback_trend_tab": "Payback Trend",
        "investment_distribution_tab": "Investment Distribution",
        "cars_served_vs_not_served": "Distribution of Cars Served vs. Not Served",
        "served_cars": "Cars served",
        "not_served_cars": "Cars not served",
        "estimated_monthly_energy_delivered": "Estimated Monthly Energy Delivered (with seasonality)",
        "annual_financial_summary": "Annual Financial Summary (Revenue vs. Costs)",
        "revenue": "Revenue",
        "cost": "Cost",
        "profit": "Profit",
        "cumulative_net_profit_trend": "Cumulative Net Profit Trend and Payback Period",
        "cumulative_net_profit": "Cumulative Net Profit (€)",
        "initial_investment": "Initial Investment (€)",
        "payback_line": "Payback: {years:.1f} years",
        "payback_not_calculable": "Payback period is not calculable or net profit is negative. Chart cannot be generated.",
        "initial_investment_cost_distribution": "Distribution of Initial Investment Costs",
        "charger_cost_component": "Charger Cost",
        "installation_cost_component": "Installation Cost",
        "run_analysis_to_view_investment": "Run the analysis to view the investment cost distribution.",
        "optimization_recommendations": "Optimization Recommendations",
        "highly_utilized_infra": "⚠️ **Infrastructure is highly utilized.** To maximize revenue and customer satisfaction, consider:",
        "add_more_chargers_rec": "- **Add more chargers:** If demand exceeds supply.",
        "increase_installed_power_rec": "- **Increase installed power:** For faster charging, if possible.",
        "extend_op_hours_rec": "- **Extend operational hours:** To cover a wider time slot.",
        "underutilized_infra": "ℹ️ **Infrastructure is underutilized.** To improve performance, you could:",
        "reduce_chargers_rec": "- **Reduce the number of chargers:** If the cost outweighs the benefit.",
        "attract_more_customers_rec": "- **Try to attract more customers:** Through marketing or partnerships.",
        "offer_promo_rates_rec": "- **Offer promotional rates:** To incentivize off-peak usage.",
        "investment_over_budget": "❌ **Investment exceeds budget.** To stay within limits, evaluate:",
        "review_charger_mix_rec": "- **Review the charger mix:** Preferring lower-cost AC chargers over high-power DC ones.",
        "phase_investment_rec": "- **Phase the investment:** Planning installation in multiple stages.",
        "seek_funding_rec": "- **Seek funding or incentives:** To cover part of the costs.",
        "cars_not_served_warning": "🔌 **{count} cars per day cannot be served.** This leads to potential revenue loss and dissatisfaction. Consider:",
        "increase_charger_power_rec": "- **Increase charger power:** To reduce charging times and serve more vehicles.",
        "optimize_charge_times_rec": "- **Optimize charging times:** By educating users or implementing maximum parking policies.",
        "implement_booking_system_rec": "- **Implement a booking system:** To better manage flow and reduce idle times.",
        "negative_net_profit_warning": "📉 **Warning: Negative Net Profit!** Your charging point does not seem to be profitable with current parameters. Consider:",
        "increase_sale_price_rec": "- **Increase the energy selling price.**",
        "reduce_op_costs_rec": "- **Reduce operating costs:** By negotiating better prices for energy or maintenance.",
        "increase_utilization_rec": "- **Increase utilization rate:** Attract more customers or extend operational hours.",
        "review_initial_investment_rec": "- **Review the initial investment:** If it is too high for expected revenues.",
        "run_analysis_to_view_recommendations": "Run the analysis to view optimization recommendations.",
        "configure_and_calculate_point": "Configure the charging point parameters and chargers, then click 'Calculate Charging Point Performance'.",
        "footer_text": "AI-Josa Suite by EV Field Service - Comprehensive tools for planning and optimizing electric vehicle charging infrastructure",
        "colonnina_label": "Charging Station",
        "vehicle_label": "Vehicle",
        "start_time_label": "Start Time",
        "end_time_label": "End Time",
        "charge_time_label": "Charge Time",
        "energy_kwh_label": "Energy (kWh)",
        "charger_type_label": "Charger Type",
        "hours_used_label": "Hours Used",
        "category_label": "Category",
        "value_label": "Value",
        "month_label": "Month",
        "component_label": "Component",
        "cost_label": "Cost (€)",
        "year_label": "Year",
        "cumulative_net_profit_label": "Cumulative Net Profit (€)",
        "initial_investment_label": "Initial Investment (€)",
        "financial_summary_category_label": "Category",
        "financial_summary_value_label": "Value (€)",
        "financial_summary_type_label": "Type",
        "revenue_label": "Revenue",
        "cost_label_short": "Cost",
        "profit_label_short": "Profit",
        "power": "Power",
        "kw": "kW",
        "cost_unit": "Unit Cost",
        "euro": "€",
        "charger_type": "Charger Type",
        "hour_of_day": "Hour of Day",
        "charger": "Charger",
        "no_charge_gantt": "No charge",
        "gantt_chart_title": "Charging Schedule",
        "day_label": "day",
        "single_label": "Single",
        "group_label": "Group",
        "num_vehicles_label": "Number of Vehicles",
        "config_label": "Configuration",
        "total_initial_cost_label": "Total Initial Cost",
        "budget_utilization_label": "Budget Utilization",
        "vehicles_served_percentage": "% Vehicles Served",
        "num_chargers_label": "Num. Chargers",
        "temporal_efficiency_label": "Temporal Efficiency",
        "energy_efficiency_label": "Energy Efficiency",
        "combined_efficiency_label": "Combined Efficiency",
        "daily_external_cost_label": "Daily External Cost",
        "years_label": "years",
        "total_installed_power_label": "Total Installed Power (kW)"
    }
}

# Function to get translated text
def get_text(key):
    lang = st.session_state.get("language", "it")
    return translations[lang].get(key, key) # Fallback to key if translation not found

# Language selection radio button
st.sidebar.header("🌐 Language / Lingua")
st.session_state.language = st.sidebar.radio(
    "Choose your language / Scegli la tua lingua",
    ["it", "en"],
    format_func=lambda x: "Italiano" if x == "it" else "English",
    key="language_selector"
)

# Application title
st.title(get_text("app_title"))

# Create tabs
tab1, tab2, tab3 = st.tabs([
    get_text("tab1_title"),
    get_text("tab2_title"),
    get_text("tab3_title")
])

# Global constant for minimum charge duration (in hours)
MIN_DURATA_RICARICA = 0.25 # 15 minutes

# =============================================================================
# 1. CHARGING STATION OPTIMIZER (OTTIMIZZATORE COLONNINE)
# =============================================================================
with tab1:
    st.header(get_text("optimizer_header"))
    st.markdown(get_text("optimizer_intro"))

    COLONNINE_TAB1 = {
        "AC_22": {
            "potenza_effettiva": 11,
            "costo_colonnina": 1500,
            "costo_installazione": 1650,
            "costo_manutenzione_anno": 50,
            "colore": "#808080"
        },
        "DC_20": {
            "potenza_effettiva": 20,
            "costo_colonnina": 7000,
            "costo_installazione": 3000,
            "costo_manutenzione_anno": 150,
            "colore": "#00FF00"
        },
        "DC_30": {
            "potenza_effettiva": 30,
            "costo_colonnina": 8000,
            "costo_installazione": 4500,
            "costo_manutenzione_anno": 200,
            "colore": "#0000FF"
        },
        "DC_50": {
            "potenza_effettiva": 50,
            "costo_colonnina": 12000,
            "costo_installazione": 7500,
            "costo_manutenzione_anno": 250,
            "colore": "#FFA500"
        },
        "DC_60": {
            "potenza_effettiva": 60,
            "costo_colonnina": 15000,
            "costo_installazione": 9000,
            "costo_manutenzione_anno": 300,
            "colore": "#FF4500"
        },
        "DC_90": {
            "potenza_effettiva": 90,
            "costo_colonnina": 20000,
            "costo_installazione": 13500,
            "costo_manutenzione_anno": 400,
            "colore": "#FF0000"
        }
    }

    MIN_INTERVALLO_RICARICA = 0.5  # 30 minuti tra una ricarica e l'altra per una colonnina

    def calcola_tempo_ricarica(energia, potenza):
        """
        Calculates the time needed to charge a given amount of energy at a specific power.
        Rounds up to the nearest 15-minute increment, with a minimum of 15 minutes.
        """
        return max(MIN_DURATA_RICARICA, ceil((energia / potenza) * 4) / 4)

    def trova_slot_disponibile(prenotazioni, inizio_sosta_veicolo, fine_sosta_veicolo):
        """
        Finds the largest available time slot on a charging station within a vehicle's stop duration,
        considering existing bookings and a minimum interval between charges.
        """
        prenotazioni.sort(key=lambda x: x["inizio"])

        best_slot = None
        max_duration = 0

        # Check slot before the first booking
        potential_start = max(inizio_sosta_veicolo, 0.0)
        potential_end = fine_sosta_veicolo
        if prenotazioni:
            potential_end = min(fine_sosta_veicolo, prenotazioni[0]["inizio"] - MIN_INTERVALLO_RICARICA)

        if potential_end - potential_start >= MIN_DURATA_RICARICA:
            max_duration = potential_end - potential_start
            best_slot = (potential_start, potential_end)

        # Check slots between existing bookings
        for i in range(len(prenotazioni)):
            current_booking_end = prenotazioni[i]["fine"]
            next_booking_start = prenotazioni[i+1]["inizio"] if i + 1 < len(prenotazioni) else 24.0 # Assume day ends at 24.0

            potential_slot_start = max(inizio_sosta_veicolo, current_booking_end + MIN_INTERVALLO_RICARICA)
            potential_slot_end = min(fine_sosta_veicolo, next_booking_start - MIN_INTERVALLO_RICARICA)

            if potential_slot_end - potential_slot_start > max_duration:
                if potential_slot_end - potential_slot_start >= MIN_DURATA_RICARICA:
                    max_duration = potential_slot_end - potential_slot_start
                    best_slot = (potential_slot_start, potential_slot_end)

        # If no slot found yet, check after the last booking
        if not best_slot and prenotazioni:
            potential_start = max(inizio_sosta_veicolo, prenotazioni[-1]["fine"] + MIN_INTERVALLO_RICARICA)
            potential_end = fine_sosta_veicolo
            if potential_end - potential_start >= MIN_DURATA_RICARICA:
                if potential_end - potential_start > max_duration:
                    max_duration = potential_start - potential_end # This was a bug, should be potential_end - potential_start
                    max_duration = potential_end - potential_start
                    best_slot = (potential_start, potential_end)
        
        # Final check for minimum duration
        if best_slot and (best_slot[1] - best_slot[0]) < MIN_DURATA_RICARICA and (best_slot[1] - best_slot[0]) > 0.01:
            # If the best slot is less than MIN_DURATA_RICARICA but still meaningful, allow it for a finishing charge
            pass
        elif best_slot and (best_slot[1] - best_slot[0]) <= 0.01: # If duration is negligible
            return None
        elif not best_slot and max_duration < MIN_DURATA_RICARICA: # If no slot found or too short
            return None

        return best_slot


    def espandi_veicoli(veicoli):
        """
        Expands a list of vehicles, handling 'group' entries by creating individual vehicle instances.
        """
        veicoli_espansi = []
        for v in veicoli:
            if v.get("gruppo", False):
                for i in range(v["quantita"]):
                    veicoli_espansi.append({
                        "nome": f"{v['nome']}_{i+1}",
                        "km": v["km"],
                        "consumo": v["consumo"],
                        "energia": v["km"] * v["consumo"],
                        "inizio": v["inizio"],
                        "fine": v["fine"],
                        "gruppo_origine": v["nome"]
                    })
            else:
                veicoli_espansi.append(v.copy())
        return veicoli_espansi

    def simula_ricariche(config, veicoli, costi, turnazioni_ac=3, turnazioni_dc=8):
        """
        Simulates the charging process for a given configuration of charging stations and vehicles.
        Assigns vehicles to available slots and calculates KPIs.
        Prioritizes faster chargers for high-demand vehicles within their available time.
        """
        colonnine = []
        for tipo, quantita in config.items():
            for i in range(quantita):
                # Set a maximum number of bookings per day for each station type
                max_prenotazioni = (
                    turnazioni_ac if tipo == "AC_22" else
                    turnazioni_dc if tipo.startswith("DC_") else
                    float('inf') # Default to infinite if not specified
                )
                colonnine.append({
                    "tipo": tipo,
                    "nome": f"{tipo}_{i+1}",
                    "potenza": COLONNINE_TAB1[tipo]["potenza_effettiva"],
                    "prenotazioni": [], # List to store bookings for this station
                    "max_prenotazioni": max_prenotazioni
                })

        veicoli_singoli = espandi_veicoli(veicoli)
        energia_totale_richiesta = sum(v["energia"] for v in veicoli_singoli)

        # Initialize remaining energy and charging history for each vehicle
        for v in veicoli_singoli:
            v["energia_rimanente"] = v["energia"]
            v["ricariche"] = []
            # This tracks the earliest time a vehicle can start its next charge
            v["prossimo_inizio_ricarica_disponibile"] = v["inizio"]

        # Main simulation loop: continue as long as vehicles need charging and charges can be assigned
        # Use a large number of iterations to prevent infinite loops, but allow for full charging
        max_charge_iterations = 24 * 4 * len(veicoli_singoli) # Max 4 15-min slots per hour, per vehicle
        
        for _ in range(max_charge_iterations):
            # Sort vehicles to prioritize those with less remaining energy or shorter stop durations
            veicoli_da_servire_in_turno = sorted(
                [v for v in veicoli_singoli if v["energia_rimanente"] > 0],
                key=lambda x: (x["fine"], -x["energia_rimanente"]) # Prioritize vehicles leaving soonest, then those needing more energy
            )

            if not veicoli_da_servire_in_turno:
                break # All vehicles are charged

            charged_in_this_turn = set() # To track which vehicles were charged in this iteration

            for veicolo in veicoli_da_servire_in_turno:
                if veicolo["energia_rimanente"] <= 0 or veicolo["nome"] in charged_in_this_turn:
                    continue # Vehicle already fully charged or handled in this turn

                best_charge_details = {
                    "colonnina": None,
                    "slot_inizio": None,
                    "slot_fine": None,
                    "energia_caricabile": 0,
                    "can_fully_charge": False
                }

                for col in colonnine:
                    # Skip colonnine that have reached their daily booking limit
                    if len(col["prenotazioni"]) >= col["max_prenotazioni"]:
                        continue
                        
                    # Find the best available slot on this specific charging station for the current vehicle
                    slot = trova_slot_disponibile(
                        col["prenotazioni"],
                        max(veicolo["inizio"], veicolo["prossimo_inizio_ricarica_disponibile"]), # Vehicle can't start before its earliest available time
                        veicolo["fine"]
                    )
                    
                    if slot:
                        durata_slot = slot[1] - slot[0]
                        # Ensure the slot is long enough for a meaningful charge, or if it's a finishing charge
                        if durata_slot >= MIN_DURATA_RICARICA or (veicolo["energia_rimanente"] / col["potenza"] <= MIN_DURATA_RICARICA and veicolo["energia_rimanente"] > 0):
                            energia_potenziale_in_slot = col["potenza"] * durata_slot
                            energy_to_charge_this_attempt = min(veicolo["energia_rimanente"], energia_potenziale_in_slot)

                            if energy_to_charge_this_attempt > 0:
                                current_can_fully_charge = (abs(energy_to_charge_this_attempt - veicolo["energia_rimanente"]) < 0.01)

                                # Decision logic:
                                # 1. Prefer full charge over partial.
                                # 2. Among full charges, prefer higher power (faster).
                                # 3. Among partial charges, prefer higher energy delivered (higher power).
                                if (current_can_fully_charge and not best_charge_details["can_fully_charge"]):
                                    # New option can fully charge, and current best cannot
                                    best_charge_details = {
                                        "colonnina": col,
                                        "slot_inizio": slot[0],
                                        "slot_fine": slot[1],
                                        "energia_caricabile": energy_to_charge_this_attempt,
                                        "can_fully_charge": True
                                    }
                                elif (current_can_fully_charge and best_charge_details["can_fully_charge"]):
                                    # Both can fully charge, prefer higher power
                                    if col["potenza"] > best_charge_details["colonnina"]["potenza"]:
                                        best_charge_details = {
                                            "colonnina": col,
                                            "slot_inizio": slot[0],
                                            "slot_fine": slot[1],
                                            "energia_caricabile": energy_to_charge_this_attempt,
                                            "can_fully_charge": True
                                        }
                                elif (not current_can_fully_charge and not best_charge_details["can_fully_charge"]):
                                    # Both are partial, prefer higher energy delivered (higher power)
                                    if energy_to_charge_this_attempt > best_charge_details["energia_caricabile"]:
                                        best_charge_details = {
                                            "colonnina": col,
                                            "slot_inizio": slot[0],
                                            "slot_fine": slot[1],
                                            "energia_caricabile": energy_to_charge_this_attempt,
                                            "can_fully_charge": False
                                        }

                # If a best option was found for the vehicle
                if best_charge_details["colonnina"]:
                    colonnina = best_charge_details["colonnina"]
                    slot_inizio = best_charge_details["slot_inizio"]
                    slot_fine = best_charge_details["slot_fine"]
                    energia_caricabile_effettiva = best_charge_details["energia_caricabile"]

                    if energia_caricabile_effettiva > 0:
                        time_needed_for_effective_charge = energia_caricabile_effettiva / colonnina["potenza"]
                        final_charge_duration = time_needed_for_effective_charge

                        # If the calculated charge duration is too short, but the vehicle needs only a little more energy
                        if final_charge_duration < MIN_DURATA_RICARICA:
                            energy_for_min_duration = colonnina["potenza"] * MIN_DURATA_RICARICA
                            if (veicolo["energia_rimanente"] <= energy_for_min_duration + 0.01 and veicolo["energia_rimanente"] > 0):
                                final_charge_duration = veicolo["energia_rimanente"] / colonnina["potenza"] # Use exactly what's needed
                                if final_charge_duration <= 0.001: # Avoid negligible charges
                                    continue
                            else:
                                continue # Skip if it's too short and not a finishing charge

                        # Ensure the charge doesn't exceed the available slot time
                        final_charge_duration = min(final_charge_duration, slot_fine - slot_inizio)

                        if final_charge_duration > 0.001: # Ensure a meaningful charge
                            actual_energy_charged = colonnina["potenza"] * final_charge_duration

                            veicolo["energia_rimanente"] -= actual_energy_charged

                            # Add booking to the charging station's schedule
                            colonnina["prenotazioni"].append({
                                "veicolo": veicolo["nome"],
                                "inizio": slot_inizio,
                                "fine": slot_inizio + final_charge_duration,
                                "energia": actual_energy_charged,
                                "tempo_ricarica": final_charge_duration
                            })
                            colonnina["prenotazioni"].sort(key=lambda x: x["inizio"]) # Keep bookings sorted

                            # Add to vehicle's individual charge history
                            veicolo["ricariche"].append({
                                "colonnina": colonnina["nome"],
                                "inizio": slot_inizio,
                                "fine": slot_inizio + final_charge_duration,
                                "energia": actual_energy_charged
                            })

                            # Update the vehicle's next available start time for charging
                            veicolo["prossimo_inizio_ricarica_disponibile"] = slot_inizio + final_charge_duration + MIN_INTERVALLO_RICARICA

                            charged_in_this_turn.add(veicolo["nome"])
                            # This break is crucial to move to the next vehicle once it's assigned a charge
                            break

            # If no vehicles were charged in this iteration, and there are still vehicles needing charge,
            # it means no more suitable slots can be found. Break to prevent infinite loop.
            if not charged_in_this_turn and any(v["energia_rimanente"] > 0 for v in veicoli_singoli):
                break
            # If all vehicles are charged, break
            if all(v["energia_rimanente"] <= 0 for v in veicoli_singoli):
                break

        energia_interna = sum(v["energia"] - v["energia_rimanente"] for v in veicoli_singoli)
        energia_esterna = energia_totale_richiesta - energia_interna

        return {
            "config": config,
            "colonnine": colonnine,
            "veicoli_originali": veicoli,
            "veicoli_singoli": veicoli_singoli,
            "kpi": {
                "energia_totale": energia_totale_richiesta,
                "energia_interna": energia_interna,
                "energia_esterna": energia_esterna,
                "costo_totale": sum(COLONNINE_TAB1[t]["costo_colonnina"]*q + COLONNINE_TAB1[t]["costo_installazione"]*q for t,q in config.items()),
                "veicoli_serviti": sum(1 for v in veicoli_singoli if v["energia_rimanente"] < v["energia"])
            }
        }

    def calcola_kpi_avanzati(risultato, costi, alpha=0.5):
        """
        Calculates additional Key Performance Indicators (KPIs) based on simulation results,
        including combined efficiency.
        """
        if not risultato:
            return

        ore_utilizzo = 0
        energia_erogata = 0
        energia_massima = 0 # Max theoretical energy if stations ran 24/7 at full power

        for col in risultato["colonnine"]:
            ore_utilizzo_col = sum(p["tempo_ricarica"] for p in col["prenotazioni"])
            energia_erogata_col = sum(p["energia"] for p in col["prenotazioni"])

            energia_massima_col = col["potenza"] * 24 # Max energy this station could provide in 24 hours

            ore_utilizzo += ore_utilizzo_col
            energia_erogata += energia_erogata_col
            energia_massima += energia_massima_col

        efficienza_temporale = ore_utilizzo / (24 * len(risultato["colonnine"])) if risultato["colonnine"] else 0
        efficienza_energetica = energia_erogata / energia_massima if energia_massima > 0 else 0
        efficienza_combinata = alpha * efficienza_temporale + (1 - alpha) * efficienza_energetica

        risultato["kpi"].update({
            "costo_manutenzione_annuale": sum(COLONNINE_TAB1[t]["costo_manutenzione_anno"]*q for t,q in risultato["config"].items()),
            "ore_utilizzo_colonnine": ore_utilizzo,
            "efficienza_temporale": efficienza_temporale,
            "efficienza_energetica": efficienza_energetica,
            "efficienza_combinata": efficienza_combinata,
            "risparmio_vs_benzina": risultato["kpi"]["energia_totale"] * (costi["benzina"] - costi["privato"]),
            "risparmio_vs_pubblico": risultato["kpi"]["energia_interna"] * (costi["pubblico"] - costi["privato"]),
        })

    def ottimizza_configurazione(veicoli, budget, costi, alpha=0.5, max_power_kw=100, turnazioni_ac=3, turnazioni_dc=8):
        """
        Finds the optimal charging station configuration within a given budget and max power,
        prioritizing internal energy served, then combined efficiency, total cost, and number of stations.
        """
        veicoli_singoli = espandi_veicoli(veicoli)
        energia_totale = sum(v["energia"] for v in veicoli_singoli)

        configurazioni_da_testare = []

        # Generate configurations: AC_22 only
        max_ac_solo = min(20, floor(budget / (COLONNINE_TAB1["AC_22"]["costo_colonnina"] + COLONNINE_TAB1["AC_22"]["costo_installazione"])))
        for qta_ac in range(1, max_ac_solo + 1):
            current_config = {"AC_22": qta_ac}
            current_power = current_config["AC_22"] * COLONNINE_TAB1["AC_22"]["potenza_effettiva"]
            if current_power <= max_power_kw:
                configurazioni_da_testare.append(current_config)

        # Generate configurations: DC only and DC with AC_22 combinations
        tipi_dc = ["DC_20", "DC_30", "DC_50", "DC_60", "DC_90"]
        for tipo_dc in tipi_dc:
            costo_dc_unitario = COLONNINE_TAB1[tipo_dc]["costo_colonnina"] + COLONNINE_TAB1[tipo_dc]["costo_installazione"]
            max_qta_dc = min(5, floor(budget / costo_dc_unitario)) # Limit DC stations to 5 for practical reasons and performance

            for qta_dc in range(1, max_qta_dc + 1):
                budget_remaining_for_ac = budget - (qta_dc * costo_dc_unitario)

                # Add DC-only configuration if within power limits
                current_power_dc_only = qta_dc * COLONNINE_TAB1[tipo_dc]["potenza_effettiva"]
                if current_power_dc_only <= max_power_kw and costo_dc_unitario * qta_dc <= budget:
                    configurazioni_da_testare.append({tipo_dc: qta_dc})

                if budget_remaining_for_ac <= 0:
                    continue

                # Ensure a minimum number of AC chargers if combining with DC (e.g., 20% of DC quantity, but at least 1)
                min_ac_required = ceil(qta_dc * 0.20)
                if min_ac_required == 0 and qta_dc > 0: # If DC exists, at least 1 AC
                    min_ac_required = 1

                max_ac_possible = min(
                    20, # Limit AC stations in hybrid configs
                    floor(budget_remaining_for_ac / (COLONNINE_TAB1["AC_22"]["costo_colonnina"] + COLONNINE_TAB1["AC_22"]["costo_installazione"]))
                )

                if max_ac_possible < min_ac_required:
                    continue

                for qta_ac in range(min_ac_required, max_ac_possible + 1):
                    current_config_hybrid = {tipo_dc: qta_dc, "AC_22": qta_ac}

                    current_power_hybrid = (qta_dc * COLONNINE_TAB1[tipo_dc]["potenza_effettiva"]) + \
                                           (qta_ac * COLONNINE_TAB1["AC_22"]["potenza_effettiva"])

                    costo_config_ibrida = sum(COLONNINE_TAB1[t]["costo_colonnina"]*q + COLONNINE_TAB1[t]["costo_installazione"]*q
                                              for t,q in current_config_hybrid.items())

                    if current_power_hybrid <= max_power_kw and costo_config_ibrida <= budget:
                        configurazioni_da_testare.append(current_config_hybrid)

        # Remove duplicate configurations
        unique_configs = []
        seen = set()
        for d in configurazioni_da_testare:
            # Convert dict to a frozenset of items for hashability
            frozenset_d = frozenset(d.items())
            if frozenset_d not in seen:
                seen.add(frozenset_d)
                unique_configs.append(d)

        best = None
        risultati = []
        # Simulate each unique configuration and evaluate
        for config in unique_configs:
            res = simula_ricariche(config, veicoli, costi, turnazioni_ac, turnazioni_dc)

            current_power_installed = sum(COLONNINE_TAB1[t]["potenza_effettiva"] * q for t, q in config.items())

            if res["kpi"]["costo_totale"] <= budget and current_power_installed <= max_power_kw:
                calcola_kpi_avanzati(res, costi, alpha) # Calculate advanced KPIs including combined efficiency
                
                # Calculate the percentage of internal energy charged
                internal_energy_percentage = res["kpi"]["energia_interna"] / res["kpi"]["energia_totale"] if res["kpi"]["energia_totale"] > 0 else 0

                # Define the current configuration's "score" based on new priorities
                # 1. Maximize internal_energy_percentage (so -percentage for sorting ascending)
                # 2. Minimize total_installed_power
                # 3. Minimize total_initial_cost
                # 4. Maximize combined_efficiency (tie-breaker)
                # 5. Minimize number of chargers (tie-breaker)
                current_score = (
                    -internal_energy_percentage, # Maximize this
                    current_power_installed,      # Minimize this
                    res["kpi"]["costo_totale"], # Minimize this
                    -res["kpi"]["efficienza_combinata"], # Maximize this
                    sum(res["config"].values()) # Minimize this
                )
                res["score"] = current_score # Store score for easy access

                risultati.append(res)

                if not best:
                    best = res
                else:
                    # Compare current result with the best found so far using the defined score
                    if current_score < best["score"]: # Tuple comparison works lexicographically
                        best = res

        return best, risultati

    def mostra_gantt(colonnine_configurate_finali):
        """
        Displays a Gantt chart visualizing the charging schedule for each station.
        """
        gantt_data = []

        # Collect all colonnina names to ensure all are represented in the Y-axis, even if not used
        all_colonnina_names = []
        for col in colonnine_configurate_finali:
            all_colonnina_names.append({"nome": col["nome"], "tipo": col["tipo"]})

        for col in colonnine_configurate_finali:
            if col["prenotazioni"]:
                for slot in col["prenotazioni"]:
                    gantt_data.append({
                        "ChargerName": col["nome"], # Fixed internal column name
                        "ChargerType": col["tipo"], # Fixed internal column name
                        "StartTime": datetime(2023,1,1) + timedelta(hours=slot["inizio"]), # Base date for Plotly
                        "EndTime": datetime(2023,1,1) + timedelta(hours=slot["fine"]),
                        "Vehicle": slot["veicolo"],
                        "EnergyKWh": slot["energia"],
                        "ChargeTime": f"{slot['tempo_ricarica']:.2f}h",
                        "Color": COLONNINE_TAB1[col["tipo"]]["colore"],
                        "Utilized": True
                    })
            else:
                # Add an entry for unused stations to ensure they appear in the Gantt chart
                gantt_data.append({
                    "ChargerName": col["nome"], # Fixed internal column name
                    "ChargerType": col["tipo"], # Fixed internal column name
                    "StartTime": datetime(2023,1,1), # Start at 00:00
                    "EndTime": datetime(2023,1,1), # End at 00:00 (or slightly after for visibility)
                    "Vehicle": get_text("no_charge_gantt"),
                    "EnergyKWh": 0,
                    "ChargeTime": "0.00h",
                    "Color": COLONNINE_TAB1[col["tipo"]]["colore"], # Use station's default color
                    "Utilized": False
                })

        if gantt_data:
            df = pd.DataFrame(gantt_data)

            # Sort the DataFrame to ensure consistent order in the Gantt chart Y-axis
            # Sort by type (AC first, then DC) and then by number (e.g., AC_22_1, AC_22_2, DC_30_1)
            df["OrderKey"] = df["ChargerName"].apply(lambda x: (x.split('_')[0], int(x.split('_')[2]) if len(x.split('_')) > 2 else 0))
            df = df.sort_values(by="OrderKey").drop(columns="OrderKey")

            # Create a rich hover information string
            df["Info"] = df.apply(
                lambda row: (
                    f"{row['Vehicle']}<br>"
                    f"{row['StartTime'].strftime('%H:%M')} - {row['EndTime'].strftime('%H:%M')}<br>"
                    f"{row['ChargeTime']} ({row['EnergyKWh']:.1f} kWh)"
                ) if row['Utilized'] else get_text("no_charge_gantt"), axis=1
            )

            fig = px.timeline(
                df,
                x_start="StartTime", x_end="EndTime", y="ChargerName", # Use fixed column names
                color="ChargerType", # Use fixed column name
                hover_name="Info",
                hover_data={"StartTime": False, "EndTime": False, "ChargeTime": False, "EnergyKWh": False, "Info": False, "Utilized": False},
                color_discrete_map={t: c["colore"] for t,c in COLONNINE_TAB1.items()},
                title=get_text("gantt_chart_title"),
                template="plotly_white" # Use a light theme for charts
            )
            fig.update_xaxes(tickformat="%H:%M", title_text=get_text("hour_of_day")) # Format x-axis as time, add title
            fig.update_yaxes(title_text=get_text("charger")) # Add y-axis title (translated)
            # Ensure bars are visible even for zero-duration "Nessuna ricarica" entries
            fig.update_traces(marker_line_width=0, selector=dict(type='bar'))

            fig.update_layout(
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial"
                ),
                yaxis=dict(categoryorder='array', categoryarray=df["ChargerName"].unique()) # Maintain custom order
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader(get_text("charge_details"))
            df_dettaglio = df[df["Utilized"] == True].copy()
            if not df_dettaglio.empty:
                df_dettaglio["StartTime"] = df_dettaglio["StartTime"].dt.strftime("%H:%M")
                df_dettaglio["EndTime"] = df_dettaglio["EndTime"].dt.strftime("%H:%M")
                st.dataframe(
                    df_dettaglio[["ChargerName", "Vehicle", "StartTime", "EndTime", "ChargeTime", "EnergyKWh"]], # Use fixed column names
                    column_config={
                        "ChargerName": st.column_config.Column(get_text("colonnina_label")), # Display translated label
                        "Vehicle": st.column_config.Column(get_text("vehicle_label")),
                        "StartTime": st.column_config.Column(get_text("start_time_label")),
                        "EndTime": st.column_config.Column(get_text("end_time_label")),
                        "ChargeTime": st.column_config.NumberColumn(get_text("charge_time_label"), format="%.2f h"),
                        "EnergyKWh": st.column_config.NumberColumn(get_text("energy_kwh_label"), format="%.1f kWh")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(get_text("no_actual_charges"))
        else:
            st.warning(get_text("no_chargers_configured"))

    def genera_confronto_configurazioni(risultati, budget, costi):
        """
        Displays a comparison table and cost analysis pie chart for all valid configurations.
        """
        if not risultati:
            st.warning(get_text("no_config_to_analyze"))
            return pd.DataFrame(), [] # Return empty DataFrame and list

        # Ensure advanced KPIs are calculated for all results
        for res in risultati:
            if 'efficienza_combinata' not in res['kpi']:
                calcola_kpi_avanzati(res, costi)

        # Sort results based on optimization criteria for display in the table
        risultati_ordinati_for_display = sorted(
            risultati,
            key=lambda x: (
                -(x["kpi"]["energia_interna"] / x["kpi"]["energia_totale"] if x["kpi"]["energia_totale"] > 0 else 0), # Maximize % internal energy
                sum(COLONNINE_TAB1[t]["potenza_effettiva"] * q for t, q in x["config"].items()), # Minimize total installed power
                x["kpi"]["costo_totale"], # Minimize total initial cost
                -x["kpi"]["efficienza_combinata"], # Maximize combined efficiency
                sum(x["config"].values()) # Minimize number of chargers
            )
        )

        df_confronto = pd.DataFrame([{
            "Config": "+".join(f"{q}x{t}" for t,q in r["config"].items()), # Fixed internal column name
            "TotalInitialCost": r["kpi"]["costo_totale"], # Fixed internal column name
            "BudgetUtilization": f"{r['kpi']['costo_totale']/budget*100:.1f}%", # Fixed internal column name
            "InternalEnergy": r["kpi"]["energia_interna"], # Fixed internal column name
            "ExternalEnergy": r["kpi"]["energia_esterna"], # Fixed internal column name
            "VehiclesServedPercentage": f"{r['kpi']['energia_interna']/r['kpi']['energia_totale']*100 if r['kpi']['energia_totale'] > 0 else 0:.1f}%", # Fixed internal column name
            "NumChargers": sum(r["config"].values()), # Fixed internal column name
            "TemporalEfficiency": f"{r['kpi']['efficienza_temporale']*100:.1f}%", # Fixed internal column name
            "EnergyEfficiency": f"{r['kpi']['efficienza_energetica']*100:.1f}%", # Fixed internal column name
            "CombinedEfficiency": f"{r['kpi']['efficienza_combinata']*100:.1f}%", # Fixed internal column name
            "DailyExternalCost": f"{r['kpi']['energia_esterna'] * costi['pubblico']:.2f}", # Fixed internal column name
            "TotalInstalledPower": sum(COLONNINE_TAB1[t]["potenza_effettiva"] * q for t, q in r["config"].items()) # New column
        } for r in risultati_ordinati_for_display]) # Use the sorted list for the DataFrame

        return df_confronto, risultati_ordinati_for_display


    def mostra_riepilogo_veicoli(risultato):
        """
        Displays a summary table of how well each vehicle (or group) was served.
        """
        st.subheader(get_text("vehicle_charge_summary")) # Changed subheader title
        st.markdown(get_text("vehicle_charge_summary_intro")) # Added markdown

        # Group expanded vehicles back by their original group for summary
        veicoli_per_gruppo = defaultdict(list)
        for ve in risultato["veicoli_singoli"]:
            if "gruppo_origine" in ve:
                veicoli_per_gruppo[ve["gruppo_origine"]].append(ve)
            else:
                veicoli_per_gruppo[ve["nome"]].append(ve)

        veicoli_data = []

        # Populate data for the summary table
        for v in risultato["veicoli_originali"]: # Iterate over original vehicles to get groups
            if v.get("gruppo", False):
                veicoli_gruppo = veicoli_per_gruppo.get(v["nome"], [])
                energia_richiesta = v["energia"] * v["quantita"]
                energia_caricata = sum(ve["energia"] - ve["energia_rimanente"] for ve in veicoli_gruppo)

                veicoli_data.append({
                    "Type": get_text("group_label"), # Fixed internal column name
                    "Name": f"{v['nome']} (x{v['quantita']})", # Fixed internal column name
                    "EnergyRequested": energia_richiesta, # Fixed internal column name
                    "InternalEnergy": energia_caricata, # Fixed internal column name
                    "ExternalEnergy": energia_richiesta - energia_caricata, # Fixed internal column name
                    "ChargeStatus": get_text("complete_status") if abs(energia_richiesta - energia_caricata) < 0.01 else get_text("partial_status"), # Fixed internal column name, added tolerance
                    "CoverageDetail": get_text("complete_count").format(charged=len([ve for ve in veicoli_gruppo if abs(ve['energia_rimanente']) < 0.01]), total=v['quantita']) # Fixed internal column name, added tolerance
                })
            else:
                veicolo_singolo = next((ve for ve in risultato["veicoli_singoli"] if ve["nome"] == v["nome"]), None)
                if veicolo_singolo:
                    energia_caricata = v["energia"] - veicolo_singolo["energia_rimanente"]
                    veicoli_data.append({
                        "Type": get_text("single_label"), # Fixed internal column name
                        "Name": v["nome"], # Fixed internal column name
                        "EnergyRequested": v["energia"], # Fixed internal column name
                        "InternalEnergy": energia_caricata, # Fixed internal column name
                        "ExternalEnergy": v["energia"] - energia_caricata, # Fixed internal column name
                        "ChargeStatus": get_text("complete_status") if abs(v["energia"] - energia_caricata) < 0.01 else get_text("partial_status"), # Fixed internal column name, added tolerance
                        "CoverageDetail": get_text("charge_count").format(count=len(veicolo_singolo['ricariche'])) if "ricariche" in veicolo_singolo else get_text("no_charge") # Fixed internal column name
                    })

        df = pd.DataFrame(veicoli_data)

        st.dataframe(
            df,
            column_config={
                "Type": st.column_config.Column(get_text("type_col")), # Display translated label
                "Name": st.column_config.Column(get_text("name_col")),
                "EnergyRequested": st.column_config.NumberColumn(get_text("energy_req_col"), format="%.1f kWh"),
                "InternalEnergy": st.column_config.NumberColumn(get_text("internal_energy_col"), format="%.1f kWh"),
                "ExternalEnergy": st.column_config.NumberColumn(get_text("external_energy_col"), format="%.1f kWh"),
                "ChargeStatus": st.column_config.Column(get_text("charge_status_col")),
                "CoverageDetail": st.column_config.Column(get_text("coverage_detail_col"))
            },
            hide_index=True,
            use_container_width=True
        )

    def input_parametri_tab1():
        """
        Collects global configuration parameters from the Streamlit sidebar.
        Allows dynamic modification of charging station costs.
        """
        st.sidebar.header(get_text("sidebar_config_params"))
        st.sidebar.markdown(get_text("sidebar_config_intro"))

        with st.sidebar.expander(get_text("economic_tech_params"), expanded=True):
            budget = st.slider(get_text("budget_available"), 5000, 200000, 30000, 500, key="tab1_budget",
                                 help=get_text("budget_help"))
            max_power_kw = st.slider(get_text("max_power_kw"), 0, 500, 100, 10, key="tab1_max_power", # Increased max value
                                     help=get_text("max_power_help"))
            alpha = st.slider(get_text("alpha_weight"), 0.0, 1.0, 0.5, 0.1, key="tab1_alpha",
                                 help=get_text("alpha_help"))
            turnazioni_ac = st.slider(get_text("ac_turns"), 1, 10, 3, 1, key="tab1_turnazioni_ac",
                                      help=get_text("ac_turns_help"))
            turnazioni_dc = st.slider(get_text("dc_turns"), 1, 20, 8, 1, key="tab1_turnazioni_dc",
                                      help=get_text("dc_turns_help"))

        with st.sidebar.expander(get_text("energy_costs"), expanded=False):
            costo_privato = st.number_input(get_text("private_charge_cost"), 0.10, 0.50, 0.25, 0.01, key="tab1_privato",
                                             help=get_text("private_charge_help"))
            costo_pubblico = st.number_input(get_text("public_charge_cost"), 0.30, 1.00, 0.50, 0.05, key="tab1_pubblico",
                                              help=get_text("public_charge_help"))

        with st.sidebar.expander(get_text("gas_comparison_params"), expanded=False):
            st.info(get_text("gas_comparison_info"))
            costo_benzina_km = st.number_input(get_text("gas_cost_km"), 0.05, 0.30, 0.15, 0.01, key="tab1_benzina_km",
                                                 help=get_text("gas_cost_help"))
            consumo_equivalente = st.number_input(get_text("ev_consumption_eq"), 0.10, 0.20, 0.12, 0.01, key="tab1_consumo_eq",
                                                   help=get_text("ev_consumption_help"))

        st.sidebar.subheader(get_text("modify_charger_costs"))
        st.sidebar.markdown(get_text("modify_charger_intro"))
        with st.sidebar.expander(get_text("charger_details_expander"), expanded=False): # New key for expander
            for tipo, dati in COLONNINE_TAB1.items():
                st.write(f"**{tipo}** ({get_text('power')}: {dati['potenza_effettiva']} {get_text('kw')})")
                COLONNINE_TAB1[tipo]["costo_colonnina"] = st.number_input(
                    get_text("unit_cost"),
                    value=dati["costo_colonnina"],
                    key=f"tab1_costo_{tipo}_colonnina",
                    help=get_text("unit_cost_help").format(type=tipo)
                )
                COLONNINE_TAB1[tipo]["costo_installazione"] = st.number_input(
                    get_text("installation_cost"),
                    value=dati["costo_installazione"],
                    key=f"tab1_costo_{tipo}_installazione",
                    help=get_text("installation_cost_help").format(type=tipo)
                )
                COLONNINE_TAB1[tipo]["costo_manutenzione_anno"] = st.number_input(
                    get_text("annual_maintenance_cost"),
                    value=dati["costo_manutenzione_anno"],
                    key=f"tab1_costo_{tipo}_manutenzione",
                    help=get_text("annual_maintenance_cost_help").format(type=tipo)
                )
                st.markdown("---")

        return {
            "budget": budget,
            "alpha": alpha,
            "max_power_kw": max_power_kw,
            "turnazioni_ac": turnazioni_ac,
            "turnazioni_dc": turnazioni_dc,
            "costo_privato": costo_privato,
            "costo_pubblico": costo_pubblico,
            "benzina": costo_benzina_km / consumo_equivalente if consumo_equivalente > 0 else 0
        }

    def input_veicoli_tab1():
        """
        Collects vehicle configuration details from the Streamlit sidebar,
        allowing input for single vehicles or groups of vehicles.
        """
        st.sidebar.header(get_text("vehicle_config"))
        st.sidebar.markdown(get_text("vehicle_config_intro"))

        modalita_inserimento = st.sidebar.radio(
            get_text("input_mode"),
            [get_text("single_vehicles"), get_text("vehicle_groups")],
            index=0,
            key="tab1_modalita_veicoli",
            help=get_text("input_mode_help")
        )

        veicoli = []

        if modalita_inserimento == get_text("single_vehicles"):
            num_veicoli = st.sidebar.number_input(get_text("num_single_vehicles"), 1, 100, 3, key="tab1_num_veicoli_singoli",
                                                 help=get_text("num_single_vehicles_help"))

            for i in range(num_veicoli):
                with st.sidebar.expander(get_text("single_vehicle").format(i=i+1), expanded=(i<3)):
                    nome = st.text_input(get_text("vehicle_name").format(i=i+1), f"Veicolo_{i+1}", key=f"tab1_nome_{i}")

                    cols = st.columns(2)
                    with cols[0]:
                        km = st.number_input(get_text("daily_km"), 10, 500, 100, key=f"tab1_km_{i}", help=get_text("daily_km_help"))
                    with cols[1]:
                        cons = st.number_input(get_text("consumption_kwh_km"), 0.10, 0.50, 0.17, 0.01, key=f"tab1_cons_{i}", help=get_text("consumption_kwh_km_help"))

                    cols = st.columns(2)
                    with cols[0]:
                        inizio = st.number_input(get_text("stop_start_time"), 0.0, 24.0, 8.0, 0.5, key=f"tab1_inizio_{i}", help=get_text("stop_start_time_help"))
                    with cols[1]:
                        fine = st.number_input(get_text("stop_end_time"), 0.0, 24.0, 18.0, 0.5, key=f"tab1_fine_{i}", help=get_text("stop_end_time_help"))

                    veicoli.append({
                        "nome": nome,
                        "km": km,
                        "consumo": cons,
                        "energia": km * cons,
                        "inizio": inizio,
                        "fine": fine,
                        "gruppo": False
                    })
        else:
            num_gruppi = st.sidebar.number_input(get_text("num_vehicle_groups"), 1, 10, 2, key="tab1_num_gruppi",
                                                 help=get_text("num_vehicle_groups_help"))

            for i in range(num_gruppi):
                with st.sidebar.expander(get_text("vehicle_group").format(i=i+1), expanded=(i<2)):
                    nome = st.text_input(get_text("group_name").format(i=i+1), f"Gruppo_{i+1}", key=f"tab1_nome_gruppo_{i}")

                    cols = st.columns(2)
                    with cols[0]:
                        quantita = st.number_input(get_text("group_quantity"), 1, 100, 5, key=f"tab1_qta_{i}", help=get_text("group_quantity_help"))
                        km = st.number_input(get_text("group_daily_km"), 10, 500, 100, key=f"tab1_km_gruppo_{i}", help=get_text("group_daily_km_help"))
                    with cols[1]:
                        cons = st.number_input(get_text("group_consumption"), 0.10, 0.50, 0.17, 0.01, key=f"tab1_cons_gruppo_{i}", help=get_text("group_consumption_help"))

                    cols = st.columns(2)
                    with cols[0]:
                        inizio = st.number_input(get_text("group_stop_start"), 0.0, 24.0, 8.0, 0.5, key=f"tab1_inizio_gruppo_{i}", help=get_text("group_stop_start_help"))
                    with cols[1]:
                        fine = st.number_input(get_text("group_stop_end"), 0.0, 24.0, 18.0, 0.5, key=f"tab1_fine_gruppo_{i}", help=get_text("group_stop_end_help"))

                    veicoli.append({
                        "nome": nome,
                        "quantita": quantita,
                        "km": km,
                        "consumo": cons,
                        "energia": km * cons,
                        "inizio": inizio,
                        "fine": fine,
                        "gruppo": True
                    })

        return veicoli

    # Main execution flow for Tab 1
    # Collect parameters and vehicle data from the sidebar
    parametri_tab1 = input_parametri_tab1()
    veicoli_tab1 = input_veicoli_tab1()

    st.markdown("---") # Separator for better UI

    # Initialize session state variables for optimization results
    if 'risultati_ottimizzazione' not in st.session_state:
        st.session_state.risultati_ottimizzazione = None
    if 'best_config_ottimizzazione' not in st.session_state:
        st.session_state.best_config_ottimizzazione = None
    if 'selected_config_index' not in st.session_state:
        st.session_state.selected_config_index = 0 # Default to the first (best) config

    # Button to trigger optimization
    if st.button(get_text("calculate_optimization"), key="tab1_calcola", type="primary"):
        if not veicoli_tab1:
            st.warning(get_text("add_vehicle_warning"))
        else:
            with st.spinner(get_text("analysis_in_progress")):
                costi_tab1 = {
                    "privato": parametri_tab1["costo_privato"],
                    "pubblico": parametri_tab1["costo_pubblico"],
                    "benzina": parametri_tab1["benzina"]
                }

                best_tab1, risultati_tab1 = ottimizza_configurazione(
                    veicoli_tab1,
                    parametri_tab1["budget"],
                    costi_tab1,
                    alpha=parametri_tab1["alpha"],
                    max_power_kw=parametri_tab1["max_power_kw"],
                    turnazioni_ac=parametri_tab1["turnazioni_ac"],
                    turnazioni_dc=parametri_tab1["turnazioni_dc"]
                )

                if not best_tab1:
                    st.error(get_text("no_solution_found"))
                    st.session_state.risultati_ottimizzazione = None
                    st.session_state.best_config_ottimizzazione = None
                else:
                    # The best_tab1 already has its score calculated within ottimizza_configurazione
                    st.session_state.risultati_ottimizzazione = risultati_tab1
                    st.session_state.best_config_ottimizzazione = best_tab1
                    st.session_state.selected_config_index = 0 # Reset to best when new optimization runs

    # Display optimization results if available in session state
    if st.session_state.risultati_ottimizzazione:
        st.header(get_text("optimization_results"))

        # Sort results for display based on the new criteria
        risultati_tab1_sorted_for_display = sorted(
            st.session_state.risultati_ottimizzazione,
            key=lambda x: (
                -(x["kpi"]["energia_interna"] / x["kpi"]["energia_totale"] if x["kpi"]["energia_totale"] > 0 else 0), # Maximize % internal energy
                sum(COLONNINE_TAB1[t]["potenza_effettiva"] * q for t, q in x["config"].items()), # Minimize total installed power
                x["kpi"]["costo_totale"], # Minimize total initial cost
                -x["kpi"]["efficienza_combinata"], # Maximize combined efficiency
                sum(x["config"].values()) # Minimize number of chargers
            )
        )

        current_displayed_config = None
        if risultati_tab1_sorted_for_display and st.session_state.selected_config_index < len(risultati_tab1_sorted_for_display):
            current_displayed_config = risultati_tab1_sorted_for_display[st.session_state.selected_config_index]
        elif st.session_state.best_config_ottimizzazione: # Fallback to best if index is somehow off
            current_displayed_config = st.session_state.best_config_ottimizzazione
            st.session_state.selected_config_index = 0 # Reset index to 0

        if current_displayed_config:
            st.subheader(get_text("selected_solution"))
            # Added line to show the selected configuration explicitly
            st.markdown(f"**{get_text('current_config_display')}** {' + '.join(f'{q}x{t}' for t,q in current_displayed_config['config'].items())}")
            cols = st.columns(len(current_displayed_config["config"]) + 1)
            for i, (tipo, quantita) in enumerate(current_displayed_config["config"].items()):
                cols[i].metric(
                    label=get_text("chargers_label").format(type=tipo),
                    value=quantita,
                    help=f"{get_text('power')}: {COLONNINE_TAB1[tipo]['potenza_effettiva']} {get_text('kw')}, {get_text('cost_unit')}: {get_text('euro')}{COLONNINE_TAB1[tipo]['costo_colonnina']:,.0f}"
                )

            cols[-1].metric(
                label=get_text("total_chargers"),
                value=sum(current_displayed_config["config"].values()),
                help=get_text("total_chargers_help").format(config_str=' + '.join(f'{q}x{t}' for t,q in current_displayed_config['config'].items()))
            )

            st.markdown("---")
            st.subheader(get_text("kpi_header"))
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

            col_kpi1.metric(get_text("total_initial_cost"), f"€{current_displayed_config['kpi']['costo_totale']:,.0f}",
                           get_text("budget_percentage").format(percent=current_displayed_config['kpi']['costo_totale']/parametri_tab1['budget']*100))
            col_kpi2.metric(get_text("internal_energy_charged"), f"{current_displayed_config['kpi']['energia_interna']:,.1f} kWh",
                           get_text("total_request_percentage").format(percent=(current_displayed_config['kpi']['energia_interna']/current_displayed_config['kpi']['energia_totale']*100 if current_displayed_config['kpi']['energia_totale']>0 else 0)))
            col_kpi3.metric(get_text("estimated_annual_savings"), f"€{current_displayed_config['kpi']['risparmio_vs_pubblico']*365:,.0f}",
                           get_text("vs_public_charges"))
            col_kpi4.metric(get_text("combined_efficiency"), f"{current_displayed_config['kpi']['efficienza_combinata']*100:.1f}%",
                           help=get_text("combined_efficiency_help").format(temp_eff=current_displayed_config['kpi']['efficienza_temporale']*100, energy_eff=current_displayed_config['kpi']['efficienza_energetica']*100))

            st.subheader(get_text("estimated_external_charge_cost"))
            st.metric(
                label=get_text("avg_daily_external_cost"),
                value=f"€{current_displayed_config['kpi']['energia_esterna'] * parametri_tab1['costo_pubblico']:.2f}",
                help=get_text("external_cost_help").format(cost=parametri_tab1['costo_pubblico'])
            )
            
            if abs(current_displayed_config['kpi']['energia_esterna']) > 0.01:
                st.warning(get_text("partial_charge_warning").format(energy=current_displayed_config['kpi']['energia_esterna']))
            else:
                st.success(get_text("full_charge_success"))


            tab1_1, tab1_2, tab1_3, tab1_4 = st.tabs([get_text("detailed_planning_tab"), get_text("vehicle_summary_tab"), get_text("all_configs_tab"), get_text("detailed_optimization_analysis_tab")])

            with tab1_1:
                st.markdown(get_text("gantt_intro"))
                if len(current_displayed_config["veicoli_singoli"]) > 50 or sum(len(col["prenotazioni"]) for col in current_displayed_config["colonnine"]) > 100:
                    st.warning(get_text("gantt_warning"))
                mostra_gantt(current_displayed_config["colonnine"])

            with tab1_2:
                mostra_riepilogo_veicoli(current_displayed_config)

            with tab1_3:
                df_confronto_display, all_risultati_sorted = genera_confronto_configurazioni(
                    st.session_state.risultati_ottimizzazione,
                    parametri_tab1["budget"],
                    {
                        "privato": parametri_tab1["costo_privato"],
                        "pubblico": parametri_tab1["costo_pubblico"],
                        "benzina": parametri_tab1["benzina"]
                    }
                )
                
                st.subheader(get_text("all_tested_configs"))
                st.info(get_text("configs_evaluated").format(count=len(df_confronto_display)))
                st.caption(get_text("configs_order_info"))

                selected_rows = st.dataframe(
                    df_confronto_display,
                    key="tab1_all_configs_df",
                    on_select="rerun",
                    selection_mode="single-row",
                    column_config={
                        "Config": st.column_config.Column(get_text("config_label")),
                        "TotalInitialCost": st.column_config.NumberColumn(get_text("total_initial_cost_label"), format="€%.0f"),
                        "BudgetUtilization": st.column_config.Column(get_text("budget_utilization_label")),
                        "InternalEnergy": st.column_config.NumberColumn(get_text("internal_energy_col"), format="%.1f kWh"),
                        "ExternalEnergy": st.column_config.NumberColumn(get_text("external_energy_col"), format="%.1f kWh"),
                        "VehiclesServedPercentage": st.column_config.Column(get_text("vehicles_served_percentage")),
                        "NumChargers": st.column_config.NumberColumn(get_text("num_chargers_label"), format="%d"),
                        "TemporalEfficiency": st.column_config.Column(get_text("temporal_efficiency_label")),
                        "EnergyEfficiency": st.column_config.Column(get_text("energy_efficiency_label")),
                        "CombinedEfficiency": st.column_config.Column(get_text("combined_efficiency_label")),
                        "DailyExternalCost": st.column_config.NumberColumn(get_text("daily_external_cost_label"), format="€%.2f"),
                        "TotalInstalledPower": st.column_config.NumberColumn(get_text("total_installed_power_label"), format="%.0f kW") # New column config
                    },
                    hide_index=True,
                    use_container_width=True
                )

                if selected_rows and selected_rows['selection']['rows']:
                    st.session_state.selected_config_index = selected_rows['selection']['rows'][0]
                    # No need to explicitly set current_displayed_config_from_selection here,
                    # as the rerun will pick it up from selected_config_index at the top of the block.
                # else: if no row is selected, selected_config_index defaults to 0 (best config)

                st.subheader(get_text("cost_analysis_selected_solution"))
                # Use the selected config for the pie chart
                config_for_pie_chart = current_displayed_config # Always use the currently displayed config
                if config_for_pie_chart:
                    fig = px.pie(
                        names=[get_text("charger_cost_pie"), get_text("installation_cost_pie"), get_text("maintenance_cost_pie")],
                        values=[
                            sum(COLONNINE_TAB1[t]["costo_colonnina"]*q for t,q in config_for_pie_chart["config"].items()),
                            sum(COLONNINE_TAB1[t]["costo_installazione"]*q for t,q in config_for_pie_chart["config"].items()),
                            config_for_pie_chart["kpi"]["costo_manutenzione_annuale"]*10
                        ],
                        title=get_text("cost_distribution_title"),
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(get_text("no_config_to_analyze"))
            
            with tab1_4:
                st.subheader(get_text("detailed_optimization_analysis"))
                st.markdown(get_text("detailed_opt_intro"))

                st.markdown(f"#### {get_text('energy_charged_by_type')}")
                charger_energy_data = defaultdict(float)
                for col in current_displayed_config["colonnine"]:
                    for booking in col["prenotazioni"]:
                        charger_energy_data[col["tipo"]] += booking["energia"]
                
                if charger_energy_data:
                    df_charger_energy = pd.DataFrame([
                        {"ChargerType": k, "EnergyKWh": v} for k, v in charger_energy_data.items() # Fixed internal column names
                    ])
                    fig_charger_energy = px.bar(df_charger_energy, x="ChargerType", y="EnergyKWh", # Use fixed column names
                                                title=get_text("energy_charged_by_type"),
                                                color="ChargerType",
                                                color_discrete_map={t: COLONNINE_TAB1[t]["colore"] for t in COLONNINE_TAB1.keys()},
                                                template="plotly_white")
                    fig_charger_energy.update_xaxes(title_text=get_text("charger_type_label")) # Apply translated label
                    fig_charger_energy.update_yaxes(title_text=get_text("energy_kwh_label")) # Apply translated label
                    st.plotly_chart(fig_charger_energy, use_container_width=True)
                else:
                    st.info(get_text("no_energy_charged"))

                st.markdown(f"#### {get_text('vehicle_charge_status')}")
                charged_count = sum(1 for v in current_displayed_config["veicoli_singoli"] if abs(v["energia_rimanente"]) < 0.01)
                partial_count = sum(1 for v in current_displayed_config["veicoli_singoli"] if v["energia_rimanente"] > 0.01 and v["energia_rimanente"] < v["energia"])
                unassigned_count = sum(1 for v in current_displayed_config["veicoli_singoli"] if abs(v["energia_rimanente"] - v["energia"]) < 0.01)

                df_charge_status = pd.DataFrame({
                    "ChargeStatus": [get_text("fully_charged"), get_text("partially_charged"), get_text("not_charged")], # Fixed internal column name
                    "NumVehicles": [charged_count, partial_count, unassigned_count] # Fixed internal column name
                })
                fig_charge_status_pie = px.pie(df_charge_status, values="NumVehicles", names="ChargeStatus", # Use fixed column names
                                                title=get_text("charge_status_distribution"),
                                                color_discrete_sequence=px.colors.qualitative.Set2,
                                                template="plotly_white")
                st.plotly_chart(fig_charge_status_pie, use_container_width=True)

                st.markdown(f"#### {get_text('energy_req_vs_charged_top10')}")
                df_veicoli_charged = pd.DataFrame([
                    {
                        "Vehicle": v["nome"], # Fixed internal column name
                        "EnergyRequested": v["energia"], # Fixed internal column name
                        "InternalEnergy": v["energia"] - v["energia_rimanente"] # Fixed internal column name
                    } for v in current_displayed_config["veicoli_singoli"]
                ])
                df_veicoli_charged = df_veicoli_charged.sort_values(by="EnergyRequested", ascending=False).head(10) # Use fixed column name

                if not df_veicoli_charged.empty:
                    fig_energy_comparison = px.bar(df_veicoli_charged, x="Vehicle", y=["EnergyRequested", "InternalEnergy"], # Use fixed column names
                                                    barmode='group',
                                                    title=get_text("energy_comparison_chart_title"),
                                                    template="plotly_white")
                    fig_energy_comparison.update_xaxes(title_text=get_text("vehicle_label")) # Apply translated label
                    fig_energy_comparison.update_yaxes(title_text=get_text("energy_kwh_label")) # Apply translated label
                    st.plotly_chart(fig_energy_comparison, use_container_width=True)
                else:
                    st.info(get_text("no_vehicle_data_for_chart"))


                st.markdown("---")
                st.subheader(get_text("detailed_partial_charge_explanation"))
                st.markdown(get_text("partial_charge_intro"))
                
                partially_charged_vehicles = [v for v in current_displayed_config["veicoli_singoli"] if v["energia_rimanente"] > 0.01 and v["energia_rimanente"] < v["energia"]]
                unassigned_vehicles_full_energy = [v for v in current_displayed_config["veicoli_singoli"] if abs(v["energia_rimanente"] - v["energia"]) < 0.01]

                example_vehicle = None
                if partially_charged_vehicles:
                    example_vehicle = partially_charged_vehicles[0]
                    st.info(get_text("analysis_for_partial_vehicle").format(name=example_vehicle['nome']))
                elif unassigned_vehicles_full_energy:
                    example_vehicle = unassigned_vehicles_full_energy[0]
                    st.info(get_text("analysis_for_unassigned_vehicle").format(name=example_vehicle['nome']))
                else:
                    st.success(get_text("all_vehicles_fully_charged"))

                if example_vehicle:
                    energy_needed_ex = example_vehicle["energia"]
                    energy_charged_ex = energy_needed_ex - example_vehicle["energia_rimanente"]
                    time_available_ex = example_vehicle["fine"] - example_vehicle["inizio"]

                    st.write(get_text("vehicle_needs_energy_time").format(name=example_vehicle['nome'], energy=energy_needed_ex, time=time_available_ex))
                    st.write(get_text("vehicle_charged_for").format(energy=energy_charged_ex))

                    if energy_charged_ex < energy_needed_ex:
                        st.markdown(get_text("reasons_for_partial_charge"))
                        possible_reasons = []

                        could_full_charge_any_charger = False
                        for charger_type, charger_data in COLONNINE_TAB1.items():
                            time_to_full_charge = energy_needed_ex / charger_data["potenza_effettiva"]
                            if time_to_full_charge <= time_available_ex:
                                could_full_charge_any_charger = True
                                break
                        
                        if not could_full_charge_any_charger:
                            possible_reasons.append(get_text("insufficient_stop_time").format(max_power=max(c['potenza_effettiva'] for c in COLONNINE_TAB1.values()), available_time=time_available_ex, energy_needed=energy_needed_ex, min_time_needed=energy_needed_ex / max(c['potenza_effettiva'] for c in COLONNINE_TAB1.values())))
                        else:
                            if not example_vehicle["ricariche"]:
                                possible_reasons.append(get_text("no_charger_available"))
                            else:
                                assigned_charger_power = 0
                                if example_vehicle["ricariche"]:
                                    last_charge = example_vehicle["ricariche"][-1]
                                    for col in current_displayed_config["colonnine"]:
                                        if col["nome"] == last_charge["colonnina"]:
                                            assigned_charger_power = col["potenza"]
                                            break
                                
                                if assigned_charger_power > 0:
                                    time_needed_on_assigned = energy_needed_ex / assigned_charger_power
                                    if time_needed_on_assigned > time_available_ex:
                                        possible_reasons.append(get_text("charger_not_powerful_enough").format(assigned_power=assigned_charger_power, energy_needed=energy_needed_ex, available_time=time_available_ex, time_needed_on_assigned=time_needed_on_assigned))
                                    else:
                                        possible_reasons.append(get_text("scheduling_conflicts"))
                                else:
                                    possible_reasons.append(get_text("assignment_logic"))

                        for reason in possible_reasons:
                            st.markdown(reason)
                        st.markdown("---")
                        st.markdown(get_text("to_ensure_full_charge"))
                        st.markdown(get_text("increase_stop_time"))
                        st.markdown(get_text("add_more_powerful_chargers"))
                        st.markdown(get_text("optimize_scheduling"))
                    else:
                        st.success(get_text("vehicle_fully_charged"))
                else:
                    st.info(get_text("no_optimization_results"))

    else:
        st.info(get_text("configure_and_calculate"))


# =============================================================================
# 2. INFRASTRUCTURE TEST (TEST INFRASTRUTTURA)
# =============================================================================
with tab2:
    st.header(get_text("infrastructure_test_header"))
    st.markdown(get_text("infrastructure_test_intro"))

    # Initialize session state for results of tab2 to avoid KeyError on initial load
    if 'risultati_tab2' not in st.session_state:
        st.session_state.risultati_tab2 = None

    def calculate_infrastructure_test(veicoli, colonnine_config, costo_energia_interna, prezzo_energia_pubblica, ore_disponibili, costi_investimento_colonnine):
        """
        Simulates charging for a given infrastructure configuration and vehicle fleet.
        Calculates internal/external energy, costs, and station utilization,
        including investment and ROI.
        """
        MIN_INTERVALLO_RICARICA_SIM = 0.5  # 30 minuti between charges on the same station

        colonnine_instances = []
        power_map = {
            'ac_11': 11, 'ac_22': 22, 'dc_30': 30, 'dc_60': 60, 'dc_90': 90,
            'dc_20': COLONNINE_TAB1.get('DC_20', {}).get('potenza_effettiva', 20),
            'dc_40': COLONNINE_TAB1.get('DC_40', {}).get('potenza_effettiva', 40),
        }

        for tipo, quantita in colonnine_config.items():
            potenza = power_map.get(tipo, 11)
            for i in range(quantita):
                colonnine_instances.append({
                    'tipo': tipo,
                    'nome': f"{tipo}_{i+1}",
                    'potenza': potenza,
                    'available_slots': [(0.0, float(ore_disponibili))], # List of (start, end) free intervals
                    'bookings': [] # Actual bookings made
                })

        risultati = {
            'energia_totale': 0,
            'energia_caricata': 0,
            'energia_esterna': 0,
            'tempo_esterno_stimato': 0,
            'costo_ricariche_esterne': 0,
            'utilizzo_colonnine_ore': defaultdict(float),
            'prenotazioni': [],
            'auto_caricate_completamente': 0,
            'num_veicoli_totali': len(veicoli),
            'costo_operativo_interno': 0,
            'investimento_totale_iniziale': 0,
            'risparmio_annuo_stimato': 0,
            'ROI': 0
        }

        veicoli_for_sim = [v.copy() for v in veicoli]
        for v in veicoli_for_sim:
            v['energia_rimanente'] = v['energia_richiesta']
            v['caricata_completamente'] = False
            # For simplicity in Tab2, assume vehicle is available from 0.0 to its 'sosta' duration
            v['sosta_start'] = 0.0
            v['sosta_end'] = v['sosta_start'] + v['sosta']

        # Sort vehicles by their departure time (earliest departure first)
        veicoli_for_sim.sort(key=lambda x: x['sosta_end'])

        # Simulation loop: try to assign charges until no more can be assigned
        # Limit iterations to prevent infinite loops
        max_sim_iterations = len(veicoli_for_sim) * len(colonnine_instances) * 24 # A generous upper bound

        for _ in range(max_sim_iterations):
            something_charged_in_this_iteration = False
            
            # Get vehicles that still need charging, sorted by urgency (earliest departure, most energy needed)
            vehicles_needing_charge = sorted(
                [v for v in veicoli_for_sim if v['energia_rimanente'] > 0],
                key=lambda x: (x['sosta_end'], -x['energia_rimanente'])
            )

            if not vehicles_needing_charge:
                break # All vehicles are charged

            for vehicle in vehicles_needing_charge:
                if vehicle['energia_rimanente'] <= 0:
                    continue # Already fully charged

                best_option = None # (colonnina_instance, charge_start, charge_end, energy_to_charge)

                # Iterate through all colonnines and their available slots to find the best fit
                for colonnina in colonnine_instances:
                    for slot_idx, (slot_start, slot_end) in enumerate(colonnina['available_slots']):
                        # Calculate the intersection of vehicle's available time and colonnina's available slot
                        effective_charge_start = max(vehicle['sosta_start'], slot_start)
                        effective_charge_end = min(vehicle['sosta_end'], slot_end)

                        # Account for minimum interval if there's a previous booking on this station
                        if colonnina['bookings']:
                            last_booking_end = max(b['fine'] for b in colonnina['bookings'])
                            effective_charge_start = max(effective_charge_start, last_booking_end + MIN_INTERVALLO_RICARICA_SIM)

                        if effective_charge_end - effective_charge_start >= MIN_DURATA_RICARICA:
                            potential_duration = effective_charge_end - effective_charge_start
                            energy_possible_in_slot = colonnina['potenza'] * potential_duration
                            
                            energy_to_attempt = min(vehicle['energia_rimanente'], energy_possible_in_slot)

                            if energy_to_attempt > 0:
                                # Prioritize options that charge more energy, or use higher power stations
                                if not best_option or energy_to_attempt > best_option[3]:
                                    best_option = (colonnina, effective_charge_start, effective_charge_end, energy_to_attempt)

                if best_option:
                    colonnina_to_use, charge_start, charge_end, energy_to_charge = best_option
                    
                    # Calculate actual duration needed for the charged energy
                    actual_duration_needed = energy_to_charge / colonnina_to_use['potenza']
                    
                    # Ensure final duration respects minimum charge duration and slot limits
                    final_charge_duration = max(MIN_DURATA_RICARICA, actual_duration_needed)
                    final_charge_duration = min(final_charge_duration, charge_end - charge_start)

                    # If the vehicle needs very little energy to finish, allow a shorter charge
                    if vehicle['energia_rimanente'] <= colonnina_to_use['potenza'] * MIN_DURATA_RICARICA:
                        final_charge_duration = min(final_charge_duration, vehicle['energia_rimanente'] / colonnina_to_use['potenza'])
                        if final_charge_duration < 0.01: # Avoid negligible charges
                            continue

                    if final_charge_duration > 0.01: # Ensure a meaningful charge
                        actual_energy_charged = colonnina_to_use['potenza'] * final_charge_duration
                        vehicle['energia_rimanente'] -= actual_energy_charged
                        something_charged_in_this_iteration = True

                        # Update the colonnina's available slots
                        new_slots_for_colonnina = []
                        for s_idx, (s_start, s_end) in enumerate(colonnina_to_use['available_slots']):
                            if s_start < charge_start + final_charge_duration + MIN_INTERVALLO_RICARICA_SIM and s_end > charge_start - MIN_INTERVALLO_RICARICA_SIM:
                                # This slot overlaps with the new booking. Split it.
                                if s_start < charge_start:
                                    new_slots_for_colonnina.append((s_start, charge_start))
                                if s_end > charge_start + final_charge_duration + MIN_INTERVALLO_RICARICA_SIM:
                                    new_slots_for_colonnina.append((charge_start + final_charge_duration + MIN_INTERVALLO_RICARICA_SIM, s_end))
                            else:
                                new_slots_for_colonnina.append((s_start, s_end))
                        colonnina_to_use['available_slots'] = sorted(new_slots_for_colonnina, key=lambda x: x[0])

                        # Record the booking
                        colonnina_to_use['bookings'].append({
                            'veicolo': vehicle['nome'],
                            'inizio': charge_start,
                            'fine': charge_start + final_charge_duration,
                            'energia': actual_energy_charged,
                            'tempo_ricarica': final_charge_duration
                        })
                        colonnina_to_use['bookings'].sort(key=lambda x: x['inizio'])

                        risultati['utilizzo_colonnine_ore'][f"{colonnina_to_use['potenza']} kW"] += final_charge_duration
                        risultati['prenotazioni'].append({
                            'veicolo': vehicle['nome'],
                            'colonnina': colonnina_to_use['nome'],
                            'inizio': charge_start,
                            'fine': charge_start + final_charge_duration,
                            'energia': actual_energy_charged,
                            'tipo_colonnina': colonnina_to_use['tipo']
                        })
                        break # Move to the next vehicle after assigning a charge

            if not something_charged_in_this_iteration:
                break # No more charges could be assigned

        # Final aggregation for results
        risultati['energia_totale'] = sum(v['energia_richiesta'] for v in veicoli_for_sim)
        risultati['energia_caricata'] = sum(sum(b['energia'] for b in col['bookings']) for col in colonnine_instances)
        risultati['energia_esterna'] = risultati['energia_totale'] - risultati['energia_caricata']
        
        risultati['auto_caricate_completamente'] = sum(1 for v in veicoli_for_sim if v['energia_rimanente'] <= 0.01) # Add tolerance

        if risultati['energia_esterna'] > 0:
            risultati['tempo_esterno_stimato'] = (risultati['energia_esterna'] / 11) * 1.5 # Simplified assumption for external time
            risultati['costo_ricariche_esterne'] = risultati['energia_esterna'] * prezzo_energia_pubblica

        total_colonnine_capacity_kwh = sum(col['potenza'] * ore_disponibili for col in colonnine_instances)
        if total_colonnine_capacity_kwh > 0:
            risultati['tasso_utilizzo'] = (risultati['energia_caricata'] / total_colonnine_capacity_kwh) * 100
        else:
            risultati['tasso_utilizzo'] = 0

        risultati['costo_operativo_interno'] = risultati['energia_caricata'] * costo_energia_interna
        
        costo_totale_esterno_se_nessuna_colonnina = risultati['energia_totale'] * prezzo_energia_pubblica
        risparmio_giornaliero = costo_totale_esterno_se_nessuna_colonnina - risultati['costo_ricariche_esterne'] - risultati['costo_operativo_interno']
        risultati['risparmio_annuo_stimato'] = risparmio_giornaliero * 365

        # Calculate total initial investment for Tab 2
        total_investment_tab2 = 0
        for tipo, quantita in colonnine_config.items():
            total_investment_tab2 += quantita * costi_investimento_colonnine.get(tipo, 0)
        risultati['investimento_totale_iniziale'] = total_investment_tab2

        if risultati['investimento_totale_iniziale'] > 0:
            risultati['ROI'] = (risultati['risparmio_annuo_stimato'] / risultati['investimento_totale_iniziale']) * 100
        else:
            risultati['ROI'] = 0
        
        # Add the simulated vehicle data to the results
        risultati['veicoli_simulati'] = veicoli_for_sim

        return risultati

    # Tab 2 User Interface
    with st.expander(get_text("test_params_vehicle_fleet"), expanded=True):
        n_auto_tab2 = st.slider(get_text("num_ev_vehicles"), 0, 100, 5, key="tab2_num_auto",
                                 help=get_text("num_ev_vehicles_help"))
        veicoli_tab2 = []

        cols_tab2_veicoli = st.columns(3)
        for i in range(n_auto_tab2):
            with cols_tab2_veicoli[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{get_text('single_vehicle_test').format(i=i+1)}**")
                    nome = st.text_input(get_text("vehicle_name").format(i=''), f"Auto_{i+1}", key=f"tab2_nome_{i}")
                    km = st.slider(get_text("daily_km_test"), 0, 500, 100, step=10, key=f"tab2_km_{i}",
                                     help=get_text("daily_km_test_help"))
                    consumo = st.slider(get_text("avg_consumption_test"), 10, 30, 18, step=1, key=f"tab2_cons_{i}",
                                         help=get_text("avg_consumption_test_help"))
                    sosta = st.slider(get_text("available_stop_hours_test"), 0, 8, 4, step=1, key=f"tab2_sosta_{i}",
                                      help=get_text("available_stop_hours_test_help"))

                    consumo_kwh_km = consumo / 100
                    energia_richiesta = km * consumo_kwh_km

                    veicoli_tab2.append({
                        "nome": nome,
                        "km": km,
                        "consumo": consumo_kwh_km,
                        "sosta": sosta,
                        "energia_richiesta": energia_richiesta
                    })

    with st.expander(get_text("existing_infra_config"), expanded=True):
        st.markdown(get_text("existing_infra_intro"))
        cols_infra = st.columns(3)
        with cols_infra[0]:
            ac_11_tab2 = st.number_input(get_text("ac_11_chargers"), 0, 20, 1, key="tab2_ac11", help=get_text("ac_11_chargers_help"))
            ac_22_tab2 = st.number_input(get_text("ac_22_chargers"), 0, 20, 0, key="tab2_ac22", help=get_text("ac_22_chargers_help"))
        with cols_infra[1]:
            dc_30_tab2 = st.number_input(get_text("dc_30_chargers"), 0, 10, 0, key="tab2_dc30", help=get_text("dc_30_chargers_help"))
            dc_60_tab2 = st.number_input(get_text("dc_60_chargers"), 0, 10, 0, key="tab2_dc60", help=get_text("dc_60_chargers_help"))
        with cols_infra[2]:
            dc_90_tab2 = st.number_input(get_text("dc_90_chargers"), 0, 10, 0, key="tab2_dc90", help=get_text("dc_90_chargers_help"))
        ore_disponibili_tab2 = st.slider(get_text("daily_charger_hours"), 1, 24, 8, step=1, key="tab2_ore",
                                         help=get_text("daily_charger_hours_help"))

    with st.expander(get_text("economic_investment_params"), expanded=False):
        st.markdown(get_text("economic_investment_intro"))

        costo_energia_interna_tab2 = st.slider(get_text("internal_energy_cost_test"), 0.10, 1.00, 0.25, step=0.05, key="tab2_costo_interno",
                                               help=get_text("internal_energy_cost_test_help"))
        prezzo_energia_pubblica_tab2 = st.slider(get_text("external_energy_price_test"), 0.10, 1.00, 0.80, step=0.05, key="tab2_prezzo_esterno",
                                                help=get_text("external_energy_price_test_help"))

        st.markdown("---")
        st.markdown(f"**{get_text('charger_purchase_costs')}**")
        col1_inv, col2_inv, col3_inv = st.columns(3)
        with col1_inv:
            inv_ac11 = st.number_input(get_text("investment_ac11"), 500, 5000, 1500, step=100, key="tab2_inv_ac11", help=get_text("investment_ac11_help"))
            inv_ac22 = st.number_input(get_text("investment_ac22"), 1000, 8000, 2500, step=100, key="tab2_inv_ac22", help=get_text("investment_ac22_help"))
        with col2_inv:
            inv_dc30 = st.number_input(get_text("investment_dc30"), 5000, 20000, 10000, step=500, key="tab2_inv_dc30", help=get_text("investment_dc30_help"))
            inv_dc60 = st.number_input(get_text("investment_dc60"), 10000, 40000, 20000, step=1000, key="tab2_inv_dc60", help=get_text("investment_dc60_help"))
        with col3_inv:
            inv_dc90 = st.number_input(get_text("investment_dc90"), 15000, 60000, 30000, step=1000, key="tab2_inv_dc90", help=get_text("investment_dc90_help"))

        costi_investimento_colonnine = {
            'ac_11': inv_ac11,
            'ac_22': inv_ac22,
            'dc_30': inv_dc30,
            'dc_60': inv_dc60,
            'dc_90': inv_dc90,
        }

    if st.button(get_text("run_infra_analysis"), key="tab2_analisi", type="primary"):
        if not veicoli_tab2:
            st.warning(get_text("add_vehicle_warning_analysis"))
        else:
            with st.spinner(get_text("analysis_execution")):
                risultati_tab2_temp = calculate_infrastructure_test(
                    veicoli_tab2,
                    {'ac_11': ac_11_tab2, 'ac_22': ac_22_tab2, 'dc_30': dc_30_tab2, 'dc_60': dc_60_tab2, 'dc_90': dc_90_tab2},
                    costo_energia_interna_tab2,
                    prezzo_energia_pubblica_tab2,
                    ore_disponibili_tab2,
                    costi_investimento_colonnine
                )
                st.session_state.risultati_tab2 = risultati_tab2_temp # Store results in session state

            st.success(get_text("analysis_complete_success"))
            st.divider()
            st.subheader(get_text("performance_summary"))

            # Use results from session state
            risultati_tab2 = st.session_state.risultati_tab2

            col1_tab2, col2_tab2, col3_tab2 = st.columns(3)
            col1_tab2.metric(get_text("total_energy_requested"), f"{risultati_tab2['energia_totale']:.1f} kWh",
                             help=get_text("total_energy_requested_help"))
            col2_tab2.metric(get_text("internal_energy_charged_test"), f"{risultati_tab2['energia_caricata']:.1f} kWh",
                            f"{(risultati_tab2['energia_caricata']/risultati_tab2['energia_totale']*100 if risultati_tab2['energia_totale']>0 else 0):.1f}%",
                            help=get_text("internal_energy_charged_test_help"))
            col3_tab2.metric(get_text("external_energy_to_charge"), f"{risultati_tab2['energia_esterna']:.1f} kWh",
                            f"{(risultati_tab2['energia_esterna']/risultati_tab2['energia_totale']*100 if risultati_tab2['energia_totale']>0 else 0):.1f}%",
                            help=get_text("external_energy_to_charge_help"))

            col4_tab2, col5_tab2, col6_tab2 = st.columns(3)
            col4_tab2.metric(get_text("estimated_time_lost"), f"{risultati_tab2['tempo_esterno_stimato']:.1f} h/{get_text('day_label')}", # New key
                             help=get_text("estimated_time_lost_help"))
            col5_tab2.metric(get_text("daily_external_charge_cost"), f"€{risultati_tab2['costo_ricariche_esterne']:.2f}",
                             help=get_text("daily_external_charge_cost_help"))
            col6_tab2.metric(get_text("avg_charger_utilization_rate"), f"{risultati_tab2['tasso_utilizzo']:.1f}%",
                             help=get_text("avg_charger_utilization_rate_help"))

            col7_tab2, col8_tab2, col9_tab2 = st.columns(3)
            col7_tab2.metric(get_text("fully_charged_cars"), f"{risultati_tab2['auto_caricate_completamente']}/{risultati_tab2['num_veicoli_totali']}",
                             help=get_text("fully_charged_cars_help"))
            col8_tab2.metric(get_text("internal_operating_cost"), f"€{risultati_tab2['costo_operativo_interno']:.2f}/{get_text('day_label')}", # New key
                             help=get_text("internal_operating_cost_help"))
            # col9_tab2 is intentionally left blank for alignment or future use
            col_roi_1, col_roi_2 = st.columns(2)
            col_roi_1.metric(get_text("estimated_annual_savings_test"), f"€{risultati_tab2['risparmio_annuo_stimato']:.2f}",
                             help=get_text("estimated_annual_savings_test_help"))
            col_roi_2.metric(get_text("roi_test"), f"{risultati_tab2['ROI']:.1f}%",
                             help=get_text("roi_test_help"))


            tab2_1, tab2_2, tab2_3, tab2_4 = st.tabs([get_text("charger_utilization_details"), get_text("vehicle_charge_status_test"), get_text("energy_req_vs_charged_test"), get_text("operating_costs_analysis_test")])

            with tab2_1:
                st.markdown(get_text("hourly_utilization_details"))
                if risultati_tab2['utilizzo_colonnine_ore']:
                    df_utilizzo = pd.DataFrame({
                        "ChargerType": list(risultati_tab2['utilizzo_colonnine_ore'].keys()), # Fixed internal column name
                        "HoursUsed": list(risultati_tab2['utilizzo_colonnine_ore'].values()) # Fixed internal column name
                    })
                    fig = px.bar(df_utilizzo, x="ChargerType", y="HoursUsed", # Use fixed column names
                                 title=get_text("hourly_utilization_chart_title"),
                                 color="ChargerType",
                                 color_discrete_sequence=px.colors.qualitative.Dark24, # Use a different color sequence
                                 template="plotly_white")
                    fig.update_xaxes(title_text=get_text("charger_type_label")) # Apply translated label
                    fig.update_yaxes(title_text=get_text("hours_used_label")) # Apply translated label
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(get_text("no_chargers_configured_analysis"))
                
                st.markdown(f"##### {get_text('gantt_planning_details')}")
                st.markdown(get_text("gantt_planning_intro"))
                if risultati_tab2['prenotazioni']:
                    df_prenotazioni = pd.DataFrame(risultati_tab2['prenotazioni'])
                    # Adjust 'inizio' and 'fine' to be datetime objects for plotly.timeline
                    df_prenotazioni['StartTime'] = df_prenotazioni['inizio'].apply(lambda h: datetime(2023,1,1) + timedelta(hours=h)) # Fixed internal column name
                    df_prenotazioni['EndTime'] = df_prenotazioni['fine'].apply(lambda h: datetime(2023,1,1) + timedelta(hours=h)) # Fixed internal column name

                    # Map types for consistent coloring with Tab1, or define new colors if not directly mapped
                    tab2_color_map = {
                        'ac_11': '#808080', 'ac_22': '#666666',
                        'dc_30': '#0000FF', 'dc_60': '#FF4500', 'dc_90': '#FF0000',
                        'dc_20': '#00FF00', 'dc_40': '#FFA500' # Assuming these are used for new types
                    }
                    # Fallback to general colors if type not explicitly in map
                    df_prenotazioni['Color'] = df_prenotazioni['tipo_colonnina'].map(tab2_color_map).fillna('#CCCCCC') # Fixed internal column name

                    fig = px.timeline(
                        df_prenotazioni,
                        x_start="StartTime", # Use fixed column name
                        x_end="EndTime", # Use fixed column name
                        y="colonnina", # This is an internal name, should be fine
                        color="tipo_colonnina", # Use colonnina type for color coding
                        title=get_text("gantt_chart_title"),
                        hover_name="veicolo", # This is also an internal name, should be fine
                        hover_data={
                            "StartTime": False, "EndTime": False, "tipo_colonnina": False,
                            "colonnina": True, "veicolo": True, "energia": ':.1f kWh' # These are internal, should be fine
                        },
                        color_discrete_map=tab2_color_map, # Apply the color map
                        template="plotly_white"
                    )
                    fig.update_yaxes(title_text=get_text("charger"))
                    fig.update_xaxes(title_text=get_text("hour_of_day"), tickformat="%H:%M")
                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        df_prenotazioni[["veicolo", "colonnina", 'inizio', 'fine', 'energia']], # Use internal names
                        column_config={
                            "veicolo": st.column_config.Column(get_text("vehicle_label")),
                            "colonnina": st.column_config.Column(get_text("charger")),
                            "inizio": st.column_config.NumberColumn(get_text("start_time_label"), format="%.1f h"), # Format as hours
                            "fine": st.column_config.NumberColumn(get_text("end_time_label"), format="%.1f h"), # Format as hours
                            "energia": st.column_config.NumberColumn(get_text("energy_kwh_label"), format="%.1f kWh")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info(get_text("no_charges_recorded"))

            with tab2_2:
                st.markdown(f"#### {get_text('vehicle_charge_status_test')}")
                # Use veicoli_simulati from results_tab2
                if st.session_state.risultati_tab2 and 'veicoli_simulati' in st.session_state.risultati_tab2:
                    charged_count_tab2 = sum(1 for v in st.session_state.risultati_tab2['veicoli_simulati'] if v['energia_richiesta'] - v['energia_rimanente'] >= v['energia_richiesta'] * 0.99) # Fully charged
                    partial_count_tab2 = sum(1 for v in st.session_state.risultati_tab2['veicoli_simulati'] if v['energia_richiesta'] - v['energia_rimanente'] > 0 and v['energia_richiesta'] - v['energia_rimanente'] < v['energia_richiesta'] * 0.99) # Partially charged
                    unassigned_count_tab2 = sum(1 for v in st.session_state.risultati_tab2['veicoli_simulati'] if v['energia_richiesta'] - v['energia_rimanente'] <= 0.01) # Not charged (or negligible)

                    df_charge_status_tab2 = pd.DataFrame({
                        "ChargeStatus": [get_text("fully_charged"), get_text("partially_charged"), get_text("not_charged")], # Fixed internal column name
                        "NumVehicles": [charged_count_tab2, partial_count_tab2, unassigned_count_tab2] # Fixed internal column name
                    })
                    fig_charge_status_pie_tab2 = px.pie(df_charge_status_tab2, values="NumVehicles", names="ChargeStatus", # Use fixed column names
                                                    title=get_text("vehicle_charge_status_chart_title"),
                                                    color_discrete_sequence=px.colors.qualitative.Set2,
                                                    template="plotly_white")
                    st.plotly_chart(fig_charge_status_pie_tab2, use_container_width=True)
                else:
                    st.info(get_text("run_analysis_to_view_status"))


            with tab2_3:
                st.markdown(f"#### {get_text('energy_req_vs_charged_test')}")
                # Use veicoli_simulati from results_tab2
                if st.session_state.risultati_tab2 and 'veicoli_simulati' in st.session_state.risultati_tab2:
                    df_veicoli_charged_tab2 = pd.DataFrame([
                        {
                            "Vehicle": v["nome"], # Fixed internal column name
                            "EnergyRequested": v["energia_richiesta"], # Fixed internal column name
                            "InternalEnergy": v["energia_richiesta"] - v["energia_rimanente"] # Fixed internal column name
                        } for v in st.session_state.risultati_tab2['veicoli_simulati']
                    ])
                    df_veicoli_charged_tab2 = df_veicoli_charged_tab2.sort_values(by="EnergyRequested", ascending=False).head(10) # Use fixed column name

                    if not df_veicoli_charged_tab2.empty:
                        fig_energy_comparison_tab2 = px.bar(df_veicoli_charged_tab2, x="Vehicle", y=["EnergyRequested", "InternalEnergy"], # Use fixed column names
                                                        barmode='group',
                                                        title=get_text("energy_comparison_chart_title"),
                                                        template="plotly_white")
                        fig_energy_comparison_tab2.update_xaxes(title_text=get_text("vehicle_label")) # Apply translated label
                        fig_energy_comparison_tab2.update_yaxes(title_text=get_text("energy_kwh_label")) # Apply translated label
                        st.plotly_chart(fig_energy_comparison_tab2, use_container_width=True)
                    else:
                        st.info(get_text("no_vehicle_data_for_chart"))
                else:
                    st.info(get_text("run_analysis_to_view_comparison"))


            with tab2_4:
                st.markdown(f"#### {get_text('operating_costs_analysis_test')}")
                if st.session_state.risultati_tab2:
                    df_cost_breakdown_tab2 = pd.DataFrame({
                        "Type": [get_text("internal_operating_cost"), get_text("daily_external_charge_cost")], # Fixed internal column name
                        "Cost": [st.session_state.risultati_tab2['costo_operativo_interno'], st.session_state.risultati_tab2['costo_ricariche_esterne']] # Fixed internal column name
                    })
                    fig_cost_breakdown_tab2 = px.pie(df_cost_breakdown_tab2, values="Cost", names="Type", # Use fixed column names
                                                    title=get_text("operating_costs_distribution_chart_title"),
                                                    color_discrete_sequence=px.colors.qualitative.Pastel,
                                                    template="plotly_white")
                    st.plotly_chart(fig_cost_breakdown_tab2, use_container_width=True)
                else:
                    st.info(get_text("run_analysis_to_view_costs"))

            with st.expander(get_text("optimization_suggestions"), expanded=True):
                if st.session_state.risultati_tab2:
                    risultati_tab2 = st.session_state.risultati_tab2 # Re-assign for convenience
                    if risultati_tab2['energia_esterna'] > 0:
                        st.warning(get_text("improvement_opportunity").format(energy=risultati_tab2['energia_esterna']))

                    if risultati_tab2['auto_caricate_completamente'] < risultati_tab2['num_veicoli_totali']:
                        st.warning(get_text("fleet_coverage").format(charged=risultati_tab2['auto_caricate_completamente'], total=risultati_tab2['num_veicoli_totali']))

                    if risultati_tab2['tasso_utilizzo'] > 80: # Adjusted threshold for warning
                        st.warning(get_text("high_utilization_warning").format(utilization=risultati_tab2['tasso_utilizzo']))
                    elif risultati_tab2['tasso_utilizzo'] < 40: # Adjusted threshold for info
                        st.info(get_text("low_utilization_info").format(utilization=risultati_tab2['tasso_utilizzo']))
                    else:
                        st.success(get_text("well_balanced_utilization"))

                    if risultati_tab2['investimento_totale_iniziale'] > 0: # Show ROI suggestions only if there's an investment
                        if risultati_tab2['ROI'] > 15: # Example threshold for a good ROI
                            st.success(get_text("good_roi_success").format(roi=risultati_tab2['ROI']))
                        elif risultati_tab2['ROI'] > 0:
                            st.info(get_text("positive_roi_info").format(roi=risultati_tab2['ROI']))
                        else:
                            st.error(get_text("negative_roi_error").format(roi=risultati_tab2['ROI']))
                    else:
                        st.info(get_text("roi_not_calculable"))
                else:
                    st.info(get_text("run_analysis_to_view_suggestions"))
    else:
        st.info(get_text("configure_and_calculate"))

# =============================================================================
# 3. PERFORMANCE EVALUATION (VALUTAZIONE RENDIMENTO)
# =============================================================================
with tab3:
    st.header(get_text("performance_eval_header"))
    st.markdown(get_text("performance_eval_intro"))

    GIORNI_ANNUI_TAB3 = 260 # Default value, user can change

    # Initialize session state for results of tab3 to avoid KeyError on initial load
    if 'risultati_tab3' not in st.session_state:
        st.session_state.risultati_tab3 = None

    def calculate_charging_point_performance(params):
        """
        Calculates the estimated performance and ROI of a charging point.
        """
        potenza_totale_kw = (
            params['ac_22'] * 22 + params['dc_20'] * 20 + params['dc_30'] * 30 +
            params['dc_40'] * 40 + params['dc_60'] * 60 + params['dc_90'] * 90
        )

        energia_massima_giorno = potenza_totale_kw * params['ore_disponibili'] * (params['utilizzo_percentuale'] / 100)
        energia_richiesta_totale_giorno = params['num_auto_giorno'] * params['kwh_per_auto']
        energia_erogata_giorno = min(energia_massima_giorno, energia_richiesta_totale_giorno)
        energia_erogata_annuo = energia_erogata_giorno * params['giorni_attivi']

        auto_servite = int(energia_erogata_giorno // params['kwh_per_auto'])
        auto_non_servite = max(0, params['num_auto_giorno'] - auto_servite)
        guadagno_annuo = energia_erogata_annuo * params['prezzo_vendita']

        # Costs as per original tab3 logic (different from tab1 definitions)
        costo_colonnine = (
            params['ac_22'] * 1000 + params['dc_20'] * 8000 + params['dc_30'] * 12000 +
            params['dc_40'] * 15000 + params['dc_60'] * 18000 + params['dc_90'] * 25000
        )
        costo_installazione = potenza_totale_kw * 150 # Assuming 150€/kW for installation
        costo_totale_investimento = costo_colonnine + costo_installazione # Renamed for clarity

        # New: Calculate total operational costs
        costo_operativo_energia_annuo = energia_erogata_annuo * params['costo_acquisto_energia_kwh']
        
        costo_ammortamento_annuo = costo_totale_investimento / params['vita_utile_anni'] if params['vita_utile_anni'] > 0 else costo_totale_investimento

        costo_operativo_totale_annuo = (
            costo_operativo_energia_annuo +
            params['costo_manutenzione_annuale'] +
            params['costo_software_annuale'] +
            params['costo_assicurazione_annuale'] +
            params['costo_terreno_annuale'] +
            costo_ammortamento_annuo
        )

        profitto_netto_annuo = guadagno_annuo - costo_operativo_totale_annuo
        
        # ROI calculation remains the same, but now profit_netto_annuo is used for payback period
        ROI = (profitto_netto_annuo / costo_totale_investimento) * 100 if costo_totale_investimento > 0 else 0
        payback_period = costo_totale_investimento / profitto_netto_annuo if profitto_netto_annuo > 0 else float('inf')

        tasso_utilizzo_effettivo = (energia_erogata_giorno / energia_massima_giorno) * 100 if energia_massima_giorno > 0 else 0

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
            'tasso_utilizzo': tasso_utilizzo_effettivo
        }

    st.subheader(get_text("charging_point_usage_params"))

    with st.expander(get_text("base_usage_params"), expanded=True):
        num_auto_giorno_tab3 = st.slider(get_text("expected_daily_cars"), 1, 1000, 50, step=5, key="tab3_num_auto",
                                         help=get_text("expected_daily_cars_help"))
        kwh_per_auto_tab3 = st.slider(get_text("avg_energy_per_car"), 5, 100, 30, step=5, key="tab3_kwh_auto",
                                       help=get_text("avg_energy_per_car_help"))
        tempo_ricarica_media_tab3 = st.slider(get_text("avg_charge_time"), 0.5, 12.0, 2.0, step=0.5, key="tab3_tempo_ric",
                                               help=get_text("avg_charge_time_help"))

    with st.expander(get_text("operational_time_config"), expanded=False):
        ore_disponibili_tab3 = st.slider(get_text("daily_op_hours"), 1, 24, 8, step=1, key="tab3_ore_op",
                                         help=get_text("daily_op_hours_help"))
        giorni_attivi_tab3 = st.slider(get_text("annual_op_days"), 1, 365, GIORNI_ANNUI_TAB3, step=5, key="tab3_giorni_op",
                                       help=get_text("annual_op_days_help"))

    with st.expander(get_text("economic_utilization_params"), expanded=False):
        prezzo_vendita_tab3 = st.slider(get_text("energy_sale_price"), 0.10, 1.00, 0.25, step=0.05, key="tab3_prezzo",
                                         help=get_text("energy_sale_price_help"))
        costo_acquisto_energia_kwh_tab3 = st.slider(get_text("energy_purchase_cost"), 0.05, 0.50, 0.15, step=0.01, key="tab3_costo_acquisto_energia",
                                                    help=get_text("energy_purchase_cost_help"))
        
        utilizzo_percentuale_tab3 = st.slider(get_text("infra_utilization_prob"), 10, 100, 85, step=5, key="tab3_utilizzo",
                                               help=get_text("infra_utilization_prob_help"))
        budget_tab3 = st.number_input(get_text("max_initial_investment"), 0, 500000, 20000, step=1000, key="tab3_budget",
                                       help=get_text("max_initial_investment_help"))

        st.markdown("---")
        st.subheader(get_text("additional_annual_op_costs"))
        costo_manutenzione_annuale_tab3 = st.number_input(get_text("annual_charger_maintenance_cost"), 0, 50000, 5000, step=100, key="tab3_manutenzione_annuale",
                                                        help=get_text("annual_charger_maintenance_cost_help"))
        costo_software_annuale_tab3 = st.number_input(get_text("annual_software_cost"), 0, 20000, 1000, step=100, key="tab3_software_annuale",
                                                      help=get_text("annual_software_cost_help"))
        costo_assicurazione_annuale_tab3 = st.number_input(get_text("annual_insurance_cost"), 0, 10000, 500, step=50, key="tab3_assicurazione_annuale",
                                                           help=get_text("annual_insurance_cost_help"))
        costo_terreno_annuale_tab3 = st.number_input(get_text("annual_land_cost"), 0, 50000, 0, step=100, key="tab3_terreno_annuale",
                                                     help=get_text("annual_land_cost_help"))
        vita_utile_anni_tab3 = st.number_input(get_text("useful_life_years"), 1, 30, 10, step=1, key="tab3_vita_utile",
                                              help=get_text("useful_life_years_help"))


    st.subheader(get_text("charger_point_config"))
    with st.expander(get_text("select_quantify_chargers"), expanded=True):
        cols_chargers_tab3 = st.columns(3)
        with cols_chargers_tab3[0]:
            ac_22_tab3 = st.number_input(get_text("ac22_chargers_eval"), 0, 50, 2, key="tab3_ac22", help=get_text("ac22_chargers_eval_help"))
            dc_20_tab3 = st.number_input(get_text("dc20_chargers_eval"), 0, 20, 0, key="tab3_dc20", help=get_text("dc20_chargers_eval_help"))
        with cols_chargers_tab3[1]:
            dc_30_tab3 = st.number_input(get_text("dc30_chargers_eval"), 0, 20, 0, key="tab3_dc30", help=get_text("dc30_chargers_eval_help"))
            dc_40_tab3 = st.number_input(get_text("dc40_chargers_eval"), 0, 20, 0, key="tab3_dc40", help=get_text("dc40_chargers_eval_help"))
        with cols_chargers_tab3[2]:
            dc_60_tab3 = st.number_input(get_text("dc60_chargers_eval"), 0, 20, 0, key="tab3_dc60", help=get_text("dc60_chargers_eval_help"))
            dc_90_tab3 = st.number_input(get_text("dc90_chargers_eval"), 0, 20, 0, key="tab3_dc90", help=get_text("dc90_chargers_eval_help"))

    if st.button(get_text("calculate_point_performance"), key="tab3_calcola", type="primary"):
        params_tab3 = {
            'num_auto_giorno': num_auto_giorno_tab3,
            'kwh_per_auto': kwh_per_auto_tab3,
            'tempo_ricarica_media': tempo_ricarica_media_tab3,
            'ore_disponibili': ore_disponibili_tab3,
            'giorni_attivi': giorni_attivi_tab3,
            'prezzo_vendita': prezzo_vendita_tab3,
            'costo_acquisto_energia_kwh': costo_acquisto_energia_kwh_tab3, # Added
            'utilizzo_percentuale': utilizzo_percentuale_tab3,
            'budget': budget_tab3,
            'ac_22': ac_22_tab3,
            'dc_20': dc_20_tab3,
            'dc_30': dc_30_tab3,
            'dc_40': dc_40_tab3,
            'dc_60': dc_60_tab3,
            'dc_90': dc_90_tab3,
            'costo_manutenzione_annuale': costo_manutenzione_annuale_tab3, # Added
            'costo_software_annuale': costo_software_annuale_tab3, # Added
            'costo_assicurazione_annuale': costo_assicurazione_annuale_tab3, # Added
            'costo_terreno_annuale': costo_terreno_annuale_tab3, # Added
            'vita_utile_anni': vita_utile_anni_tab3 # Added
        }

        with st.spinner(get_text("calculate_performance_spinner")):
            risultati_tab3_temp = calculate_charging_point_performance(params_tab3)
            st.session_state.risultati_tab3 = risultati_tab3_temp # Store results in session state

        st.success(get_text("performance_analysis_complete"))
        st.divider()

        # Use results from session state
        risultati_tab3 = st.session_state.risultati_tab3

        st.subheader(get_text("charging_point_summary"))
        col1_tab3, col2_tab3, col3_tab3 = st.columns(3)
        col1_tab3.metric(get_text("total_installed_power"), f"{risultati_tab3['potenza_totale_kw']} kW",
                         help=get_text("total_installed_power_help"))
        col2_tab3.metric(get_text("estimated_annual_energy_delivered"), f"{risultati_tab3['energia_erogata_annuo']:,.0f} kWh",
                         help=get_text("estimated_annual_energy_delivered_help"))
        col3_tab3.metric(get_text("daily_cars_served"), f"{risultati_tab3['auto_servite']}/{num_auto_giorno_tab3}",
                         help=get_text("daily_cars_served_help"))

        st.subheader(get_text("key_economic_indicators"))
        col4_tab3, col5_tab3, col6_tab3 = st.columns(3)
        col4_tab3.metric(get_text("estimated_annual_revenue"), f"€{risultati_tab3['guadagno_annuo']:,.0f}",
                         help=get_text("estimated_annual_revenue_help"))
        col5_tab3.metric(get_text("total_system_cost_capex"), f"€{risultati_tab3['costo_totale_investimento']:,.0f}", # Changed label
                         get_text("within_budget") if risultati_tab3['entro_budget'] else get_text("over_budget"),
                         help=get_text("total_system_cost_capex_help"))
        col6_tab3.metric(get_text("annual_operating_cost_opex"), f"€{risultati_tab3['costo_operativo_totale_annuo']:,.0f}", # New metric
                         help=get_text("annual_operating_cost_opex_help"))

        st.divider()
        st.subheader(get_text("detailed_financial_analysis"))

        col_profit, col_roi, col_payback = st.columns(3) # Added a column for profit
        col_profit.metric(get_text("estimated_annual_net_profit"), f"€{risultati_tab3['profitto_netto_annuo']:,.0f}",
                          help=get_text("estimated_annual_net_profit_help"))
        col_roi.metric(get_text("roi_test"), f"{risultati_tab3['ROI']:.1f}%", # Changed format to .1f
                             help=get_text("roi_test_help"))
        col_payback.metric(get_text("payback_period"), f"{(risultati_tab3['payback_period'] if risultati_tab3['payback_period'] != float('inf') else get_text('infinite_payback')):.1f} {get_text('years_label')}", # Adjusted display for infinity, new key
                                 help=get_text("payback_period_help"))

        tab3_1, tab3_2, tab3_3, tab3_4 = st.tabs([get_text("detailed_visualization_tab"), get_text("financial_summary_tab"), get_text("payback_trend_tab"), get_text("investment_distribution_tab")])

        with tab3_1:
            st.markdown(f"#### {get_text('cars_served_vs_not_served')}")
            df_auto = pd.DataFrame({
                "Category": [get_text("served_cars"), get_text("not_served_cars")], # Fixed internal column name
                "Value": [risultati_tab3['auto_servite'], risultati_tab3['auto_non_servite']] # Fixed internal column name
            })
            fig = px.pie(df_auto, values="Value", names="Category", # Use fixed column names
                         title=get_text("cars_served_vs_not_served"),
                         color_discrete_sequence=px.colors.qualitative.Pastel,
                         template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"#### {get_text('estimated_monthly_energy_delivered')}")
            months = range(1, 13)
            # Introduce some seasonality to the monthly energy for a more realistic view
            monthly_energy = [risultati_tab3['energia_erogata_annuo'] / 12 * (1 + 0.1 * (i - 6)/6) for i in months] # Peak in summer, low in winter
            df_monthly = pd.DataFrame({
                "Month": months, # Fixed internal column name
                "EnergyKWh": monthly_energy # Fixed internal column name
            })
            fig = px.line(df_monthly, x="Month", y="EnergyKWh", title=get_text("estimated_monthly_energy_delivered"), # Use fixed column names
                          markers=True,
                          template="plotly_white")
            fig.update_xaxes(title_text=get_text("month_label")) # Apply translated label
            fig.update_yaxes(title_text=get_text("energy_kwh_label")) # Apply translated label
            st.plotly_chart(fig, use_container_width=True)

        with tab3_2:
            st.markdown(f"#### {get_text('annual_financial_summary')}")
            df_financial_summary = pd.DataFrame({
                "Category": [get_text("estimated_annual_revenue"), get_text("annual_operating_cost_opex"), get_text("estimated_annual_net_profit")], # Fixed internal column name
                "Value": [risultati_tab3['guadagno_annuo'], -risultati_tab3['costo_operativo_totale_annuo'], risultati_tab3['profitto_netto_annuo']], # Fixed internal column name
                "Type": [get_text("revenue_label"), get_text("cost_label_short"), get_text("profit_label_short")] # Fixed internal column name
            })
            # Use a waterfall chart for a clear financial overview
            fig_financial_summary = px.bar(df_financial_summary, x="Category", y="Value", # Use fixed column names
                                            color="Type", # Use fixed column name
                                            color_discrete_map={get_text("revenue_label"): "green", get_text("cost_label_short"): "red", get_text("profit_label_short"): "blue"},
                                            title=get_text("annual_financial_summary"),
                                            template="plotly_white")
            fig_financial_summary.update_xaxes(title_text=get_text("financial_summary_category_label")) # Apply translated label
            fig_financial_summary.update_yaxes(title_text=get_text("financial_summary_value_label")) # Apply translated label
            st.plotly_chart(fig_financial_summary, use_container_width=True)

        with tab3_3:
            st.markdown(f"#### {get_text('cumulative_net_profit_trend')}")
            if risultati_tab3['profitto_netto_annuo'] > 0 and risultati_tab3['payback_period'] != float('inf'):
                years = list(range(1, int(risultati_tab3['payback_period']) + 3)) # Show a few years beyond payback
                cumulative_profit = [risultati_tab3['profitto_netto_annuo'] * y for y in years]
                
                df_payback = pd.DataFrame({
                    "Year": years, # Fixed internal column name
                    "CumulativeNetProfit": cumulative_profit, # Fixed internal column name
                    "InitialInvestment": [risultati_tab3['costo_totale_investimento']] * len(years) # Fixed internal column name
                })

                fig_payback = px.line(df_payback, x="Year", y=["CumulativeNetProfit", "InitialInvestment"], # Use fixed column names
                                    title=get_text("cumulative_net_profit_trend"),
                                    markers=True,
                                    color_discrete_map={"CumulativeNetProfit": "green", "InitialInvestment": "red"}, # Use fixed internal names
                                    template="plotly_white")
                
                # Add vertical line for payback period
                if risultati_tab3['payback_period'] > 0:
                    fig_payback.add_vline(x=risultati_tab3['payback_period'], line_width=2, line_dash="dash", line_color="blue",
                                        annotation_text=get_text("payback_line").format(years=risultati_tab3['payback_period']),
                                        annotation_position="top right")
                fig_payback.update_xaxes(title_text=get_text("year_label")) # Apply translated label
                fig_payback.update_yaxes(title_text=get_text("cumulative_net_profit_label")) # Apply translated label
                st.plotly_chart(fig_payback, use_container_width=True)
            else:
                st.info(get_text("payback_not_calculable"))

        with tab3_4:
            st.markdown(f"#### {get_text('initial_investment_cost_distribution')}")
            # Corrected: Access potenza_totale_kw from risultati_tab3
            if risultati_tab3: # Ensure results are available
                df_investment_breakdown = pd.DataFrame({
                    "Component": [get_text("charger_cost_component"), get_text("installation_cost_component")], # Fixed internal column name
                    "Cost": [params_tab3['ac_22'] * 1000 + params_tab3['dc_20'] * 8000 + params_tab3['dc_30'] * 12000 +
                                  params_tab3['dc_40'] * 15000 + params_tab3['dc_60'] * 18000 + params_tab3['dc_90'] * 25000,
                                  risultati_tab3['potenza_totale_kw'] * 150] # Fixed internal column name
                })
                fig_investment_breakdown = px.pie(df_investment_breakdown, values="Cost", names="Component", # Use fixed column names
                                                title=get_text("initial_investment_cost_distribution"),
                                                color_discrete_sequence=px.colors.qualitative.Pastel,
                                                template="plotly_white")
                st.plotly_chart(fig_investment_breakdown, use_container_width=True)
            else:
                st.info(get_text("run_analysis_to_view_investment"))


        with st.expander(get_text("optimization_recommendations"), expanded=True):
            if st.session_state.risultati_tab3:
                risultati_tab3 = st.session_state.risultati_tab3 # Re-assign for convenience
                if risultati_tab3['tasso_utilizzo'] > 90:
                    st.warning(get_text("highly_utilized_infra"))
                    st.markdown(get_text("add_more_chargers_rec"))
                    st.markdown(get_text("increase_installed_power_rec"))
                    st.markdown(get_text("extend_op_hours_rec"))

                elif risultati_tab3['tasso_utilizzo'] < 50:
                    st.info(get_text("underutilized_infra"))
                    st.markdown(get_text("reduce_chargers_rec"))
                    st.markdown(get_text("attract_more_customers_rec"))
                    st.markdown(get_text("offer_promo_rates_rec"))

                if not risultati_tab3['entro_budget']:
                    st.error(get_text("investment_over_budget"))
                    st.markdown(get_text("review_charger_mix_rec"))
                    st.markdown(get_text("phase_investment_rec"))
                    st.markdown(get_text("seek_funding_rec"))

                if risultati_tab3['auto_non_servite'] > 0:
                    st.warning(get_text("cars_not_served_warning").format(count=risultati_tab3['auto_non_servite']))
                    st.markdown(get_text("increase_charger_power_rec"))
                    st.markdown(get_text("optimize_charge_times_rec"))
                    st.markdown(get_text("implement_booking_system_rec"))
                
                if risultati_tab3['profitto_netto_annuo'] <= 0: # New recommendation based on profit
                    st.error(get_text("negative_net_profit_warning"))
                    st.markdown(get_text("increase_sale_price_rec"))
                    st.markdown(get_text("reduce_op_costs_rec"))
                    st.markdown(get_text("increase_utilization_rec"))
                    st.markdown(get_text("review_initial_investment_rec"))
            else:
                st.info(get_text("run_analysis_to_view_recommendations"))
    else:
        st.info(get_text("configure_and_calculate_point"))


# Footer for the entire application
st.markdown("---")
st.markdown(f"""
<style>
.footer {{
    font-size: 12px;
    color: #666;
    text-align: center;
    padding: 10px;
}}
</style>
<div class="footer">
    {get_text("footer_text")}
</div>
""", unsafe_allow_html=True)
