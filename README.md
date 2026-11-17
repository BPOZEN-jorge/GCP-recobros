# GCP-recobros · Visor de documentos

App de Streamlit para ver documentos de Google Cloud Storage **sin entregar credenciales a los usuarios**.

- El administrador inicia sesión **una sola vez** con la cuenta que tiene acceso al bucket. El refresh token queda en los secrets de Streamlit.
- Los usuarios pegan el enlace (`https://storage.cloud.google.com/...`) o abren `https://<app>/?doc=<enlace>` y ven el PDF dentro de la app.
- Acceso restringido por **IP pública** (`[network] ips_permitidas`), igual que en `lector-cobros`.
- Solo se sirven los buckets de `[gcp] buckets_permitidos`. La descarga está desactivada por defecto (`permitir_descarga`).

## 1. Configurar Google Cloud (una vez)

1. **APIs y servicios → Biblioteca**: habilita **Cloud Storage API** (normalmente ya viene habilitada).
2. **APIs y servicios → Pantalla de consentimiento de OAuth**:
   - Tipo **Interno** si la cuenta es de Google Workspace. Si no, tipo **Externo** y **publícala en Producción**: en modo *Testing* el refresh token caduca a los 7 días.
   - Ámbito: `https://www.googleapis.com/auth/devstorage.read_only`.
3. **APIs y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth**:
   - Tipo de aplicación: **App de escritorio**.
   - Descarga el JSON y guárdalo junto a este proyecto como `client_secret.json` (está en `.gitignore`).
4. En el bucket (`contratos_enerweb`) → **Permisos**:
   - Da a la cuenta del visor el rol **Lector de objetos de almacenamiento** (`roles/storage.objectViewer`).
   - Quita los correos generales.

## 2. Inicio de sesión único del administrador

```bash
pip install google-auth-oauthlib
python login_admin.py
```

Entra con la cuenta del visor. El script imprime el bloque `[gcp_oauth]`.

## 3. Secrets de Streamlit

Copia `secrets.toml.example` en **Streamlit Cloud → App → Settings → Secrets** y reemplaza `[gcp_oauth]` por el bloque que imprimió `login_admin.py`.

## 4. Desplegar

En Streamlit Cloud, crea una app a partir de este repositorio con el archivo principal `app.py`.

## Enlaces admitidos

- `https://storage.cloud.google.com/<bucket>/<ruta>`
- `https://storage.googleapis.com/<bucket>/<ruta>`
- `gs://<bucket>/<ruta>`
- `https://console.cloud.google.com/storage/browser/_details/<bucket>/<ruta>`

## Renovar el acceso

Si cambia la contraseña de la cuenta o se revoca el acceso, la app muestra *"El acceso de la cuenta del visor caducó"*. Vuelve a ejecutar `login_admin.py` y actualiza `refresh_token` en los secrets.

## Limitaciones

- La IP la informa el navegador (ipify), igual que en `lector-cobros`: sirve para filtrar el uso normal, pero un usuario con conocimientos técnicos podría falsearla.
- Lo que se muestra en pantalla se puede capturar.
