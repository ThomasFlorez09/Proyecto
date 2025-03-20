import network
import time
import ntptime
import machine
import json
import urequests  # Librería para hacer peticiones HTTP en MicroPython
from hcsr04 import HCSR04
from hx711 import HX711

# Configuración WiFi
SSID = "Familia VC"
PASSWORD = "sergio10203."

# Configuración de Firebase
FIREBASE_URL = "https://trabajo-12ee4-default-rtdb.firebaseio.com/"

# Configuración de zona horaria (UTC-6 para México, Colombia, etc.)
TIMEZONE_OFFSET = -5 * 3600  

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)  
    wlan.active(True)  
    wlan.connect(SSID, PASSWORD)  
    print("Conectando...")
    for _ in range(10):
        if wlan.isconnected():
            print("Conectado")
            return True
        time.sleep(1)
    return False

def obtener_fecha_hora():
    intentos = 5
    for intento in range(intentos):
        try:
            ntptime.settime()
            tiempo = time.localtime(time.time() + TIMEZONE_OFFSET)
            return list(tiempo[:6])
        except Exception as e:
            print(f"No se puede obtener la hora", e)
            time.sleep(2)

def incrementar_segundo(fecha_hora):
    fecha_hora[5] += 1  
    if fecha_hora[5] >= 60:
        fecha_hora[5] = 0
        fecha_hora[4] += 1  
        if fecha_hora[4] >= 60:
            fecha_hora[4] = 0
            fecha_hora[3] += 1  
            if fecha_hora[3] >= 24:
                fecha_hora[3] = 0
                fecha_hora[2] += 1  
    return fecha_hora

def redondear_peso(peso):
    """Redondea el peso al número entero más cercano."""
    return round(peso)

def enviar_a_firebase(datos):
    url = FIREBASE_URL + "monedas.json"
    intentos = 5  
    for intento in range(intentos):
        try:
            respuesta = urequests.post(url, json=datos)
            print("Datos enviados a Firebase:", respuesta.text)
            respuesta.close()
            return  
        except Exception as e:
            print(f"Error enviando datos a Firebase (Intento {intento+1}/{intentos}):", e)
            time.sleep(2)  
    print("❌ No se pudo enviar los datos después de varios intentos.")

# Ejecutar funciones
if conectar_wifi():
    time.sleep(2)  
    fecha_hora_actual = obtener_fecha_hora()

# --- Configuración de Sensores ---
PIN_IR1 = 16
sensor_ir1 = machine.Pin(PIN_IR1, machine.Pin.IN)
medidor = HCSR04(trigger_pin=14, echo_pin=12)

# --- Configuración del HX711 ---
hx = HX711(dout=4, pd_sck=5)  # Asegúrate de conectar los pines correctos
hx.tare()  # Tara inicial

# --- Configuración del Watchdog ---
wdt = machine.WDT(timeout=5000)  

# --- Variables Globales ---
conteo_global = 0  
caja1, caja2, caja3 = 0, 0, 0  
peso_caja1, peso_caja2, peso_caja3 = 0, 0, 0  # Ahora los pesos serán enteros
buffer_datos = []
MAX_DATOS = 10  
error_clasificacion = 0

# --- Bucle principal ---
while True:
    wdt.feed()
    
    # Leer peso del sensor HX711
    try:
        peso = hx.read()  # Lectura en valores sin procesar
        peso_corregido = (peso + 378000) * 20000 / 2100  # Fórmula corregida
        peso_redondeado = redondear_peso(peso_corregido)  # Redondear el peso
        print("Peso medido (kg):", peso_redondeado)
    except Exception as e:
        print("Error al leer el sensor:", e)
        peso_redondeado = 0  # Si hay error, asignar 0 como precaución
    peso_caja3 = peso_redondeado 
    # Detectar si el sensor infrarrojo detecta un 1
    if sensor_ir1.value() == 1:
        conteo_global += 1  # Sumar a conteo global cada vez que el sensor infrarrojo detecta un 1
    
    # Medir distancia pero sin afectar el conteo global ni los pesos
    distancia = medidor.distance_cm()
    
    # Clasificación por distancia
    if 11 <= distancia <= 15:
        caja3 += 1
    elif 7 <= distancia < 11:
        caja2 += 1
        peso_caja2 += 5  # Asignar el nuevo peso 
    elif 1 <= distancia < 7:
        caja1 += 1
        peso_caja1 += 9.5  # Asignar el nuevo peso 
    elif distancia > 15:
        error_clasificacion = 1  # Error de clasificación

    # Actualizar hora
    fecha_hora_actual = incrementar_segundo(fecha_hora_actual)
    fecha_hora_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*fecha_hora_actual)
    
    # Crear datos para enviar
    datos = {
        "conteo_global": conteo_global,
        "fecha_hora_recoleccion": fecha_hora_str,
        "caja1": peso_caja1,
        "caja2": peso_caja2,
        "caja3": peso_caja3,
        "conteo_caja1": caja1,
        "conteo_caja2": caja2,
        "conteo_caja3": caja3,
        "errores_clasificacion": error_clasificacion
    }
    
    error_clasificacion = 0  # Resetear error
    print(distancia) 
    print(peso_corregido) 
    print(datos)
    buffer_datos.append(datos)  

    # Enviar solo cuando se acumulen 10 datos
    if len(buffer_datos) >= MAX_DATOS:
        print("Enviando datos a Firebase...")
        enviar_a_firebase(buffer_datos)
        buffer_datos = []  
    
    time.sleep(1)