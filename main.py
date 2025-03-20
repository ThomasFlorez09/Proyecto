import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import matplotlib.pyplot as plt
import plotly.express as px
import json

# 🔹 1. Configurar Firebase usando Secrets de Streamlit
firebase_secrets = st.secrets["firebase"]
firebase_credentials = json.loads(firebase_secrets["credentials"])
database_url = firebase_secrets["database_url"]

# Verifica si Firebase ya está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred, {
        "databaseURL": database_url
    })

# 🔹 2. Obtener datos desde Firebase
try:
    ref = db.reference("/monedas")
    datos = ref.get()
    st.write("Datos obtenidos correctamente de Firebase.")
except Exception as e:
    st.error(f"Error al obtener datos de Firebase: {e}")

# Procesar datos
registros = []
for clave, valor in datos.items():
    if isinstance(valor, dict):
        registros.append(valor)
    elif isinstance(valor, list):
        for item in valor:
            registros.append(item)

df = pd.DataFrame(registros)
df["fecha_hora_recoleccion"] = pd.to_datetime(df["fecha_hora_recoleccion"])
df = df.sort_values("fecha_hora_recoleccion")

# Función para corregir ceros
def corregir_ceros(df, columna):
    valores_corrigidos = df[columna].copy()
    maximo = valores_corrigidos.iloc[0]  # Inicia con el primer valor válido
    for i in range(1, len(valores_corrigidos)):
        variable = valores_corrigidos.iloc[i]
        if valores_corrigidos.iloc[i] < maximo:
            valores_corrigidos.iloc[i]  = maximo  
            if variable >= 2:
                variable = 1
            valores_corrigidos.iloc[i]  += variable 
        maximo = valores_corrigidos.iloc[i]

    df[columna] = valores_corrigidos
    return df

# Aplicar corrección de ceros a las columnas necesarias
columnas_a_corregir = ["conteo_caja1", "conteo_caja2", "conteo_caja3", "caja1", "caja2", "caja3", "conteo_global"]
for columna in columnas_a_corregir:
    df = corregir_ceros(df, columna)

# Función para graficar
def graficar(x, y, titulo, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df[x], df[y], marker="o", linestyle="-")
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid()
    st.pyplot(fig)

# Interfaz de Streamlit
st.write("**Integrantes:** Thomas Flórez Mendoza - Sergio Vargas Cruz")
st.title("Dashboard de Monitoreo de Conteo de Monedas")
st.write("En el presente dashboard se presentan los datos y mediciones preliminares correspondientes a la primera entrega del proyecto de la asignatura Internet de las Cosas (IOT), el cual consiste en "
"el desarrollo de un sistema integral IoT para el seguimiento de clasificación, distribución y entrega de monedas como forma de carga efectiva para transacciones punto a punto. En el caso de esta primera entrega, se realizan mediciones sobre la cantidad de monedas, la clasificación correspondiente y el peso total de la caja en la que se clasifican.")

st.subheader("📄 Datos almacenados en la base de datos de Firebase")
st.write("Los datos utilizados corresponden a las mediciones realizadas con sensores de tipo infrarrojo, de ultrasonido y de peso (extensiométricos) y son extraídos de una base de datos creada anteriormente en Firebase. El dataset correspondiente se evidencia a continuación.")

st.dataframe(df)

st.write("De acuerdo a lo anterior, es posible evidenciar que el dataset cuenta con 612 filas que corresponden al número de mediciones realizadas por los sensores y tiene columnas que corresponden a las variables **caja1** que corresponde al peso de la primer caja, **caja2** que corresponde al peso de la segunda caja, **caja3** que corresponde al peso de la tercer caja, "
"**conteo_caja1** que corresponde al número de monedas en la caja 1, **conteo_caja2** que corresponde al número de monedas en la caja 2, **conteo_caja3** que corresponde al número de monedas en la caja 3, **conteo_global** que corresponde al número total de monedas, **errores_clasificacion** que corresponde a mediciones fuera del rango predeterminado y **fecha_hora_recoleccion** "
"que corresponde a la fecha y hora de la toma del dato.")

st.subheader("Visualización de gráficas de las mediciones")
st.write("Para la visualización de los datos almacenados, inicialmente se opta por presentar las gráficas correspondientes a las mediciones realizadas con respecto al tiempo."
" Esto con el fin de evidenciar la variación de los datos almacenados.")

st.write("La gráfica que se presenta a continuación permite evidenciar el conteo de monedas para la caja 1 con respecto al tiempo. En este es posible evidenciar el comportamiento ascendente que tiene el conteo en la caja, así como también los instantes en los que no se presenta un aumento de monedas en esta caja. "
"El valor final del conteo para esta variable es de 133 monedas")
graficar("fecha_hora_recoleccion", "conteo_caja1", "Conteo de Caja 1 vs Hora", "Hora", "Conteo")

st.write("La siguiente gráfica corresponde al conteo de monedas para la caja 2 con respecto al tiempo. En este es posible evidenciar el comportamiento ascendente que tiene el conteo en la caja, así como también los instantes en los que no se presenta un aumento de monedas en esta caja. "
"El valor final del conteo para esta variable es de 379 monedas")
graficar("fecha_hora_recoleccion", "conteo_caja2", "Conteo de Caja 2 vs Hora", "Hora", "Conteo")

st.write("La gráfica que se presenta a continuación permite evidenciar el conteo de monedas para la caja 3 con respecto al tiempo. En este es posible evidenciar el comportamiento ascendente que tiene el conteo en la caja, así como también los instantes en los que no se presenta un aumento de monedas en esta caja. "
"El valor final del conteo para esta variable es de 243 monedas")
graficar("fecha_hora_recoleccion", "conteo_caja3", "Conteo de Caja 3 vs Hora", "Hora", "Conteo")

st.write("Posteriormente, se procede a presentar las gráficas de la variación del peso para cada una de las cajas con respecto al tiempo.")
st.write("La gráfica que se evidencia a continuación corresponde a la variación del peso por cada hora para la caja 1. El peso final en esta medición es de 294.5 gramos.")
graficar("fecha_hora_recoleccion", "caja1", "Peso de Caja 1 vs Hora", "Hora", "Peso")
st.write("La gráfica que se presenta en la parte inferior corresponde a la variación del peso por cada hora para la caja 2. El peso final en esta medición es de 435 gramos.")
graficar("fecha_hora_recoleccion", "caja2", "Peso de Caja 2 vs Hora", "Hora", "Peso")
st.write("La siguiente gráfica corresponde a la variación del peso por cada hora para la caja 3. El peso final en esta medición es de 258 gramos.")
graficar("fecha_hora_recoleccion", "caja3", "Peso de Caja 3 vs Hora", "Hora", "Peso")

st.subheader("Gráficos para al comparación de caja con más monedas")

st.write("Los graficos que se presenta a continuación son de gran importancia, debido a que permiten visualizar el conteo y la proporción de monedas en cada caja para comprender "
"cómo se distribuyen las monedas en el sistema de clasificación. Esta información ayuda a identificar posibles desequilibrios o preferencias en la acumulación de monedas, "
"lo que puede ser útil para el proceso de clasificación, ajustar la capacidad de las cajas o detectar anomalías en el funcionamiento del sistema.")

st.write("La gráfica de barars que se presenta a continuación  permite evidenciar el conteo númerico de la cantidad de monedas que hay en cada caja y permite comparar la diferencia"
"a través de la variación de la altura de las barras.")

# Gráfico de barras para el conteo de monedas por caja
st.subheader("Gráfico de Barras: Conteo de Monedas por Caja")
conteo_por_caja = df[["conteo_caja1", "conteo_caja2", "conteo_caja3"]].iloc[-1]  # Último valor de cada columna
fig_bar = px.bar(conteo_por_caja, x=conteo_por_caja.index, y=conteo_por_caja.values, labels={"x": "Caja", "y": "Conteo de Monedas"})
st.plotly_chart(fig_bar)

st.write("La gráfica muestra el conteo de monedas en tres cajas diferentes: conteo_caja1, conteo_caja2 y conteo_caja3. Se observa que conteo_caja2 tiene el mayor número de monedas, "
"alcanzando un valor cercano a 350, lo que indica que es la caja con la mayor acumulación. Le sigue conteo_caja3 con un valor alrededor de 250, y finalmente conteo_caja1 con un conteo "
"cercano a 150. Esta distribución sugiere que las monedas se han clasificado de manera desigual, con una preferencia notable hacia la caja 2. ")

st.write("El diagrama de pastel que se evidencia a continuación va ligado directamente a la gráfica presentada anteriormente, sin embargo, en este caso se presenta la proporción en "
"la clasificación de monedas de manera porcentual.")

# Gráfico de pastel para la proporción de monedas en cada caja
st.subheader("Gráfico de Pastel: Proporción de Monedas por Caja")
fig_pie = px.pie(values=conteo_por_caja.values, names=conteo_por_caja.index, title="Proporción de Monedas por Caja")
st.plotly_chart(fig_pie)

st.write("El gráfico de pastel muestra la proporción de monedas distribuidas en las tres cajas: conteo_caja1, conteo_caja2 y conteo_caja3. La caja 2 (conteo_caja2) representa la mayor "
"proporción con un 50.2%, lo que indica que más de la mitad de las monedas se han acumulado en esta caja. La caja 3 (conteo_caja3) sigue con un 32.2%, mientras que la caja 1 (conteo_caja1) "
"tiene la menor proporción con solo un 17.6%. Esta distribución refuerza la idea de que las monedas se han clasificado de manera desigual, con una clara preferencia hacia la caja 2")