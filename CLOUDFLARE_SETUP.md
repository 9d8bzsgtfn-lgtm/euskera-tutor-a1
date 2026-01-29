# Configuración de Cloudflare Worker para Euskera Tutor

## Paso 1: Crear cuenta en Cloudflare

1. Ve a [workers.cloudflare.com](https://workers.cloudflare.com/)
2. Crea una cuenta gratuita si no tienes una
3. El plan gratuito incluye 100,000 peticiones/día

## Paso 2: Crear el Worker

1. En el dashboard, ve a **Workers & Pages**
2. Click en **Create application**
3. Click en **Create Worker**
4. Nombre sugerido: `euskera-tutor`
5. Click en **Deploy**

## Paso 3: Editar el código del Worker

1. Click en **Edit code** o **Quick edit**
2. Borra todo el código existente
3. Copia y pega el contenido de `worker/claude-proxy.js`
4. Click en **Save and Deploy**

## Paso 4: Configurar Variables de Entorno

1. Ve a **Settings** > **Variables**
2. Click en **Add variable** para cada una:

| Variable | Valor |
|----------|-------|
| `ANTHROPIC_API_KEY` | Tu API key de Anthropic (sk-ant-...) |
| `OPENAI_API_KEY` | Tu API key de OpenAI (sk-...) |

3. Marca ambas como **Encrypt** para seguridad
4. Click en **Save and Deploy**

## Paso 5: Obtener la URL del Worker

Tu Worker estará disponible en:
```
https://euskera-tutor.TU_SUBDOMINIO.workers.dev
```

Por ejemplo, si tu subdominio es `francisco-lopez`:
```
https://euskera-tutor.francisco-lopez.workers.dev
```

## Paso 6: Actualizar la aplicación

Edita estos archivos con tu URL:

### js/api.js (línea 8)
```javascript
workerUrl: 'https://euskera-tutor.TU_SUBDOMINIO.workers.dev',
```

### js/speech.js (línea 24)
```javascript
workerUrl: 'https://euskera-tutor.TU_SUBDOMINIO.workers.dev'
```

## Paso 7: Probar

1. Abre `index.html` en tu navegador
2. Escribe "Kaixo" en el chat
3. Deberías recibir una respuesta de Iker

## Obtener API Keys

### Anthropic API Key
1. Ve a [console.anthropic.com](https://console.anthropic.com/)
2. Crea cuenta o inicia sesión
3. Ve a **API Keys**
4. Click en **Create Key**
5. Copia la key (empieza con `sk-ant-`)

### OpenAI API Key (para TTS)
1. Ve a [platform.openai.com](https://platform.openai.com/)
2. Crea cuenta o inicia sesión
3. Ve a **API Keys**
4. Click en **Create new secret key**
5. Copia la key (empieza con `sk-`)

## Costos aproximados

| Servicio | Costo |
|----------|-------|
| Cloudflare Workers | Gratis (100k req/día) |
| Claude API | ~$0.003 por mensaje corto |
| OpenAI TTS | ~$0.015 por minuto de audio |

Para uso personal educativo, el costo es mínimo (unos pocos dólares al mes).

## Troubleshooting

### Error CORS
Si ves errores de CORS, verifica que el Worker tenga los headers correctos en la respuesta.

### Error 401
API key incorrecta o expirada. Verifica las variables de entorno.

### Error 500
Revisa los logs del Worker en el dashboard de Cloudflare.

### Sin respuesta de voz
- Verifica OPENAI_API_KEY
- El navegador puede bloquear autoplay de audio
- Prueba con auriculares conectados

---

## Reutilizar Worker existente

Si ya tienes el Worker de `english-tutor`, puedes:

1. **Opción A:** Crear un nuevo Worker `euskera-tutor`
2. **Opción B:** Reutilizar el mismo Worker (el código es idéntico)

Si eliges la opción B, simplemente usa la misma URL:
```javascript
workerUrl: 'https://english-tutor.francisco-lopez.workers.dev'
```

El Worker es genérico y funciona para cualquier idioma.
