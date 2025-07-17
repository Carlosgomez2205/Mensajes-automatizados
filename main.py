import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# 1. Cargar variables de entorno
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_USER     = os.environ.get("EMAIL_USER")
EMAIL_PASS     = os.environ.get("EMAIL_PASS")
EMAIL_TO       = os.environ.get("EMAIL_TO")

# Validar claves
if not all([GEMINI_API_KEY, EMAIL_USER, EMAIL_PASS, EMAIL_TO]):
    print("❌ Error: Una o más variables de entorno no están definidas.")
    exit(1)

# 2. Configuración de grupos como lista (ya no como diccionario con claves duplicadas)
grupos = [
    {
        "nombre": "Análisis de datos G4",
        "horario": {"Mon": "18:00–22:00", "Fri": "18:00–22:00"},
        "lugar": "CEIE, PASTO - AULA: 202"
    },
    {
        "nombre": "Análisis de datos G4",
        "horario": {"Wed": "18:00–22:00"},
        "lugar": "CEIE, PASTO - AULA: 303"
    },
    {
        "nombre": "Inteligencia Artificial G7",
        "horario": {"Sat": "08:00–12:00"},
        "lugar": "CEIE, PASTO - AULA: 203"
    },
    {
        "nombre": "Inteligencia Artificial G7",
        "horario": {"Tue": "08:00–12:00", "Thu": "08:00–12:00"},
        "lugar": "CEIE, PASTO - AULA: 201"
    },
    {
        "nombre": "Inteligencia Artificial G4",
        "horario": {"Mon": "08:00–12:00", "Wed": "08:00–12:00", "Fri": "08:00–12:00"},
        "lugar": "CEIE, PASTO - AULA: 202"
    },
    {
        "nombre": "Inteligencia Artificial G6",
        "horario": {"Wed": "18:00–22:00"},
        "lugar": "CEIE, PASTO - AULA: 302"
    },
    {
        "nombre": "Inteligencia Artificial G6",
        "horario": {"Thu": "18:00–22:00"},
        "lugar": "CINAR SISTEMAS, PASTO - AULA: 101"
    },
    {
        "nombre": "Inteligencia Artificial G6",
        "horario": {"Tue": "18:00–22:00"},
        "lugar": "CEIE, PASTO - AULA: 203"
    }
]

# 3. Calcular el día siguiente (puedes cambiar days=0 a days=1 si deseas programar para mañana)
mañana = datetime.now() + timedelta(days=1)
dia_abbr = mañana.strftime("%a")
fecha_texto = mañana.strftime("%A, %d de %B").capitalize()

# 4. Generar mensajes
mensajes = []
for grupo in grupos:
    if dia_abbr in grupo["horario"]:
        hora = grupo["horario"][dia_abbr]
        lugar = grupo["lugar"]
        nombre = grupo["nombre"]

        prompt = (
            "Eres un asistente educativo que redacta recordatorios de clases para jóvenes en un bootcamp. "
            "Redacta el siguiente mensaje completamente en español, con tono positivo, breve y usando emojis relacionados al aprendizaje. "
            f"Grupo: {nombre}, Fecha: {fecha_texto}, Hora: {hora}, Lugar: {lugar}. "
            "Nunca mezcles inglés ni digas 'camper', usa 'campistas'. Este mensaje se enviará por correo."
        )

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            r = requests.post(url, headers=headers, json=payload)
            r.raise_for_status()

            texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            mensajes.append(texto.strip())
        except Exception as e:
            print(f"❌ Error al generar mensaje para {nombre}: {e}")

# 5. Verificar y enviar
if not mensajes:
    print("✅ Ningún grupo tiene clase hoy.")
    exit(0)

mensaje_html = "<br><br>".join(mensajes)
print("📩 Mensaje generado:\n", mensaje_html)

# 6. Enviar correo
email = MIMEMultipart("alternative")
email["From"] = EMAIL_USER
email["To"] = EMAIL_TO
email["Subject"] = f"📌 Recordatorios de clase para {fecha_texto}"

contenido_html = f"<html><body style='font-family:sans-serif;'>{mensaje_html}</body></html>"
email.attach(MIMEText(contenido_html, "html", "utf-8"))

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(email)
    print("✅ Correo enviado con éxito.")
except Exception as e:
    print(f"❌ Error al enviar el correo: {e}")

