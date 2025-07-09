from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Función para evitar emojis fuera del rango BMP (que generan error en ChromeDriver)
def filtrar_texto_bmp(texto):
    return ''.join(c for c in texto if ord(c) <= 0xFFFF)

# 1. Cargar clave desde .env
load_dotenv(dotenv_path="keys.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Configurar grupos y horarios
grupos = {
    "Análisis de datos G4": {
        "horario": {"Mon": "18:00–22:00", "Wed": "18:00–22:00", "Fri": "18:00–22:00"},
        "lugar": "CEIE calle 11A#32-40, PASTO"
    },
    "Inteligencia Artificial G7": {
        "horario": {"Tue": "08:00–12:00", "Thu": "08:00–12:00", "Sat": "08:00–12:00"},
        "lugar": "CEIE calle 11A#32-40, PASTO"
    },
    "Inteligencia Artificial G4": {
        "horario": {"Mon": "08:00–12:00", "Wed": "08:00–12:00", "Fri": "08:00–12:00"},
        "lugar": "CEIE calle 11A#32-40, PASTO"
    },
    "Inteligencia Artificial G6": {
        "horario": {"Tue": "18:00–22:00", "Wed": "18:00–22:00", "Thu": "18:00–22:00"},
        "lugar": "CEIE calle 11A#32-40, PASTO"
    }
}

# 3. Calcular mañana
mañana = datetime.now() + timedelta(days=1)
dia_abbr = mañana.strftime("%a")
fecha_texto = mañana.strftime("%A, %d de %B")

# 4. Generar mensajes
mensajes = []
for grupo, info in grupos.items():
    if dia_abbr in info["horario"]:
        hora = info["horario"][dia_abbr]
        lugar = info["lugar"]

        prompt = (
            f"Eres un asistente educativo. Escribe un mensaje corto, claro y motivador para recordar a los campistas del grupo "
            f"{grupo} que mañana {fecha_texto} tienen clase de {hora}. "
            f"El lugar es {lugar}. "
            f"No uses la palabra 'Camper', di 'campistas'. El mensaje será enviado por WhatsApp."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            r = requests.post(url, headers=headers, json=payload)
            r.raise_for_status()
            mensaje = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            mensajes.append(mensaje.strip())
        except Exception as e:
            print(f"❌ Error al generar mensaje para {grupo}:", e)

# 5. Unir mensajes y filtrar caracteres fuera del rango BMP
if not mensajes:
    print("✅ Ningún grupo tiene clase mañana.")
    exit()

mensaje_final = filtrar_texto_bmp("\n\n".join(mensajes))
print("📩 Mensaje generado:\n", mensaje_final)

# 6. Lanzar navegador con sesión guardada
options = webdriver.ChromeOptions()
options.add_argument(r"user-data-dir=C:\Users\carlo\AppData\Local\Google\Chrome\User Data\RemBot")
driver = webdriver.Chrome(options=options)

# 7. Cargar WhatsApp y esperar automáticamente
driver.get("https://web.whatsapp.com")
print("⏳ Esperando que WhatsApp Web cargue...")
time.sleep(10)

# 8. Buscar grupo y enviar mensaje
NOMBRE_DESTINO = "Mensajes grupos TTech"
try:
    search = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search.click()
    search.send_keys(NOMBRE_DESTINO)
    time.sleep(2)

    driver.find_element(By.XPATH, f'//span[@title="{NOMBRE_DESTINO}"]').click()
    time.sleep(2)

    chatbox = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
    chatbox.send_keys(mensaje_final)
    time.sleep(1)
    chatbox.send_keys(u'\ue007')  # ENTER para enviar
    print("✅ Mensaje enviado.")

    # Espera extra para asegurar el envío
    time.sleep(5)

except Exception as e:
    print("❌ Error al enviar el mensaje:", e)

# 9. Cierre automático del navegador
print("🔒 Cerrando navegador...")
driver.quit()
