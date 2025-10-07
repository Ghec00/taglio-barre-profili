import streamlit as st
import pandas as pd

st.title("Calcolo Taglio Profili 🔧")
st.write("Inserisci le misure delle aperture e ottieni il piano di taglio ottimale")

# Lunghezza barra standard
LUNGHEZZA_BARRA = 600  # 6 metri = 600 cm

# Input dati
st.subheader("Inserisci le Aperture")

num_aperture = st.number_input("Quante aperture devi realizzare?", min_value=1, max_value=50, value=1)

# Raccogli dati per ogni apertura
aperture_data = []
pezzi_necessari = []

for i in range(num_aperture):
    st.write(f"**Apertura {i+1}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        altezza_sx = st.number_input(f"Altezza SX (cm)", min_value=1, max_value=600, value=100, key=f"alt_sx_{i}")
    
    with col2:
        altezza_diversa = st.checkbox("Altezza DX diversa?", key=f"check_alt_{i}")
    
    if altezza_diversa:
        altezza_dx = st.number_input(f"Altezza DX (cm)", min_value=1, max_value=600, value=100, key=f"alt_dx_{i}")
    else:
        altezza_dx = altezza_sx
    
    col3, col4 = st.columns(2)
    
    with col3:
        larghezza_sotto = st.number_input(f"Larghezza sotto (cm)", min_value=1, max_value=600, value=100, key=f"lar_sotto_{i}")
    
    with col4:
        larghezza_doppia = st.checkbox("Larghezza sopra diversa?", key=f"check_lar_{i}")
    
    if larghezza_doppia:
        larghezza_sopra = st.number_input(f"Larghezza sopra (cm)", min_value=1, max_value=600, value=100, key=f"lar_sopra_{i}")
    else:
        larghezza_sopra = None
    
    aperture_data.append({
        'numero': i+1,
        'altezza_sx': altezza_sx,
        'altezza_dx': altezza_dx,
        'larghezza_sotto': larghezza_sotto,
        'larghezza_sopra': larghezza_sopra
    })
    
    # Aggiungi i pezzi necessari
    pezzi_necessari.append(('Altezza SX', f'Apertura {i+1}', altezza_sx))
    pezzi_necessari.append(('Altezza DX', f'Apertura {i+1}', altezza_dx))
    pezzi_necessari.append(('Larghezza sotto', f'Apertura {i+1}', larghezza_sotto))
    
    if larghezza_sopra:
        pezzi_necessari.append(('Larghezza sopra', f'Apertura {i+1}', larghezza_sopra))
    
    st.divider()

# Bottone calcolo
if st.button("Calcola Piano di Taglio Ottimale", type="primary"):
    with st.spinner("Ottimizzazione in corso..."):
        
        # Algoritmo First Fit Decreasing
        pezzi_ordinati = sorted(pezzi_necessari, key=lambda x: x[2], reverse=True)
        
        barre = []
        
        for pezzo in pezzi_ordinati:
            tipo, apertura, lunghezza = pezzo
            
            # Prova ad inserire in una barra esistente
            inserito = False
            for barra in barre:
                spazio_usato = sum([p[2] for p in barra['pezzi']])
                spazio_rimanente = LUNGHEZZA_BARRA - spazio_usato
                
                if lunghezza <= spazio_rimanente:
                    barra['pezzi'].append((tipo, apertura, lunghezza))
                    inserito = True
                    break
            
            # Se non entra in nessuna barra, crea una nuova barra
            if not inserito:
                barre.append({
                    'numero': len(barre) + 1,
                    'pezzi': [(tipo, apertura, lunghezza)]
                })
        
        # Mostra risultati
        st.success(f"✅ Calcolo completato!")
        
        st.subheader("Riepilogo")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Barre da 6m necessarie", len(barre))
        
        with col2:
            spreco_totale = sum([LUNGHEZZA_BARRA - sum([p[2] for p in b['pezzi']]) for b in barre])
            st.metric("Spreco totale (cm)", f"{spreco_totale:.0f}")
        
        with col3:
            percentuale_utilizzo = ((sum([sum([p[2] for p in b['pezzi']]) for b in barre]) / (len(barre) * LUNGHEZZA_BARRA)) * 100)
            st.metric("Utilizzo materiale", f"{percentuale_utilizzo:.1f}%")
        
        # Tabella dettagliata piano di taglio
        st.subheader("Piano di Taglio Dettagliato")
        
        piano_taglio_data = []
        for barra in barre:
            pezzi_str = []
            for pezzo in barra['pezzi']:
                tipo, apertura, lunghezza = pezzo
                pezzi_str.append(f"{tipo} {apertura} ({lunghezza}cm)")
            
            spreco = LUNGHEZZA_BARRA - sum([p[2] for p in barra['pezzi']])
            
            piano_taglio_data.append({
                'Barra #': barra['numero'],
                'Pezzi da tagliare': ' + '.join(pezzi_str),
                'Totale usato (cm)': sum([p[2] for p in barra['pezzi']]),
                'Spreco (cm)': spreco
            })
        
        df_piano = pd.DataFrame(piano_taglio_data)
        st.dataframe(df_piano, use_container_width=True)
        
        # Istruzioni per tua madre
        st.subheader("📋 Istruzioni di Taglio")
        st.info("Stampa questa pagina o segui le istruzioni barra per barra")
        
        for barra in barre:
            with st.expander(f"Barra #{barra['numero']} - Dettaglio"):
                st.write(f"**Prendi una barra da 6 metri e taglia:**")
                for idx, pezzo in enumerate(barra['pezzi'], 1):
                    tipo, apertura, lunghezza = pezzo
                    st.write(f"{idx}. {tipo} per {apertura}: **{lunghezza} cm**")
                spreco = LUNGHEZZA_BARRA - sum([p[2] for p in barra['pezzi']])
                st.write(f"*Avanzo: {spreco} cm*")
