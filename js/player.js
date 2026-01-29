/**
 * PLAYER.JS - Reproductor de podcasts
 * Euskera Tutor A1 - Iker
 */

const PodcastPlayer = {
    // Elementos DOM
    audio: null,
    playBtn: null,
    progressBar: null,
    progressFill: null,
    currentTimeEl: null,
    durationEl: null,
    volumeEl: null,

    // Estado
    isPlaying: false,
    currentLesson: null,

    /**
     * Inicializa el reproductor
     */
    init() {
        // Obtener elementos
        this.audio = document.getElementById('podcastAudio');
        this.playBtn = document.getElementById('podcastPlayBtn');
        this.progressBar = document.getElementById('podcastProgressBar');
        this.progressFill = document.getElementById('podcastProgressFill');
        this.currentTimeEl = document.getElementById('podcastCurrentTime');
        this.durationEl = document.getElementById('podcastDuration');
        this.volumeEl = document.getElementById('podcastVolume');

        if (!this.audio) {
            console.error('Audio elementua ez da aurkitu');
            return;
        }

        // Event listeners
        this.setupEventListeners();

        console.log('Podcast Player hasieratuta');
    },

    /**
     * Configura los event listeners
     */
    setupEventListeners() {
        // Play/Pause
        this.playBtn?.addEventListener('click', () => this.togglePlay());

        // Tiempo actualizado
        this.audio.addEventListener('timeupdate', () => this.updateProgress());

        // Duracion cargada
        this.audio.addEventListener('loadedmetadata', () => this.updateDuration());

        // Fin del audio
        this.audio.addEventListener('ended', () => this.onEnded());

        // Error
        this.audio.addEventListener('error', (e) => this.onError(e));

        // Click en barra de progreso
        this.progressBar?.addEventListener('click', (e) => this.seek(e));

        // Volumen
        this.volumeEl?.addEventListener('input', (e) => this.setVolume(e.target.value));

        // Inicializar volumen
        if (this.volumeEl) {
            this.audio.volume = this.volumeEl.value / 100;
        }
    },

    /**
     * Carga un podcast
     * @param {number} lessonId - ID de la leccion
     */
    load(lessonId) {
        const podcastPath = `podcasts/lesson-${lessonId}.mp3`;

        // Verificar si el archivo existe (asumimos que si por ahora)
        this.audio.src = podcastPath;
        this.currentLesson = lessonId;

        // Reset UI
        this.isPlaying = false;
        this.playBtn?.classList.remove('playing');
        this.progressFill.style.width = '0%';
        this.currentTimeEl.textContent = '0:00';
        this.durationEl.textContent = '0:00';

        console.log('Podcasta kargatuta:', podcastPath);
    },

    /**
     * Alterna play/pause
     */
    togglePlay() {
        if (!this.audio.src) {
            console.warn('Ez dago podcastarik kargatuta');
            return;
        }

        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    },

    /**
     * Reproduce el podcast
     */
    play() {
        this.audio.play()
            .then(() => {
                this.isPlaying = true;
                this.playBtn?.classList.add('playing');
            })
            .catch(error => {
                console.error('Errorea erreproduzitzean:', error);
            });
    },

    /**
     * Pausa el podcast
     */
    pause() {
        this.audio.pause();
        this.isPlaying = false;
        this.playBtn?.classList.remove('playing');
    },

    /**
     * Actualiza la barra de progreso
     */
    updateProgress() {
        if (this.audio.duration) {
            const percent = (this.audio.currentTime / this.audio.duration) * 100;
            this.progressFill.style.width = `${percent}%`;
            this.currentTimeEl.textContent = this.formatTime(this.audio.currentTime);
        }
    },

    /**
     * Actualiza la duracion mostrada
     */
    updateDuration() {
        this.durationEl.textContent = this.formatTime(this.audio.duration);
    },

    /**
     * Busca en el audio (seek)
     * @param {Event} e - Evento de click
     */
    seek(e) {
        if (!this.audio.duration) return;

        const rect = this.progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        this.audio.currentTime = percent * this.audio.duration;
    },

    /**
     * Ajusta el volumen
     * @param {number} value - Valor de 0 a 100
     */
    setVolume(value) {
        this.audio.volume = value / 100;
    },

    /**
     * Cuando termina el audio
     */
    onEnded() {
        this.isPlaying = false;
        this.playBtn?.classList.remove('playing');
        this.progressFill.style.width = '0%';
        this.audio.currentTime = 0;
    },

    /**
     * Maneja errores
     * @param {Event} e - Evento de error
     */
    onError(e) {
        console.warn('Errorea podcasta kargatzean:', e);
        this.durationEl.textContent = 'Ez dago';
    },

    /**
     * Formatea segundos a mm:ss
     * @param {number} seconds - Segundos
     * @returns {string} - Tiempo formateado
     */
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';

        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    /**
     * Obtiene el estado actual
     */
    getState() {
        return {
            isPlaying: this.isPlaying,
            currentLesson: this.currentLesson,
            currentTime: this.audio?.currentTime || 0,
            duration: this.audio?.duration || 0
        };
    }
};

// Exportar
window.PodcastPlayer = PodcastPlayer;
