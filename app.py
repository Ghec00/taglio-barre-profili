import streamlit as st
import pulp
import pandas as pd

st.title("Ottimizzatore Taglio Barre Lego 🔧")
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
        altezza = st.number_input(f"Altezza (cm)", min_value=1, max_value=600, value=100, key=f"alt_{i}")
    with col2:
        larghezza = st.number_input(f"Larghezza (cm)", min_value=1, max_value=600, value=100, key=f"lar_{i}")
    
    aperture_data.append({
        'numero': i+1,
        'altezza': altezza,
        'larghezza': larghezza
    })
    
    # Ogni apertura richiede 2 pezzi altezza + 1 pezzo larghezza
    pezzi_necessari.append(('Altezza SX', f'Apertura {i+1}', altezza))
    pezzi_necessari.append(('Altezza DX', f'Apertura {i+1}', altezza))
    pezzi_necessari.append(('Larghezza', f'Apertura {i+1}', larghezza))

# Bottone calcolo
if st.button("Calcola Piano di Taglio Ottimale"):
    with st.spinner("Ottimizzazione in corso..."):
        
        # Algoritmo First Fit Decreasing (euristica semplice ed efficace)
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