"""
Inicio de sesión ÚNICO con el correo que tiene permisos sobre el bucket.

No hay que configurar nada en la consola de GCP: se usa el login de Google Cloud CLI.

1. Instala Google Cloud CLI (una vez):
       winget install Google.CloudSDK
2. Inicia sesión con el correo que tiene permisos (se abre el navegador):
       gcloud auth application-default login
3. Ejecuta este script:
       python login_admin.py
   Imprime el bloque [gcp_oauth] listo para pegar en los secrets de Streamlit.

No subas ese bloque a GitHub.
"""
import json
import os
import sys
from pathlib import Path


def ruta_credenciales() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    if os.name == "nt":
        return Path(os.environ["APPDATA"]) / "gcloud" / "application_default_credentials.json"
    return Path.home() / ".config" / "gcloud" / "application_default_credentials.json"


ruta = ruta_credenciales()
if not ruta.exists():
    sys.exit(f"No se encontró {ruta}.\nPrimero ejecuta: gcloud auth application-default login")

datos = json.loads(ruta.read_text(encoding="utf-8"))
if datos.get("type") != "authorized_user" or not datos.get("refresh_token"):
    sys.exit("El archivo no es un login de usuario. Ejecuta: gcloud auth application-default login")

print("\n# ===== Pega esto en los secrets de Streamlit =====")
print("[gcp_oauth]")
for campo in ("client_id", "client_secret", "refresh_token"):
    print(f"{campo} = {json.dumps(datos[campo])}")
