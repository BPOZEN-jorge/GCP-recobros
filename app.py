"""
Visor de documentos GCP — Streamlit
--------------------------------------------------------------
- Bloqueo por IP pública del navegador (misma lógica que "lector-cobros").
- La app queda "logueada" con UN correo que tiene permisos sobre el bucket
  (login único con `gcloud auth application-default login`, ver login_admin.py).
  Su refresh token vive en los secrets de Streamlit: los usuarios nunca ven
  correo, contraseña ni token, y no necesitan cuenta de Google.
- El usuario pega el enlace de storage.cloud.google.com (o abre la app con
  ?doc=<enlace>) y ve el PDF dentro de la app.
- Solo se sirven documentos de los buckets listados en [gcp] buckets_permitidos.
"""
import ipaddress
import re
import urllib.parse

import streamlit as st
import streamlit.components.v1 as components
from google.api_core import exceptions as gexc
from google.cloud import storage
from google.oauth2.credentials import Credentials

# ==========================================
# CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Visor de documentos", page_icon="📄", layout="wide")

# Sin scopes explícitos: se usan los que concedió el login de gcloud (cloud-platform).
# Pedir otro scope (p. ej. devstorage.read_only) al renovar da "invalid_scope".
TOKEN_URI = "https://oauth2.googleapis.com/token"
CACHE_SEGUNDOS = 300

# Acepta: https://storage.cloud.google.com/<bucket>/<objeto>
#         https://storage.googleapis.com/<bucket>/<objeto>
#         gs://<bucket>/<objeto>
#         https://console.cloud.google.com/storage/browser/_details/<bucket>/<objeto>
PATRON_ENLACE = re.compile(
    r"(?:gs://|storage\.cloud\.google\.com/|storage\.googleapis\.com/|/_details/)"
    r"(?P<bucket>[a-z0-9][a-z0-9._-]{1,220})/(?P<objeto>[^?#]+)"
)


# ==========================================
# VALIDACIÓN DE IP PÚBLICA (igual que lector-cobros)
# ==========================================
CAMPO_IP = "ip_publica_navegador"  # campo de texto oculto por donde el navegador entrega su IP pública
CSS_CAMPO_IP = f"""
<style>
.st-key-{CAMPO_IP},
div[data-testid="stTextInput"]:has(input[aria-label="{CAMPO_IP}"]) {{
  position: absolute !important; left: -10000px !important; width: 1px; height: 1px; overflow: hidden;
}}
</style>
"""


def validar_ip(ip_usuario: str) -> bool:
    if not ip_usuario or not isinstance(ip_usuario, str):
        return False
    rangos = st.secrets.get("network", {}).get("ips_permitidas", ["127.0.0.1"])
    try:
        ip_obj = ipaddress.ip_address(ip_usuario.strip())
        return any(ip_obj in ipaddress.ip_network(r, strict=False) for r in rangos)
    except ValueError:
        return False


def detectar_ip_publica():
    """El navegador consulta su IP pública en ipify y la escribe en el campo oculto CAMPO_IP."""
    html = f"""
<script>
(async () => {{
  const app = window.parent;
  let ip = "";
  try {{
    const r = await fetch("https://api.ipify.org?format=json", {{cache: "no-store"}});
    ip = (await r.json()).ip || "";
  }} catch (e) {{}}
  ip = ip || "ERROR";
  for (let i = 0; i < 100; i++) {{
    const campo = app.document.querySelector('input[aria-label="{CAMPO_IP}"]');
    if (campo) {{
      const setter = Object.getOwnPropertyDescriptor(app.HTMLInputElement.prototype, "value").set;
      campo.focus();
      setter.call(campo, ip);
      campo.dispatchEvent(new app.Event("input", {{bubbles: true}}));
      campo.dispatchEvent(new app.KeyboardEvent("keydown", {{key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true}}));
      campo.blur();
      return;
    }}
    await new Promise(r => setTimeout(r, 100));
  }}
}})();
</script>
"""
    # st.iframe reemplaza a components.html (obsoleto) en Streamlit recientes
    if hasattr(st, "iframe"):
        st.iframe(html, height=1)
    else:
        components.html(html, height=0)


# ==========================================
# ACCESO A CLOUD STORAGE (cuenta única del administrador)
# ==========================================
@st.cache_resource
def cliente_storage() -> storage.Client:
    cfg = st.secrets["gcp_oauth"]
    creds = Credentials(
        token=None,
        refresh_token=cfg["refresh_token"],
        token_uri=TOKEN_URI,
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        scopes=None,
    )
    return storage.Client(project=st.secrets.get("gcp", {}).get("project_id"), credentials=creds)


def leer_enlace(enlace: str):
    """Devuelve (bucket, objeto) a partir de un enlace de GCS, o None si no se reconoce."""
    m = PATRON_ENLACE.search(enlace.strip())
    if not m:
        return None
    objeto = urllib.parse.unquote(m.group("objeto")).strip("/")
    if not objeto or ".." in objeto.split("/"):
        return None
    return m.group("bucket"), objeto


def bucket_permitido(bucket: str) -> bool:
    permitidos = st.secrets.get("gcp", {}).get("buckets_permitidos", [])
    return bucket in permitidos


@st.cache_data(ttl=CACHE_SEGUNDOS, show_spinner=False, max_entries=50)
def descargar(bucket: str, objeto: str):
    """Devuelve (bytes, content_type) o lanza la excepción de GCS."""
    blob = cliente_storage().bucket(bucket).get_blob(objeto)
    if blob is None:
        raise FileNotFoundError(objeto)
    return blob.download_as_bytes(), blob.content_type or ""


# ==========================================
# CORTAFUEGOS POR IP PÚBLICA
# ==========================================
st.markdown(CSS_CAMPO_IP, unsafe_allow_html=True)
ip_detectada = st.text_input(CAMPO_IP, key=CAMPO_IP, label_visibility="collapsed").strip()

if not ip_detectada:
    detectar_ip_publica()
    st.info("⏳ Validando conexión con la red corporativa...")
    st.stop()

if ip_detectada == "ERROR":
    st.error(
        "⚠️ No se pudo consultar tu IP pública (api.ipify.org). Revisa tu conexión o que la red no "
        "bloquee ese sitio y recarga la página."
    )
    st.stop()

if not validar_ip(ip_detectada):
    st.error("🚫 **ACCESO NO AUTORIZADO**")
    st.warning(
        f"No puedes ingresar a este portal desde tu red actual.\n\n"
        f"**IP detectada:** `{ip_detectada}`\n\n"
        f"La plataforma solo está disponible desde la red corporativa autorizada."
    )
    st.stop()

# ==========================================
# VISOR
# ==========================================
st.title("📄 Visor de documentos")
st.caption(f"🌐 IP autorizada: `{ip_detectada}`")

doc_param = st.query_params.get("doc", "")
enlace = st.text_input(
    "Enlace del documento",
    value=doc_param,
    placeholder="https://storage.cloud.google.com/<bucket>/<ruta>/archivo.pdf",
)

if not enlace:
    st.info("Pega el enlace de Google Cloud Storage del documento que quieres ver.")
    st.stop()

datos = leer_enlace(enlace)
if not datos:
    st.error("Enlace no reconocido. Debe ser un enlace de storage.cloud.google.com o gs://.")
    st.stop()

bucket, objeto = datos
if not bucket_permitido(bucket):
    st.error(f"El bucket `{bucket}` no está autorizado en este visor.")
    st.stop()

# Mantiene el documento en la URL para poder recargar o compartir el enlace de la app
if doc_param != enlace:
    st.query_params["doc"] = enlace

try:
    with st.spinner("Cargando documento..."):
        contenido, tipo = descargar(bucket, objeto)
except FileNotFoundError:
    st.error("El documento no existe en el bucket.")
    st.stop()
except gexc.Forbidden:
    st.error("La cuenta del visor no tiene permiso sobre ese documento.")
    st.stop()
except Exception as e:  # token revocado/caducado, red, etc.
    if "invalid_grant" in str(e):
        st.error("El acceso de la cuenta del visor caducó. Avisa al administrador para renovar el token.")
    else:
        st.error("No se pudo cargar el documento. Inténtalo de nuevo en unos minutos.")
    st.caption(f"Detalle técnico: {type(e).__name__}: {str(e)[:200]}")
    st.stop()

nombre = objeto.rsplit("/", 1)[-1]
st.subheader(nombre)

# Muchos archivos del bucket están guardados como application/octet-stream (por eso el
# navegador los descarga); se decide el tipo por la extensión y se muestran dentro de la app.
if nombre.lower().endswith(".pdf"):
    tipo = "application/pdf"

if tipo == "application/pdf":
    st.pdf(contenido, height=900)
elif tipo.startswith("image/"):
    st.image(contenido)
else:
    st.info("Este tipo de archivo no se puede previsualizar.")

if st.secrets.get("gcp", {}).get("permitir_descarga", False):
    st.download_button("⬇️ Descargar", contenido, file_name=nombre, mime=tipo or None)
