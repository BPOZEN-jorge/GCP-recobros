# GCP-recobros · Visor de documentos

App de Streamlit que queda **logueada con un correo que tiene permisos** sobre el bucket. Quien abra el enlace de la app, desde una IP autorizada, ve los documentos **sin cuenta de Google y sin conocer ese correo**.

- **Login único:** inicias sesión una vez con el correo que tiene permisos y su token queda en los secrets de Streamlit.
- **Enlaces compartibles:** compartes `https://<tu-app>.streamlit.app/?doc=<enlace de GCS>` en lugar del enlace de Google Cloud.
- **Acceso por IP pública** (`[network] ips_permitidas`), igual que en `lector-cobros`.
- **Buckets limitados:** solo se sirven los de `[gcp] buckets_permitidos`. La descarga está desactivada por defecto.
- **Nada que configurar en la consola de GCP.**

## 1. Login único con el correo que tiene permisos

En tu equipo (una sola vez):

```bash
winget install Google.CloudSDK
```

Cierra y vuelve a abrir la terminal, y luego:

```bash
gcloud auth application-default login
```

Se abre el navegador: entra con el correo que tiene permisos sobre el bucket. Después:

```bash
python login_admin.py
```

El script imprime el bloque `[gcp_oauth]`.

## 2. Secrets de Streamlit

Copia `secrets.toml.example` en **Streamlit Cloud → App → Settings → Secrets** y reemplaza `[gcp_oauth]` por el bloque que imprimió `login_admin.py`.

## 3. Compartir documentos

Enlace de GCS:
```
https://storage.cloud.google.com/contratos_enerweb/contratos_canalaecorp/OJ8DXYS1KMAWDGLN2VA5W4WWQOMMGH7U/contrato.pdf
```
Enlace que compartes:
```
https://<tu-app>.streamlit.app/?doc=https://storage.cloud.google.com/contratos_enerweb/contratos_canalaecorp/OJ8DXYS1KMAWDGLN2VA5W4WWQOMMGH7U/contrato.pdf
```
También se puede abrir la app y pegar el enlace de GCS en el campo de texto.

Enlaces admitidos: `storage.cloud.google.com`, `storage.googleapis.com`, `gs://` y `console.cloud.google.com/storage/browser/_details/...`.

## Renovar el login

Si cambia la contraseña del correo o se revoca el acceso, la app muestra *"El acceso de la cuenta del visor caducó"*. Repite el paso 1 y actualiza `refresh_token` en los secrets.

## Limitaciones

- La IP la informa el navegador (ipify), igual que en `lector-cobros`: un usuario con conocimientos técnicos podría falsearla.
- Lo que se muestra en pantalla se puede capturar.
