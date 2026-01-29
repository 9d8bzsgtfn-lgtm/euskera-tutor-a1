/**
 * SPEECH.JS - Web Speech API para STT + OpenAI TTS
 * Euskera Tutor A1 - Iker
 */

const SpeechManager = {
    // Estado
    isListening: false,
    isSpeaking: false,
    recognition: null,
    synthesis: window.speechSynthesis,
    audioElement: null,

    // Configuracion para Euskera
    config: {
        lang: 'eu-ES',              // Euskera para el reconocimiento
        ttsLang: 'eu-ES',           // Euskera para la sintesis
        ttsRate: 0.85,              // Velocidad mas lenta para A1
        ttsPitch: 1,                // Tono normal
        continuous: false,          // No continuo, para controlar mejor
        interimResults: true,       // Resultados parciales
        useOpenAITTS: true,         // Usar OpenAI TTS en lugar de Web Speech
        ttsVoice: 'onyx',           // Voz de OpenAI para castellano/explicaciones
        workerUrl: 'https://english-tutor.francisco-lopez.workers.dev'
    },

    // Callbacks
    onResult: null,
    onStart: null,
    onEnd: null,
    onError: null,
    onSpeakStart: null,
    onSpeakEnd: null,

    /**
     * Inicializa el reconocimiento de voz
     */
    init() {
        // Verificar soporte
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Speech Recognition no soportado en este navegador');
            return false;
        }

        // Crear instancia
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // Configurar - Nota: eu-ES puede no estar soportado en todos los navegadores
        // Fallback a es-ES para reconocimiento si eu-ES no funciona
        this.recognition.lang = this.config.lang;
        this.recognition.continuous = this.config.continuous;
        this.recognition.interimResults = this.config.interimResults;

        // Eventos
        this.recognition.onstart = () => {
            this.isListening = true;
            if (this.onStart) this.onStart();
        };

        this.recognition.onend = () => {
            this.isListening = false;
            if (this.onEnd) this.onEnd();
        };

        this.recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (this.onResult) {
                this.onResult(finalTranscript, interimTranscript);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech Recognition Error:', event.error);
            this.isListening = false;

            // Si el error es por idioma no soportado, intentar con es-ES
            if (event.error === 'language-not-supported' && this.config.lang === 'eu-ES') {
                console.log('Euskera no soportado, usando espanol para reconocimiento');
                this.recognition.lang = 'es-ES';
            }

            if (this.onError) this.onError(event.error);
        };

        return true;
    },

    /**
     * Inicia el reconocimiento de voz
     */
    startListening() {
        if (!this.recognition) {
            if (!this.init()) {
                return false;
            }
        }

        // Detener TTS si esta hablando
        if (this.isSpeaking) {
            this.stopSpeaking();
        }

        try {
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Error al iniciar reconocimiento:', error);
            return false;
        }
    },

    /**
     * Detiene el reconocimiento de voz
     */
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    },

    /**
     * Sintetiza texto a voz
     * @param {string} text - Texto a hablar
     * @param {object} options - Opciones adicionales
     */
    speak(text, options = {}) {
        // Usar OpenAI TTS si esta habilitado
        if (this.config.useOpenAITTS) {
            return this.speakWithOpenAI(text, options);
        }

        // Fallback a Web Speech API
        return this.speakWithWebSpeech(text, options);
    },

    /**
     * Sintetiza con OpenAI TTS (voz natural)
     */
    async speakWithOpenAI(text, options = {}) {
        try {
            this.isSpeaking = true;
            if (this.onSpeakStart) this.onSpeakStart();

            const response = await fetch(`${this.config.workerUrl}/tts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice: options.voice || this.config.ttsVoice,
                }),
            });

            if (!response.ok) {
                throw new Error('TTS request failed');
            }

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);

            // Crear o reutilizar elemento de audio
            if (!this.audioElement) {
                this.audioElement = new Audio();
            }

            this.audioElement.src = audioUrl;

            this.audioElement.onended = () => {
                this.isSpeaking = false;
                URL.revokeObjectURL(audioUrl);
                if (this.onSpeakEnd) this.onSpeakEnd();
            };

            this.audioElement.onerror = () => {
                this.isSpeaking = false;
                URL.revokeObjectURL(audioUrl);
                console.error('Audio playback error');
                if (this.onSpeakEnd) this.onSpeakEnd();
            };

            await this.audioElement.play();
            return true;

        } catch (error) {
            console.error('OpenAI TTS error:', error);
            this.isSpeaking = false;
            if (this.onSpeakEnd) this.onSpeakEnd();

            // Fallback a Web Speech API
            console.log('Falling back to Web Speech API');
            return this.speakWithWebSpeech(text, options);
        }
    },

    /**
     * Sintetiza con Web Speech API (fallback)
     * Nota: Web Speech API tiene soporte limitado para euskera
     */
    speakWithWebSpeech(text, options = {}) {
        if (!this.synthesis) {
            console.error('Speech Synthesis no soportado');
            return false;
        }

        // Cancelar cualquier sintesis en curso
        this.synthesis.cancel();

        // Crear utterance
        const utterance = new SpeechSynthesisUtterance(text);

        // Intentar usar voz en euskera, fallback a espanol
        utterance.lang = options.lang || this.config.ttsLang;
        utterance.rate = options.rate || this.config.ttsRate;
        utterance.pitch = options.pitch || this.config.ttsPitch;

        // Seleccionar voz (preferir voces en euskera, fallback a espanol)
        const voices = this.synthesis.getVoices();
        const preferredVoice = voices.find(v =>
            v.lang.startsWith('eu')
        ) || voices.find(v =>
            v.lang.startsWith('es-ES') && v.localService
        ) || voices.find(v =>
            v.lang.startsWith('es')
        );

        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        // Eventos
        utterance.onstart = () => {
            this.isSpeaking = true;
            if (this.onSpeakStart) this.onSpeakStart();
        };

        utterance.onend = () => {
            this.isSpeaking = false;
            if (this.onSpeakEnd) this.onSpeakEnd();
        };

        utterance.onerror = (event) => {
            console.error('TTS Error:', event.error);
            this.isSpeaking = false;
            if (this.onSpeakEnd) this.onSpeakEnd();
        };

        // Hablar
        this.synthesis.speak(utterance);
        return true;
    },

    /**
     * Detiene la sintesis de voz
     */
    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
            this.isSpeaking = false;
        }
    },

    /**
     * Obtiene las voces disponibles
     */
    getVoices() {
        return this.synthesis ? this.synthesis.getVoices() : [];
    },

    /**
     * Verifica si el navegador soporta las APIs
     */
    isSupported() {
        return {
            stt: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
            tts: 'speechSynthesis' in window
        };
    }
};

// Cargar voces cuando esten disponibles
if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = () => {
        SpeechManager.getVoices();
    };
}

// Exportar
window.SpeechManager = SpeechManager;
