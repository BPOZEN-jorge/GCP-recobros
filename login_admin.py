"""
Inicio de sesión ÚNICO del administrador.

Se ejecuta UNA vez en tu equipo (no en Streamlit Cloud):

    pip install google-auth-oauthlib
    python login_admin.py

1. Se abre el navegador: entra con el correo que tiene acceso al bucket.
2. El script imprime el bloque [gcp_oauth] listo para pegar en los secrets de Streamlit.

No subas client_secret.json ni el refresh token a GitHub.
"""
import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/devstorage.read_only"]
ARCHIVO_CLIENTE = sys.argv[1] if len(sys.argv) > 1 else "client_secret.json"

flow = InstalledAppFlow.from_client_secrets_file(ARCHIVO_CLIENTE, SCOPES)
# prompt=consent + access_type=offline garantizan que Google entregue un refresh token
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

if not creds.refresh_token:
    sys.exit("Google no devolvió refresh token. Revoca el acceso en myaccount.google.com/permissions y repite.")

print("\n# ===== Pega esto en los secrets de Streamlit =====")
print("[gcp_oauth]")
print(f"client_id = {json.dumps(creds.client_id)}")
print(f"client_secret = {json.dumps(creds.client_secret)}")
print(f"refresh_token = {json.dumps(creds.refresh_token)}")
