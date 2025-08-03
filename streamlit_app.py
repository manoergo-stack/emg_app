import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Análisis de RMS de señales EMG", layout="wide")

st.title("Análisis de RMS de señales EMG")

# Paso 1: Subir archivo
archivo = st.file_uploader("Sube el archivo .xlsx", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Mostrar preview
    st.subheader("Datos originales")
    st.dataframe(df.head())

    # Paso 2: Convertir de mV a µV si el usuario lo desea
    multiplicar = st.checkbox("Multiplicar señales por 1000 (de mV a µV)", value=True)

    canales = df.columns[1:9]  # Solo considera columnas 1 a 8 (sin incluir "Tiempo")

    if multiplicar:
        df[canales] = df[canales] * 1000
        st.success("Se multiplicaron las señales por 1000.")
    else:
        st.info("No se realizó la conversión. Se asume que las señales ya están en µV.")

    # Mostrar preview convertido
    st.subheader("Primeras filas después de conversión (si se aplicó):")
    st.dataframe(df.head())

    # Paso 3: Cálculo de RMS por ventana
    ventana = 100  # Tamaño de ventana
    rms = pd.DataFrame()
    rms['Tiempo'] = df['Tiempo'].rolling(ventana).mean()

    for canal in canales:
        if canal in df.columns:
            rms[canal] = df[canal].rolling(ventana).apply(lambda x: np.sqrt(np.mean(x**2)), raw=True)

    # Paso 4: Gráfico interactivo
    st.subheader("RMS por ventana")
    fig = go.Figure()
    for canal in canales:
        if canal in rms.columns:
            fig.add_trace(go.Scatter(x=rms['Tiempo'], y=rms[canal], mode='lines', name=canal))
    fig.update_layout(xaxis_title="Tiempo (s)", yaxis_title="RMS (µV)")
    st.plotly_chart(fig, use_container_width=True)

    # Paso 5: Selección de intervalo y estadísticas
    st.subheader("Selecciona un intervalo de tiempo para análisis")
    tiempo_min = float(rms['Tiempo'].min())
    tiempo_max = float(rms['Tiempo'].max())

    inicio = st.number_input("Inicio (s)", min_value=tiempo_min, max_value=tiempo_max, value=tiempo_min)
    fin = st.number_input("Fin (s)", min_value=tiempo_min, max_value=tiempo_max, value=tiempo_max)

    if inicio < fin:
        seleccion = rms[(rms['Tiempo'] >= inicio) & (rms['Tiempo'] <= fin)]

        st.subheader(f"Estadísticas de RMS entre {inicio:.2f}s y {fin:.2f}s")
        for canal in canales:
            if canal in seleccion.columns:
                st.markdown(f"**{canal}**")
                st.markdown(f"- Promedio: {seleccion[canal].mean():.2f} µV")
                st.markdown(f"- Máximo: {seleccion[canal].max():.2f} µV")
                st.markdown(f"- Mínimo: {seleccion[canal].min():.2f} µV")
                st.markdown(f"- Desviación estándar: {seleccion[canal].std():.2f} µV")
    else:
        st.error("El tiempo de inicio debe ser menor que el de fin.")
