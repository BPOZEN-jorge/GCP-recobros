# Extensión "Visor de contratos" (Chrome / Edge)

Redirige automáticamente cualquier enlace de contratos a la app de Streamlit. Ejemplo:

```
https://storage.cloud.google.com/contratos_enerweb/contratos_canalaecorp/OJ8.../contrato.pdf
```

se abre como:

```
https://gcp-recobros.streamlit.app/?doc=https://storage.cloud.google.com/contratos_enerweb/contratos_canalaecorp/OJ8.../contrato.pdf
```

También redirige los enlaces de `storage.googleapis.com` del mismo bucket.

## 1. Poner la URL de tu app (una vez)

En `reglas.json`, reemplaza el nombre de la app (ya configurado: `gcp-recobros`) por el nombre de tu app de Streamlit. Por ejemplo, si tu app es `https://gcp-recobros.streamlit.app`, la línea queda:

```json
"regexSubstitution": "https://gcp-recobros.streamlit.app/?doc=https://storage.cloud.google.com/\\1"
```

Para otro bucket, cambia `contratos_enerweb` en `regexFilter`.

## 2. Instalar en un equipo (manual)

1. Copia la carpeta `extension-chrome` al equipo (por ejemplo, `C:\VisorContratos`).
2. Abre `chrome://extensions` (en Edge: `edge://extensions`).
3. Activa **Modo de desarrollador** (arriba a la derecha).
4. Pulsa **Cargar descomprimida** y elige la carpeta.
5. Prueba: abre un enlace de `storage.cloud.google.com/contratos_enerweb/...`; debe aparecer la app.

No borres ni muevas la carpeta después de cargarla: Chrome la sigue leyendo de ahí.

## 3. Instalar en todos los equipos (sin ir uno por uno)

- **Chrome administrado con Google Workspace:** publica la extensión en Chrome Web Store como **privada** para tu dominio (cuenta de desarrollador: pago único de 5 USD). Después, en **Admin → Dispositivos → Chrome → Aplicaciones y extensiones**, márcala como **Forzar instalación**.
- **Equipos Windows en dominio (Active Directory):** con la directiva de grupo `ExtensionInstallForcelist` de Chrome o Edge, apuntando a la extensión publicada en la Web Store.

Con la instalación forzada, el usuario no puede desactivar la extensión.

## Limitaciones

- Solo funciona en navegadores donde la extensión está instalada (no en móviles).
- Por eso es importante **quitar los permisos del bucket** a los correos generales: sin la extensión, el enlace de GCS da "acceso denegado" en lugar de abrir el documento.
