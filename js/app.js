/**
 * APP.JS - Logica principal de la aplicacion
 * Euskera Tutor A1 - Iker
 */

const App = {
    // Estado de la aplicacion
    state: {
        currentLesson: null,
        currentSection: 'grammar',
        lessons: [],
        isLoading: false
    },

    // Elementos DOM
    elements: {},

    /**
     * Inicializa la aplicacion
     */
    async init() {
        console.log('Euskera Tutor A1 abiarazten...');

        // Cachear elementos DOM
        this.cacheElements();

        // Cargar datos del curso
        await this.loadCourseData();

        // Renderizar navegacion
        this.renderLessonsNav();

        // Configurar event listeners
        this.setupEventListeners();

        // Inicializar modulos
        SpeechManager.init();
        PodcastPlayer.init();

        // Configurar callbacks de Speech
        this.setupSpeechCallbacks();

        // Seleccionar leccion 1 por defecto
        if (this.state.lessons.length > 0) {
            this.selectLesson(1);
        }

        console.log('Euskera Tutor A1 hasieratu da');
    },

    /**
     * Cachea elementos DOM frecuentes
     */
    cacheElements() {
        this.elements = {
            lessonsNav: document.getElementById('lessonsNav'),
            lessonTitle: document.getElementById('lessonTitle'),
            lessonDescription: document.getElementById('lessonDescription'),
            sectionTabs: document.getElementById('sectionTabs'),
            sectionContent: document.getElementById('sectionContent'),
            chatMessages: document.getElementById('chatMessages'),
            chatInput: document.getElementById('chatInput'),
            sendBtn: document.getElementById('sendBtn'),
            voiceBtn: document.getElementById('voiceBtn'),
            voiceText: document.getElementById('voiceText'),
            voiceStatus: document.getElementById('voiceStatus'),
            autoVoice: document.getElementById('autoVoice'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText')
        };
    },

    /**
     * Carga los datos del curso
     */
    async loadCourseData() {
        try {
            const response = await fetch('data/course.json');
            const data = await response.json();
            this.state.lessons = data.lessons;
            console.log('Ikastaroko datuak kargatuta:', this.state.lessons.length, 'ikasgai');
        } catch (error) {
            console.warn('Ezin izan da course.json kargatu, datu lehenetsiak erabiliz');
            this.state.lessons = this.getDefaultLessons();
        }
    },

    /**
     * Datos por defecto si no hay course.json
     */
    getDefaultLessons() {
        return [
            {
                id: 1,
                title: "Kaixo! Aurkezpenak",
                description: "Saludos y presentaciones basicas",
                completed: false,
                sections: { grammar: true, vocabulary: true, practice: true, test: true }
            },
            { id: 2, title: "Familia eta Lagunak", description: "Familia y amigos", completed: false },
            { id: 3, title: "Nire Etxea", description: "Mi casa", completed: false },
            { id: 4, title: "Eguneroko Bizitza", description: "Vida cotidiana", completed: false },
            { id: 5, title: "Janaria eta Edaria", description: "Comida y bebida", completed: false },
            { id: 6, title: "Hiria eta Garraioa", description: "Ciudad y transporte", completed: false },
            { id: 7, title: "Erosketak", description: "Compras", completed: false },
            { id: 8, title: "Osasuna eta Gorputza", description: "Salud y cuerpo", completed: false },
            { id: 9, title: "Aisialdia", description: "Tiempo libre", completed: false },
            { id: 10, title: "Denbora eta Eguraldia", description: "Tiempo y clima", completed: false },
            { id: 11, title: "Lana eta Ikasketak", description: "Trabajo y estudios", completed: false },
            { id: 12, title: "Birpasa eta Praktika", description: "Repaso y practica", completed: false }
        ];
    },

    /**
     * Renderiza la navegacion de lecciones
     */
    renderLessonsNav() {
        const nav = this.elements.lessonsNav;
        nav.innerHTML = '';

        this.state.lessons.forEach(lesson => {
            const btn = document.createElement('button');
            btn.className = `lesson-btn ${lesson.completed ? 'completed' : ''} ${this.state.currentLesson?.id === lesson.id ? 'active' : ''}`;
            btn.dataset.lessonId = lesson.id;
            btn.textContent = `${lesson.id}. ${lesson.title}`;
            btn.addEventListener('click', () => this.selectLesson(lesson.id));
            nav.appendChild(btn);
        });

        this.updateProgress();
    },

    /**
     * Selecciona una leccion
     * @param {number} lessonId - ID de la leccion
     */
    async selectLesson(lessonId) {
        const lesson = this.state.lessons.find(l => l.id === lessonId);
        if (!lesson) return;

        this.state.currentLesson = lesson;

        // Actualizar UI
        this.elements.lessonTitle.textContent = `${lesson.id}. ikasgaia: ${lesson.title}`;
        this.elements.lessonDescription.textContent = lesson.description;

        // Actualizar navegacion
        document.querySelectorAll('.lesson-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.lessonId) === lessonId);
        });

        // Cargar contenido de la seccion actual
        await this.loadSection(this.state.currentSection);

        // Cargar podcast
        PodcastPlayer.load(lessonId);

        // Informar a la API del contexto
        API.setLessonContext(lesson);

        console.log('Ikasgai hautatua:', lesson.title);
    },

    /**
     * Carga el contenido de una seccion
     * @param {string} section - Nombre de la seccion
     */
    async loadSection(section) {
        this.state.currentSection = section;

        // Actualizar tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.section === section);
        });

        // Mostrar loading
        this.elements.sectionContent.innerHTML = '<div class="loading"></div>';

        try {
            const lessonId = this.state.currentLesson?.id;
            if (!lessonId) {
                throw new Error('Ez dago ikasgairik hautatuta');
            }

            // Intentar cargar contenido del archivo
            const response = await fetch(`content/lesson-${lessonId}/${section}.html`);

            if (response.ok) {
                const content = await response.text();
                this.elements.sectionContent.innerHTML = content;
            } else {
                // Usar contenido por defecto
                this.elements.sectionContent.innerHTML = this.getDefaultSectionContent(section);
            }

            // Setup interactivo segun la seccion
            this.setupSectionInteractivity(section);

        } catch (error) {
            console.warn('Errorea sekzioa kargatzean:', error);
            this.elements.sectionContent.innerHTML = this.getDefaultSectionContent(section);
        }
    },

    /**
     * Contenido por defecto para cada seccion
     * @param {string} section - Nombre de la seccion
     */
    getDefaultSectionContent(section) {
        const lesson = this.state.currentLesson;
        if (!lesson) return '<p>Aukeratu ikasgai bat hasteko.</p>';

        const contents = {
            grammar: `
                <h3>Gramatika: ${lesson.title}</h3>
                <div class="box-importante">
                    <span class="tag tag-importante">GARRANTZITSUA</span>
                    <p>Ikasgai honen gramatika edukia ikastaroko fitxategietatik kargatuko da.</p>
                    <p>Bitartean, tutoreari galdetu dezakezu gai honi buruz txatean.</p>
                </div>
                <div class="box-info">
                    <span class="tag tag-info">AHOLKUA</span>
                    <p>Erabili txata praktikatzeko. Adibidez, galdetu: "Azaldu ${lesson.title}"</p>
                </div>
            `,
            vocabulary: `
                <h3>Hiztegia: ${lesson.title}</h3>
                <div class="vocab-grid">
                    <div class="vocab-card">
                        <div class="vocab-word">kaixo</div>
                        <div class="vocab-phonetic">/kai-sho/</div>
                        <div class="vocab-translation">hola</div>
                        <div class="vocab-example">"Kaixo, zer moduz?"</div>
                        <button class="vocab-speak-btn" onclick="SpeechManager.speak('kaixo')">&#128266; Entzun</button>
                    </div>
                </div>
                <div class="box-complementario">
                    <span class="tag tag-complementario">OHARRA</span>
                    <p>Hiztegia osoa ikastaroko fitxategietatik kargatuko da.</p>
                </div>
            `,
            practice: `
                <h3>Praktika: ${lesson.title}</h3>
                <div class="exercise">
                    <div class="exercise-question">
                        <p>Praktika ariketak ikastaroko fitxategietatik kargatuko dira.</p>
                    </div>
                </div>
                <div class="box-info">
                    <span class="tag tag-info">PRAKTIKA AHOLKUA</span>
                    <p>Erabili txata tutorearekin praktikatzeko. Idatzi zerbait ${lesson.title} erabiliz eta tutoreak zuzenduko zaitu behar izanez gero.</p>
                </div>
            `,
            test: `
                <h3>Azterketa: ${lesson.title}</h3>
                <div class="box-importante">
                    <span class="tag tag-importante">AZTERKETA</span>
                    <p>Ikasgai honen azterketa eskuragarri egongo da Gramatika, Hiztegia eta Praktika atalak osatu ondoren.</p>
                </div>
                <div class="test-results hidden" id="testResults">
                    <div class="test-score">0%</div>
                    <p>Zure puntuazioa hemen agertuko da azterketa osatu ondoren.</p>
                </div>
            `
        };

        return contents[section] || '<p>Edukia ez dago eskuragarri.</p>';
    },

    /**
     * Configura la interactividad de cada seccion
     * @param {string} section - Nombre de la seccion
     */
    setupSectionInteractivity(section) {
        switch (section) {
            case 'vocabulary':
                // Los botones de pronunciacion ya tienen onclick inline
                break;
            case 'practice':
                this.setupPracticeExercises();
                break;
            case 'test':
                this.setupTest();
                break;
        }
    },

    /**
     * Configura ejercicios de practica
     */
    setupPracticeExercises() {
        document.querySelectorAll('.exercise-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const exercise = e.target.closest('.exercise');
                const options = exercise.querySelectorAll('.exercise-option');
                const feedback = exercise.querySelector('.exercise-feedback');
                const isCorrect = option.dataset.correct === 'true';

                // Desmarcar otras opciones
                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');

                // Mostrar si es correcta o no
                if (isCorrect) {
                    option.classList.add('correct');
                    feedback?.classList.add('correct', 'show');
                    feedback?.classList.remove('incorrect');
                } else {
                    option.classList.add('incorrect');
                    feedback?.classList.add('incorrect', 'show');
                    feedback?.classList.remove('correct');
                }
            });
        });
    },

    /**
     * Configura el test
     */
    setupTest() {
        // TODO: Implementar logica de test
    },

    /**
     * Configura event listeners generales
     */
    setupEventListeners() {
        // Tabs de seccion
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => this.loadSection(btn.dataset.section));
        });

        // Chat - Enviar por click
        this.elements.sendBtn?.addEventListener('click', () => this.sendChatMessage());

        // Chat - Enviar por Enter
        this.elements.chatInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });

        // Boton de voz
        this.elements.voiceBtn?.addEventListener('click', () => this.toggleVoice());
    },

    /**
     * Configura callbacks del Speech Manager
     */
    setupSpeechCallbacks() {
        SpeechManager.onStart = () => {
            this.elements.voiceBtn?.classList.add('listening');
            this.elements.voiceBtn?.classList.remove('processing', 'speaking', 'error');
            this.elements.voiceText.textContent = 'ENTZUTEN...';
            this.elements.voiceStatus.textContent = 'Hitz egin orain';
            this.elements.voiceStatus.className = 'voice-status listening';
        };

        SpeechManager.onEnd = () => {
            this.elements.voiceBtn?.classList.remove('listening');
            if (!this.state.isLoading) {
                this.elements.voiceText.textContent = 'HITZ EGIN';
                this.elements.voiceStatus.textContent = 'PREST';
                this.elements.voiceStatus.className = 'voice-status';
            }
        };

        SpeechManager.onResult = (finalTranscript, interimTranscript) => {
            if (finalTranscript) {
                this.elements.chatInput.value = finalTranscript;
                this.sendChatMessage();
            } else if (interimTranscript) {
                this.elements.chatInput.value = interimTranscript;
            }
        };

        SpeechManager.onError = (error) => {
            this.elements.voiceBtn?.classList.add('error');
            this.elements.voiceBtn?.classList.remove('listening', 'processing', 'speaking');
            this.elements.voiceText.textContent = 'ERROREA';
            this.elements.voiceStatus.textContent = error;
            this.elements.voiceStatus.className = 'voice-status error';

            setTimeout(() => {
                this.elements.voiceBtn?.classList.remove('error');
                this.elements.voiceText.textContent = 'HITZ EGIN';
                this.elements.voiceStatus.textContent = 'PREST';
                this.elements.voiceStatus.className = 'voice-status';
            }, 3000);
        };

        SpeechManager.onSpeakStart = () => {
            this.elements.voiceBtn?.classList.add('speaking');
            this.elements.voiceBtn?.classList.remove('listening', 'processing', 'error');
            this.elements.voiceText.textContent = 'HITZ EGITEN...';
            this.elements.voiceStatus.textContent = 'Entzun';
            this.elements.voiceStatus.className = 'voice-status speaking';
        };

        SpeechManager.onSpeakEnd = () => {
            this.elements.voiceBtn?.classList.remove('speaking');
            this.elements.voiceText.textContent = 'HITZ EGIN';
            this.elements.voiceStatus.textContent = 'PREST';
            this.elements.voiceStatus.className = 'voice-status';
        };
    },

    /**
     * Alterna el reconocimiento de voz
     */
    toggleVoice() {
        if (SpeechManager.isListening) {
            SpeechManager.stopListening();
        } else {
            SpeechManager.startListening();
        }
    },

    /**
     * Envia un mensaje de chat
     */
    async sendChatMessage() {
        const message = this.elements.chatInput.value.trim();
        if (!message) return;

        // Limpiar input
        this.elements.chatInput.value = '';

        // Anadir mensaje del usuario al chat
        this.addChatMessage('user', message);

        // Mostrar estado de procesamiento
        this.state.isLoading = true;
        this.elements.voiceBtn?.classList.add('processing');
        this.elements.voiceBtn?.classList.remove('listening', 'speaking', 'error');
        this.elements.voiceText.textContent = 'PENTSATZEN...';
        this.elements.voiceStatus.textContent = 'Prozesatzen';
        this.elements.voiceStatus.className = 'voice-status processing';

        try {
            // Enviar a la API
            const response = await API.sendMessage(message, {
                lesson: this.state.currentLesson,
                section: this.state.currentSection
            });

            // Anadir respuesta al chat
            this.addChatMessage('tutor', response);

            // Leer respuesta en voz alta si esta activado
            if (this.elements.autoVoice?.checked) {
                SpeechManager.speak(response);
            }

        } catch (error) {
            console.error('Errorea:', error);
            this.addChatMessage('tutor', 'Barkatu, errore bat gertatu da. Saiatu berriro mesedez.');
        } finally {
            this.state.isLoading = false;
            if (!SpeechManager.isSpeaking) {
                this.elements.voiceBtn?.classList.remove('processing');
                this.elements.voiceText.textContent = 'HITZ EGIN';
                this.elements.voiceStatus.textContent = 'PREST';
                this.elements.voiceStatus.className = 'voice-status';
            }
        }
    },

    /**
     * Anade un mensaje al chat
     * @param {string} author - 'user' o 'tutor'
     * @param {string} text - Texto del mensaje
     */
    addChatMessage(author, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${author === 'user' ? 'user-message' : 'tutor-message'}`;

        messageDiv.innerHTML = `
            <span class="message-author">${author === 'user' ? 'Zu:' : 'Iker:'}</span>
            <p>${text}</p>
        `;

        this.elements.chatMessages.appendChild(messageDiv);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    },

    /**
     * Actualiza la barra de progreso
     */
    updateProgress() {
        const completed = this.state.lessons.filter(l => l.completed).length;
        const total = this.state.lessons.length;
        const percent = (completed / total) * 100;

        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.progressText.textContent = `${completed} / ${total} osatuta`;
    },

    /**
     * Marca una leccion como completada
     * @param {number} lessonId - ID de la leccion
     */
    completeLesson(lessonId) {
        const lesson = this.state.lessons.find(l => l.id === lessonId);
        if (lesson) {
            lesson.completed = true;
            this.renderLessonsNav();
            this.saveCourseProgress();
        }
    },

    /**
     * Guarda el progreso en localStorage
     */
    saveCourseProgress() {
        const progress = this.state.lessons.map(l => ({
            id: l.id,
            completed: l.completed
        }));
        localStorage.setItem('euskeraTutorProgress', JSON.stringify(progress));
    },

    /**
     * Carga el progreso desde localStorage
     */
    loadCourseProgress() {
        try {
            const saved = localStorage.getItem('euskeraTutorProgress');
            if (saved) {
                const progress = JSON.parse(saved);
                progress.forEach(p => {
                    const lesson = this.state.lessons.find(l => l.id === p.id);
                    if (lesson) lesson.completed = p.completed;
                });
            }
        } catch (error) {
            console.warn('Errorea aurrerapena kargatzean:', error);
        }
    }
};

// Iniciar cuando el DOM este listo
document.addEventListener('DOMContentLoaded', () => App.init());

// Exportar
window.App = App;
