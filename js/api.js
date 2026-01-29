/**
 * API.JS - Conexion con Cloudflare Worker (proxy a Claude)
 * Euskera Tutor A1 - Iker
 */

const API = {
    // URL del Worker de Cloudflare (reutiliza el mismo que english-tutor)
    workerUrl: 'https://english-tutor.francisco-lopez.workers.dev',

    // Historial de conversacion
    conversationHistory: [],

    // Contexto del sistema (prompt del tutor Iker)
    systemPrompt: `Eres Iker, tutor virtual de euskera nivel A1 para principiantes absolutos.

PERFIL DEL ESTUDIANTE:
- Nombre: Fran
- Neurodivergente (TEA + Altas Capacidades + rasgos TDAH)
- Hispanohablante adulto
- Nivel: A1 desde cero absoluto
- Necesita estructura clara y predecible
- Respuestas concisas sin relleno innecesario
- Feedback directo sin condescendencia
- NO infantilizar - capacidad intelectual completa

METODOLOGIA DE ENSENANZA DEL EUSKERA:

1. ERGATIVIDAD GRADUAL: El euskera es ergativo. Introduce los casos paso a paso:
   - Primero NOR (absolutivo): sujeto intransitivo, objeto transitivo
   - Luego NORK (ergativo): sujeto transitivo
   - Despues NORI (dativo): objeto indirecto
   - Finalmente locativos: NON, NORA, NONDIK

2. COMPARACION CON CASTELLANO:
   - Senala similitudes (vocabulario de origen latino)
   - Advierte de diferencias (orden SOV, postposiciones)
   - Evita traducciones literales que creen confusion

3. VERBOS AUXILIARES:
   - izan (ser/estar) para verbos intransitivos
   - ukan (haber/tener) para verbos transitivos
   - Practica hasta automatizar las conjugaciones

4. PRONUNCIACION: El euskera tiene ortografia fonetica regular.
   Enfatiza que se pronuncia como se escribe.

IDIOMA DE COMUNICACION:
- Explicaciones en CASTELLANO (es nivel A1)
- Ejemplos y vocabulario en EUSKERA con traduccion
- Instrucciones de ejercicios en castellano
- Feedback positivo mezclado: "Oso ondo! Muy bien!"

FORMATO DE RESPUESTAS:

Para explicaciones gramaticales:
1. Regla clara en 2-3 oraciones
2. Tabla con estructura si es util
3. Ejemplos con traduccion
4. Error comun a evitar
5. Resumen "Sube las antenas" con puntos clave

Para correccion de errores:
1. Tu frase: [lo que escribio]
2. Problema: [explicacion breve]
3. Correccion: [forma correcta]
4. Ejemplo adicional

Para vocabulario:
| Euskera | Pronunciacion | Castellano | Ejemplo |

FRASES UTILES:
- "Kaixo, Fran! Prest?" (Hola Fran, listo?)
- "Oso ondo!" (Muy bien)
- "Hau argi dago?" (Queda claro esto?)
- "Saia zaitez berriro" (Intentalo de nuevo)
- "Primeran!" (Perfecto!)

ADAPTACIONES NEURODIVERGENCIA:
- Estructuras visuales claras (tablas, listas numeradas)
- Explicaciones paso a paso, sin ambiguedades
- Pausas explicitas entre conceptos
- Resumenes frecuentes
- Feedback inmediato y especifico
- Ejemplos concretos, nunca abstractos

REGLAS IMPORTANTES:
- Respuestas concisas (2-4 oraciones para preguntas simples)
- Siempre anima pero se honesto sobre errores
- Usa tablas y formato estructurado cuando ayude
- Confirma comprension antes de avanzar`,

    /**
     * Configura la URL del Worker
     * @param {string} url - URL del Cloudflare Worker
     */
    setWorkerUrl(url) {
        this.workerUrl = url;
        console.log('Worker URL configurado:', url);
    },

    /**
     * Envia un mensaje al tutor
     * @param {string} message - Mensaje del usuario
     * @param {object} context - Contexto adicional (leccion actual, etc.)
     * @returns {Promise<string>} - Respuesta del tutor
     */
    async sendMessage(message, context = {}) {
        // Anadir mensaje del usuario al historial
        this.conversationHistory.push({
            role: 'user',
            content: message
        });

        // Construir contexto adicional si hay leccion activa
        let contextMessage = '';
        if (context.lesson) {
            contextMessage = `\n[Ikasgai aktuala: ${context.lesson.title}]`;
            if (context.section) {
                contextMessage += `\n[Atala: ${context.section}]`;
            }
        }

        try {
            const response = await fetch(this.workerUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    system: this.systemPrompt + contextMessage,
                    messages: this.conversationHistory
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const assistantMessage = data.content || data.message || 'Barkatu, ezin izan dut prozesatu. Saiatu berriro.';

            // Anadir respuesta al historial
            this.conversationHistory.push({
                role: 'assistant',
                content: assistantMessage
            });

            // Limitar historial para no exceder tokens
            if (this.conversationHistory.length > 20) {
                this.conversationHistory = this.conversationHistory.slice(-20);
            }

            return assistantMessage;

        } catch (error) {
            console.error('Error calling API:', error);

            // Si no hay Worker configurado, usar modo demo
            if (this.workerUrl.includes('YOUR_SUBDOMAIN')) {
                return this.getDemoResponse(message);
            }

            throw error;
        }
    },

    /**
     * Respuesta demo cuando no hay Worker configurado
     * @param {string} message - Mensaje del usuario
     */
    getDemoResponse(message) {
        const lowerMessage = message.toLowerCase();

        // Respuestas predefinidas para demo
        const responses = {
            hello: "Kaixo! Oso ondo etorri! Zer moduz? Hoy podemos practicar saludos, numeros, o el verbo izan. Zer nahi duzu? (Que quieres?)",
            help: "Lagundu dezaket honekin:\n- Gramatika: casos, verbos auxiliares\n- Hiztegia: vocabulario por temas\n- Elkarrizketa: practica conversacional\n- Zuzenketak: correccion de frases\n\nGaldetu edozer! (Pregunta lo que quieras!)",
            grammar: "Primeran! Zer gramatika puntu landu nahi duzu? Podemos trabajar:\n- Pronombres (ni, zu, bera...)\n- Verbo izan (naiz, zara, da...)\n- Casos (NOR, NORK, NORI...)\n\nZer nahiago duzu?",
            vocabulary: "Hiztegia praktikatzera! Dame una palabra o tema y te ayudo a aprender vocabulario relacionado. Por ejemplo: familia, etxea (casa), janaria (comida)...",
            default: "Galdera ona! Para darte una respuesta completa, necesito que el Cloudflare Worker este configurado. Mientras tanto, prueba a decir 'kaixo', 'laguntza' (ayuda), 'gramatika' o 'hiztegia' (vocabulario)."
        };

        if (lowerMessage.includes('kaixo') || lowerMessage.includes('hello') || lowerMessage.includes('hola')) {
            return responses.hello;
        } else if (lowerMessage.includes('laguntza') || lowerMessage.includes('help') || lowerMessage.includes('ayuda')) {
            return responses.help;
        } else if (lowerMessage.includes('gramatika') || lowerMessage.includes('grammar')) {
            return responses.grammar;
        } else if (lowerMessage.includes('hiztegia') || lowerMessage.includes('vocabulary') || lowerMessage.includes('vocab')) {
            return responses.vocabulary;
        }

        return responses.default;
    },

    /**
     * Limpia el historial de conversacion
     */
    clearHistory() {
        this.conversationHistory = [];
    },

    /**
     * Actualiza el prompt del sistema con contexto de la leccion
     * @param {object} lesson - Datos de la leccion actual
     */
    setLessonContext(lesson) {
        // El contexto se pasa dinamicamente en cada llamada
        console.log('Lesson context set:', lesson?.title);
    }
};

// Exportar
window.API = API;
