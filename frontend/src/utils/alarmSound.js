/**
 * Alarm Sound Utility for Water Quality Alerts
 * Uses Web Audio API for browser-native sound generation
 */

class AlarmSound {
  constructor() {
    this.audioContext = null;
    this.isPlaying = false;
    this.oscillator = null;
    this.gainNode = null;
  }

  init() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    return this.audioContext;
  }

  // Critical alarm - loud beeping
  playCriticalAlarm(duration = 3000) {
    if (this.isPlaying) return;
    
    try {
      const ctx = this.init();
      this.isPlaying = true;

      const beepDuration = 200;
      const pauseDuration = 100;
      const frequency = 880; // High pitch for urgency

      let startTime = ctx.currentTime;
      const endTime = startTime + (duration / 1000);

      const playBeep = () => {
        if (ctx.currentTime >= endTime || !this.isPlaying) {
          this.isPlaying = false;
          return;
        }

        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.frequency.value = frequency;
        osc.type = 'square';

        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + beepDuration / 1000);

        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + beepDuration / 1000);

        setTimeout(playBeep, beepDuration + pauseDuration);
      };

      playBeep();

      setTimeout(() => {
        this.isPlaying = false;
      }, duration);

    } catch (error) {
      console.error('Alarm sound error:', error);
      this.isPlaying = false;
    }
  }

  // Warning alarm - gentler tone
  playWarningAlarm(duration = 2000) {
    if (this.isPlaying) return;

    try {
      const ctx = this.init();
      this.isPlaying = true;

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.frequency.value = 440; // A4 note
      osc.type = 'sine';

      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration / 1000);

      osc.start();
      osc.stop(ctx.currentTime + duration / 1000);

      setTimeout(() => {
        this.isPlaying = false;
      }, duration);

    } catch (error) {
      console.error('Warning sound error:', error);
      this.isPlaying = false;
    }
  }

  // Success/notification sound
  playNotification() {
    try {
      const ctx = this.init();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.frequency.value = 523.25; // C5
      osc.type = 'sine';

      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);

      osc.start();
      osc.stop(ctx.currentTime + 0.3);

    } catch (error) {
      console.error('Notification sound error:', error);
    }
  }

  stop() {
    this.isPlaying = false;
    if (this.oscillator) {
      try {
        this.oscillator.stop();
      } catch (e) {}
    }
  }
}

// Singleton instance
const alarmSound = new AlarmSound();

export default alarmSound;

// Helper function to play appropriate alarm based on severity
export const playAlarmForSeverity = (severity) => {
  switch (severity) {
    case 'critical':
      alarmSound.playCriticalAlarm(3000);
      break;
    case 'warning':
      alarmSound.playWarningAlarm(2000);
      break;
    default:
      break;
  }
};

// Check water quality and play alarm if needed
export const checkAndPlayAlarm = (data) => {
  const { ph, turbidity, tds } = data;
  
  // Critical thresholds
  if (ph < 6.0 || ph > 9.0 || turbidity > 50 || tds > 1000) {
    alarmSound.playCriticalAlarm(4000);
    return 'critical';
  }
  
  // Warning thresholds
  if (ph < 6.5 || ph > 8.5 || turbidity > 10 || tds > 500) {
    alarmSound.playWarningAlarm(2000);
    return 'warning';
  }
  
  return 'normal';
};
