import math

def calculate_charging_point_performance_improved(params):
    """
    Calcola il rendimento e il ROI di un punto di ricarica,
    integrando l'analisi della capacità di servizio (sessioni) e la capacità energetica.
    """
    
    # 1. PARAMETRI DI CONFIGURAZIONE E CAPEX
    
    # Calcolo Potenza Totale Installata (kW)
    potenza_totale_kw = (
        params['ac_22'] * 22 + params['dc_20'] * 20 + params['dc_30'] * 30 +
        params['dc_40'] * 40 + params['dc_60'] * 60 + params['dc_90'] * 90
    )
    
    # Costi di Investimento (CapEx)
    costo_colonnine = (
        params['ac_22'] * 1000 + params['dc_20'] * 8000 + params['dc_30'] * 12000 +
        params['dc_40'] * 15000 + params['dc_60'] * 18000 + params['dc_90'] * 25000
    )
    # Installazione (Assumendo 150€/kW)
    costo_installazione = potenza_totale_kw * 150
    costo_totale_investimento = costo_colonnine + costo_installazione

    # 2. CAPACITÀ OPERATIVA (I Colli di Bottiglia)
    
    # Capacità 1: Massima Energia erogabile (Limitata dalla Potenza Installata)
    # Questa è la tua logica iniziale, che tiene conto dell'efficienza/affidabilità
    energia_massima_capacita = (
        potenza_totale_kw * params['ore_disponibili'] * (params['utilizzo_percentuale'] / 100)
    )

    # Capacità 2: Massime Sessioni Servibili (Limitata dal Tempo di Occupazione)
    
    # Tempo totale in cui un posto è occupato (Ricarica + Spostamento/Turnover)
    tempo_totale_slot = params['tempo_ricarica_media'] + params['tempo_turnover']
    num_totale_colonnine = (
        params['ac_22'] + params['dc_20'] + params['dc_30'] + params['dc_40'] + 
        params['dc_60'] + params['dc_90']
    )
    
    if tempo_totale_slot > 0 and num_totale_colonnine > 0:
        # Numero max di sessioni possibili al giorno (capacità di servizio fisica)
        sessioni_massime_giorno = (num_totale_colonnine * params['ore_disponibili']) / tempo_totale_slot
        # Energia massima che si può erogare se si sfrutta il tempo massimo delle sessioni
        energia_massima_sessioni = sessioni_massime_giorno * params['kwh_per_auto']
    else:
        sessioni_massime_giorno = 0
        energia_massima_sessioni = 0

    # 3. ENERGIA EROGATA EFFETTIVA E METRICHE DI SERVIZIO

    # Domanda Totale richiesta dagli utenti
    energia_richiesta_totale_giorno = params['num_auto_giorno'] * params['kwh_per_auto']
    
    # L'energia erogata effettiva è il minimo tra la Domanda e le due Capacità Massime
    energia_erogata_giorno = min(
        energia_richiesta_totale_giorno, 
        energia_massima_capacita,
        energia_massima_sessioni
    )
    
    energia_erogata_annuo = energia_erogata_giorno * params['giorni_attivi']

    # Auto Servite (il numero intero di auto a cui è stata fornita l'energia richiesta)
    auto_servite = math.floor(energia_erogata_giorno / params['kwh_per_auto']) if params['kwh_per_auto'] > 0 else 0
    auto_non_servite = max(0, params['num_auto_giorno'] - auto_servite)

    # Tasso di Utilizzo (Plug/Sessione) - Quante sessioni effettive rispetto alle massime possibili
    tasso_utilizzo_plug = (auto_servite / sessioni_massime_giorno) * 100 if sessioni_massime_giorno > 0 else 0
    
    # Tasso di Utilizzo (Energetico) - Quanta energia effettiva rispetto alla massima teorica
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
    
    # Payback Period (anni)
    payback_period = costo_totale_investimento / profitto_netto_annuo if profitto_netto_annuo > 0 else float('inf')
    
    # Se il payback è maggiore della vita utile, forziamo 'infinito' per coerenza
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
        
        # Nuove metriche di Utilizzo per l'analisi
        'tasso_utilizzo_energetico': tasso_utilizzo_energetico,
        'tasso_utilizzo_plug': tasso_utilizzo_plug,
        
        # Dettaglio Costi per la visualizzazione OpEx/CapEx
        'costo_operativo_energia_annuo': costo_operativo_energia_annuo,
        'costo_ammortamento_annuo': costo_ammortamento_annuo,
        'costo_colonnine': costo_colonnine, 
        'costo_installazione': costo_installazione, 
    }
