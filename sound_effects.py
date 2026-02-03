"""Sound effects for the Jutsu Trainer."""

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class JutsuSoundEffects:
    def __init__(self, enabled=True):
        self.enabled = enabled and PYGAME_AVAILABLE
        self.sounds = {}
        if self.enabled:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self._generate_sounds()
            except:
                self.enabled = False
    
    def _generate_sounds(self):
        try:
            import numpy as np
            # Beep de confirmation
            sr = 44100
            t = np.linspace(0, 0.1, int(sr * 0.1), False)
            wave = (np.sin(2 * np.pi * 880 * t) * 0.3 * 32767).astype(np.int16)
            stereo = np.column_stack((wave, wave))
            self.sounds['confirm'] = pygame.sndarray.make_sound(stereo)
            
            # Son de jutsu
            t2 = np.linspace(0, 1.5, int(sr * 1.5), False)
            freq = 100 + 700 * (t2 / 1.5) ** 2
            wave2 = np.sin(2 * np.pi * freq * t2) * 0.4
            wave2 *= np.exp(-(t2 - 0.5) ** 2 * 3)
            wave2 = (wave2 / np.max(np.abs(wave2)) * 0.8 * 32767).astype(np.int16)
            stereo2 = np.column_stack((wave2, wave2))
            self.sounds['jutsu'] = pygame.sndarray.make_sound(stereo2)
        except:
            pass
    
    def play_gesture_confirm(self):
        if self.enabled and 'confirm' in self.sounds:
            try: self.sounds['confirm'].play()
            except: pass
    
    def play_jutsu_complete(self):
        if self.enabled and 'jutsu' in self.sounds:
            try: self.sounds['jutsu'].play()
            except: pass
    
    def cleanup(self):
        if PYGAME_AVAILABLE:
            try: pygame.mixer.quit()
            except: pass
