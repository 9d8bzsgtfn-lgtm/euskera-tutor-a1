# Euskera Tutor A1 - Iker

Tutor virtual de euskera nivel A1 (principiante absoluto) con adaptaciones para neurodivergencia.

## Caracteristicas

- **12 lecciones** estructuradas de euskera desde cero
- **Tutor IA** (Iker) integrado con Claude API
- **Reconocimiento de voz** (STT) y sintesis de voz (TTS)
- **Podcasts** de cada leccion
- **Ejercicios interactivos** con feedback inmediato
- **Adaptado para neurodivergencia** (TEA + Altas Capacidades + TDAH)

## Estructura del Proyecto

```
euskera-tutor/
├── index.html                    # Pagina principal
├── css/style.css                 # Estilos (adaptados neurodivergencia)
├── js/
│   ├── app.js                    # Logica principal
│   ├── api.js                    # Integracion Claude API
│   ├── speech.js                 # STT/TTS (eu-ES)
│   └── player.js                 # Reproductor podcasts
├── data/course.json              # Estructura del curso (12 lecciones)
├── content/lesson-{1-12}/        # Contenido por leccion
│   ├── grammar.html
│   ├── vocabulary.html
│   ├── practice.html
│   └── test.html
├── podcasts/                     # MP3 de cada leccion
├── worker/claude-proxy.js        # Cloudflare Worker
└── claude-project/               # Para usar con Claude Projects
    ├── INSTRUCTIONS.md           # Prompt del tutor Iker
    ├── COURSE_OVERVIEW.md        # Descripcion del curso
    └── knowledge/
        ├── grammar_reference.md
        ├── vocabulary_list.md
        └── common_errors.md
```

## Las 12 Lecciones

1. **Kaixo! Aurkezpenak** - Saludos y presentaciones
2. **Familia eta Lagunak** - Familia y amigos
3. **Nire Etxea** - Mi casa
4. **Eguneroko Bizitza** - Vida cotidiana
5. **Janaria eta Edaria** - Comida y bebida
6. **Hiria eta Garraioa** - Ciudad y transporte
7. **Erosketak** - Compras
8. **Osasuna eta Gorputza** - Salud y cuerpo
9. **Aisialdia** - Tiempo libre
10. **Denbora eta Eguraldia** - Tiempo y clima
11. **Lana eta Ikasketak** - Trabajo y estudios
12. **Birpasa eta Praktika** - Repaso y practica

## Instalacion

### 1. Clonar el repositorio
```bash
git clone [url-del-repo]
cd euskera-tutor
```

### 2. Configurar Cloudflare Worker

1. Crear cuenta en [Cloudflare Workers](https://workers.cloudflare.com/)
2. Crear nuevo Worker
3. Copiar contenido de `worker/claude-proxy.js`
4. Configurar variables de entorno:
   - `ANTHROPIC_API_KEY`: Tu API key de Anthropic
   - `OPENAI_API_KEY`: Tu API key de OpenAI (para TTS)
5. Obtener URL del Worker

### 3. Configurar la aplicacion

Editar `js/api.js` y `js/speech.js`:
```javascript
workerUrl: 'https://euskera-tutor.TU_SUBDOMINIO.workers.dev'
```

### 4. Generar podcasts (opcional)

```bash
pip install edge-tts
python scripts/generate_podcast.py --all
```

### 5. Desplegar

Opciones:
- **GitHub Pages**: Push y activar en Settings > Pages
- **Servidor local**: `python -m http.server 8000`
- **Cualquier hosting estatico**: Netlify, Vercel, etc.

## Uso con Claude Projects

Para usar el tutor Iker directamente en claude.ai:

1. Crear nuevo proyecto en Claude
2. Copiar `claude-project/INSTRUCTIONS.md` como Custom Instructions
3. Subir los archivos de `claude-project/knowledge/` como Knowledge
4. Iniciar conversacion con el tutor

## Tecnologias

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Cloudflare Workers
- **IA**: Claude API (Anthropic)
- **TTS**: OpenAI TTS API / Web Speech API
- **STT**: Web Speech API
- **Podcasts**: edge-tts (Microsoft Azure voices)

## Voces TTS para Euskera

El proyecto utiliza:
- **eu-ES-AnderNeural**: Voz masculina (para Iker)
- **eu-ES-AinhoaNeural**: Voz femenina (alternativa)

## Adaptaciones Neurodivergencia

- Estructura visual clara con tablas y listas
- Explicaciones paso a paso sin ambiguedades
- Resumenes "Sube las antenas" al final de cada seccion
- Feedback inmediato y especifico
- Sin infantilizacion
- Colores de alto contraste
- Espaciado generoso

## Licencia

MIT

---

*Ongi etorri euskararen mundura!*
*Bienvenido al mundo del euskera!*
