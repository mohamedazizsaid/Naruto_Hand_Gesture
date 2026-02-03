"""
Naruto Jutsu Trainer - Main Application
Affiche 5 gestes aléatoires que l'utilisateur doit reproduire pour débloquer le Rasengan!
"""

import cv2
import numpy as np
import time
import random
import os
from typing import Optional, List, Tuple

from config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_INDEX
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer, GestureStabilizer
from visual_effects import UIRenderer, ParticleSystem, GlowEffect
from sound_effects import JutsuSoundEffects

# Mapping des images aux noms de gestes (7 gestes faciles)
IMAGE_TO_GESTURE = {
    'image1.png': 'dragon',   # Pouces + auriculaires (rock)
    'image2.png': 'tiger',    # Index + majeurs levés
    'image3.png': 'dog',      # Poing gauche + main droite ouverte
    'image6.png': 'horse',    # Index pointés
    'image7.png': 'monkey',   # Mains ouvertes
    'image9.png': 'ox',       # Pouces levés
    'image10.png': 'snake',   # Poings fermés
}

GESTURE_TO_IMAGE = {v: k for k, v in IMAGE_TO_GESTURE.items()}


class RasenganChallenge:
    """Application principale pour le défi Rasengan."""
    
    def __init__(self):
        print("🍥 Démarrage du Naruto Jutsu Trainer...")
        
        # Composants
        self.cap = None
        self.hand_detector = None
        self.gesture_recognizer = None
        self.gesture_stabilizer = None
        self.ui_renderer = None
        self.sound_effects = None
        
        # État du jeu
        self.running = False
        self.gesture_images = {}  # Images chargées
        self.target_sequence = []  # 5 gestes à faire
        self.current_progress = 0  # Progression (0-5)
        self.last_confirmed_gesture = None
        self.show_rasengan_effect = False
        self.rasengan_start_time = 0
        
        # Performance
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        
        # Dimensions
        self.frame_width = WINDOW_WIDTH
        self.frame_height = WINDOW_HEIGHT
    
    def load_gesture_images(self):
        """Charge les images des gestes depuis assets/images."""
        images_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images')
        
        for filename, gesture_name in IMAGE_TO_GESTURE.items():
            filepath = os.path.join(images_dir, filename)
            if os.path.exists(filepath):
                img = cv2.imread(filepath)
                if img is not None:
                    # Redimensionner pour l'affichage
                    img = cv2.resize(img, (100, 100))
                    self.gesture_images[gesture_name] = img
                    print(f"  ✓ Chargé: {gesture_name}")
                else:
                    print(f"  ✗ Erreur lecture: {filename}")
            else:
                print(f"  ✗ Non trouvé: {filename}")
        
        print(f"  Total: {len(self.gesture_images)} images chargées")
    
    def generate_new_sequence(self):
        """Génère une nouvelle séquence de 5 gestes aléatoires."""
        available_gestures = list(self.gesture_images.keys())
        if len(available_gestures) >= 5:
            self.target_sequence = random.sample(available_gestures, 5)
        else:
            self.target_sequence = random.choices(available_gestures, k=5)
        
        self.current_progress = 0
        self.show_rasengan_effect = False
        print(f"\n🎯 Nouvelle séquence: {' → '.join(self.target_sequence)}")
    
    def initialize(self) -> bool:
        """Initialise tous les composants."""
        print("Initialisation...")
        
        # Charger les images
        print("\nChargement des images de gestes:")
        self.load_gesture_images()
        
        if not self.gesture_images:
            print("ERREUR: Aucune image de geste trouvée!")
            return False
        
        # Caméra
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            print("ERREUR: Impossible d'ouvrir la caméra")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"\nCaméra: {self.frame_width}x{self.frame_height}")
        
        # Détecteur de mains
        self.hand_detector = HandDetector(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Reconnaissance de gestes
        self.gesture_recognizer = GestureRecognizer(
            confidence_threshold=0.80,
            hold_time=0.4,
            cooldown=0.5
        )
        self.gesture_stabilizer = GestureStabilizer(buffer_size=10)
        
        # UI et effets
        self.ui_renderer = UIRenderer(self.frame_width, self.frame_height)
        self.sound_effects = JutsuSoundEffects(enabled=True)
        
        # Générer la première séquence
        self.generate_new_sequence()
        
        # Fenêtre
        cv2.namedWindow("Naruto Jutsu Trainer", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Naruto Jutsu Trainer", WINDOW_WIDTH, WINDOW_HEIGHT)
        
        print("\n" + "="*50)
        print("🎮 CONTRÔLES:")
        print("  Q/ESC - Quitter")
        print("  R - Nouvelle séquence")
        print("  ESPACE - Confirmer geste")
        print("="*50)
        print("\n🍥 Reproduisez les 5 gestes pour débloquer le RASENGAN!")
        
        return True
    
    def run(self):
        """Boucle principale."""
        if not self.initialize():
            return
        
        self.running = True
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Miroir
            frame = cv2.flip(frame, 1)
            
            # Traitement
            frame = self.process_frame(frame)
            
            # FPS
            self.update_fps()
            
            # Affichage
            cv2.imshow("Naruto Jutsu Trainer", frame)
            
            # Entrées
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('r'):
                self.restart_game()
            elif key == ord(' '):
                # Si effet Rasengan affiché, recommencer
                if self.show_rasengan_effect:
                    self.restart_game()
                else:
                    self.force_confirm_gesture()
        
        self.cleanup()
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Traite une frame."""
        current_gesture = None
        confidence = 0.0
        
        # Détection des mains
        hands_detected = self.hand_detector.process_frame(frame)
        
        if hands_detected:
            hands = self.hand_detector.get_hands()
            frame = self.hand_detector.draw_landmarks(frame)
            
            # Reconnaissance avec mode hybride (2 mains ou mains jointes)
            result = self.gesture_recognizer.recognize_two_hands(hands, self.hand_detector)
            
            if result:
                current_gesture = result.sign_name
                confidence = result.confidence
                self.gesture_stabilizer.add_gesture(current_gesture, confidence)
                
                # Dessiner les bounding boxes
                for hand in hands:
                    x, y, w, h = hand.bounding_box
                    color = COLORS['success'] if confidence > 0.85 else COLORS['warning']
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Label
                if len(hands) >= 2:
                    center_x = (hands[0].bounding_box[0] + hands[1].bounding_box[0]) // 2
                    center_y = min(hands[0].bounding_box[1], hands[1].bounding_box[1]) - 20
                else:
                    center_x = hands[0].bounding_box[0]
                    center_y = hands[0].bounding_box[1] - 20
                
                label = f"{current_gesture.upper()}: {confidence:.0%}"
                cv2.putText(frame, label, (center_x, center_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['success'], 2)
                
                # Indicateur mains jointes
                if len(hands) == 1:
                    cv2.putText(frame, "[Mains jointes]", 
                               (center_x, center_y + 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['chakra_blue'], 1)
                
                # Vérifier si c'est le bon geste (utiliser le geste stable)
                stable_gesture = self.gesture_stabilizer.get_stable_gesture()
                if result.is_confirmed and stable_gesture:
                    self.check_gesture(stable_gesture)
            else:
                self.gesture_stabilizer.add_gesture(None, 0)
                # Message d'aide
                if len(hands) == 1:
                    x, y, w, h = hands[0].bounding_box
                    if w < 150:  # Main trop petite = une seule main
                        cv2.putText(frame, "Joignez vos DEUX mains!", 
                                   (self.frame_width//2 - 150, self.frame_height - 50),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['chakra_orange'], 2)
                    else:
                        cv2.putText(frame, "Formez un signe...", 
                                   (self.frame_width//2 - 100, self.frame_height - 50),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['warning'], 2)
                elif len(hands) >= 2:
                    cv2.putText(frame, "Rapprochez vos mains!", 
                               (self.frame_width//2 - 150, self.frame_height - 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['warning'], 2)
        else:
            self.gesture_stabilizer.add_gesture(None, 0)
        
        # Obtenir le geste stable pour l'affichage
        stable_gesture = self.gesture_stabilizer.get_stable_gesture()
        if stable_gesture and not current_gesture:
            current_gesture = stable_gesture
        
        # Dessiner l'UI
        frame = self.draw_ui(frame, current_gesture, confidence)
        
        # Effet Rasengan
        if self.show_rasengan_effect:
            frame = self.draw_rasengan_effect(frame)
        
        # Effets visuels
        self.ui_renderer.update_effects()
        self.ui_renderer.draw_effects(frame)
        
        return frame
    
    def check_gesture(self, gesture: str):
        """Vérifie si le geste correspond au geste attendu."""
        if self.show_rasengan_effect:
            return
        
        if self.current_progress >= len(self.target_sequence):
            return
        
        expected = self.target_sequence[self.current_progress]
        
        if gesture == expected and gesture != self.last_confirmed_gesture:
            self.current_progress += 1
            self.last_confirmed_gesture = gesture
            self.sound_effects.play_gesture_confirm()
            print(f"✓ Geste {self.current_progress}/5: {gesture.upper()}")
            
            # Vérifier si la séquence est complète
            if self.current_progress >= 5:
                self.activate_rasengan()
        else:
            self.last_confirmed_gesture = gesture
    
    def force_confirm_gesture(self):
        """Force la confirmation du geste actuel."""
        stable = self.gesture_stabilizer.get_stable_gesture()
        if stable:
            self.check_gesture(stable)
    
    def activate_rasengan(self):
        """Active l'effet Rasengan!"""
        print("\n" + "="*50)
        print("🌀 RASENGAN DÉBLOQUÉ! 🌀")
        print("="*50 + "\n")
        
        self.show_rasengan_effect = True
        self.rasengan_start_time = time.time()
        self.sound_effects.play_jutsu_complete()
        
        # Démarrer l'effet Rasengan réaliste
        center = (self.frame_width // 2, self.frame_height // 2 + 50)
        self.ui_renderer.start_rasengan(center)
        
        # Explosion de particules initiale
        self.ui_renderer.particle_system.emit_burst(
            self.frame_width // 2,
            self.frame_height // 2,
            (255, 200, 100),  # Chakra orange
            count=150,
            spread=15,
            lifetime=2.5
        )
    
    def draw_ui(self, frame: np.ndarray, 
                current_gesture: Optional[str],
                confidence: float) -> np.ndarray:
        """Dessine l'interface utilisateur."""
        
        # === BARRE SUPÉRIEURE ===
        cv2.rectangle(frame, (0, 0), (self.frame_width, 70), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 70), (self.frame_width, 72), COLORS['chakra_blue'], -1)
        
        # Titre
        cv2.putText(frame, "NARUTO JUTSU TRAINER", (self.frame_width//2 - 180, 35),
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, COLORS['chakra_orange'], 2)
        
        # FPS
        cv2.putText(frame, f"FPS: {self.fps}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['success'], 2)
        
        # Progression
        progress_text = f"Progression: {self.current_progress}/5"
        cv2.putText(frame, progress_text, (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['white'], 2)
        
        # Geste actuel
        if current_gesture:
            gesture_text = f"Detecte: {current_gesture.upper()} ({confidence:.0%})"
            cv2.putText(frame, gesture_text, (self.frame_width - 350, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['info'], 2)
        
        # === BARRE INFÉRIEURE - SÉQUENCE DE GESTES ===
        bar_height = 150
        bar_y = self.frame_height - bar_height
        
        # Fond
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, bar_y), (self.frame_width, self.frame_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        # Ligne de séparation
        cv2.rectangle(frame, (0, bar_y), (self.frame_width, bar_y + 2), COLORS['chakra_blue'], -1)
        
        # Titre de la séquence
        cv2.putText(frame, "SEQUENCE RASENGAN:", (20, bar_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['chakra_orange'], 2)
        
        # Afficher les 5 images de la séquence
        img_size = 100
        spacing = 20
        total_width = 5 * img_size + 4 * spacing
        start_x = (self.frame_width - total_width) // 2
        img_y = bar_y + 35
        
        for i, gesture_name in enumerate(self.target_sequence):
            x = start_x + i * (img_size + spacing)
            
            # Cadre
            if i < self.current_progress:
                # Complété - vert
                border_color = COLORS['success']
                border_thickness = 4
            elif i == self.current_progress:
                # Actuel - orange clignotant
                if int(time.time() * 3) % 2:
                    border_color = COLORS['chakra_orange']
                else:
                    border_color = COLORS['warning']
                border_thickness = 4
            else:
                # À venir - gris
                border_color = (100, 100, 100)
                border_thickness = 2
            
            # Dessiner l'image du geste
            if gesture_name in self.gesture_images:
                img = self.gesture_images[gesture_name]
                
                # Assombrir si pas encore atteint
                if i > self.current_progress:
                    img = (img * 0.4).astype(np.uint8)
                
                # Placer l'image
                frame[img_y:img_y+img_size, x:x+img_size] = img
            
            # Bordure
            cv2.rectangle(frame, (x-2, img_y-2), (x+img_size+2, img_y+img_size+2), 
                         border_color, border_thickness)
            
            # Numéro
            num_color = COLORS['success'] if i < self.current_progress else COLORS['white']
            cv2.putText(frame, str(i+1), (x + 5, img_y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, num_color, 2)
            
            # Checkmark si complété
            if i < self.current_progress:
                cv2.putText(frame, "OK", (x + img_size - 30, img_y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['success'], 2)
        
        # Instruction
        if self.current_progress < 5:
            next_gesture = self.target_sequence[self.current_progress]
            instruction = f"Faites le geste: {next_gesture.upper()}"
            cv2.putText(frame, instruction, (self.frame_width//2 - 150, bar_y + img_size + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['white'], 2)
        
        return frame
    
    def draw_rasengan_effect(self, frame: np.ndarray) -> np.ndarray:
        """Dessine l'effet Rasengan réaliste."""
        elapsed = time.time() - self.rasengan_start_time
        
        # Après 4 secondes, afficher le message pour recommencer
        # Ne pas auto-réinitialiser, attendre ESPACE
        waiting_for_restart = elapsed > 4.0
        
        # Phase 1: Flash initial (0-0.5s)
        if elapsed < 0.5:
            flash_alpha = 0.6 * (1 - elapsed * 2)
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (self.frame_width, self.frame_height), 
                         (255, 255, 255), -1)
            cv2.addWeighted(overlay, flash_alpha, frame, 1-flash_alpha, 0, frame)
        
        # Phase 2: Aura de chakra (0.3s+)
        if elapsed > 0.3:
            # Aura bleue diffuse autour de l'écran
            overlay = frame.copy()
            alpha = min(0.15, (elapsed - 0.3) * 0.1)
            
            # Gradient du bord vers le centre
            for i in range(5):
                border = 50 + i * 30
                cv2.rectangle(overlay, (border, border), 
                             (self.frame_width - border, self.frame_height - border),
                             (255, 200, 100), -1)
            cv2.addWeighted(overlay, alpha * 0.3, frame, 1 - alpha * 0.3, 0, frame)
        
        # Texte RASENGAN avec effet
        text = "RASENGAN!"
        
        # Taille pulsante
        base_scale = 2.5
        pulse = 0.3 * np.sin(elapsed * 8)
        scale = base_scale + pulse
        
        # Position
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, 4)[0]
        text_x = (self.frame_width - text_size[0]) // 2
        text_y = 120
        
        # Effet de tremblement pour l'énergie
        shake_x = int(3 * np.sin(elapsed * 30))
        shake_y = int(2 * np.cos(elapsed * 25))
        
        # Glow externe
        for i in range(8, 0, -1):
            glow_alpha = 0.08 / i
            glow_color = (int(255 * glow_alpha), int(180 * glow_alpha), int(50 * glow_alpha))
            cv2.putText(frame, text, (text_x + shake_x - i, text_y + shake_y),
                       cv2.FONT_HERSHEY_DUPLEX, scale, glow_color, 6 + i*2)
            cv2.putText(frame, text, (text_x + shake_x + i, text_y + shake_y),
                       cv2.FONT_HERSHEY_DUPLEX, scale, glow_color, 6 + i*2)
        
        # Ombre
        cv2.putText(frame, text, (text_x + shake_x + 3, text_y + shake_y + 3),
                   cv2.FONT_HERSHEY_DUPLEX, scale, (0, 0, 0), 5)
        
        # Texte principal (gradient simulé)
        # Bleu chakra lumineux
        cv2.putText(frame, text, (text_x + shake_x, text_y + shake_y),
                   cv2.FONT_HERSHEY_DUPLEX, scale, (255, 200, 100), 4)
        
        # Contour blanc
        cv2.putText(frame, text, (text_x + shake_x, text_y + shake_y),
                   cv2.FONT_HERSHEY_DUPLEX, scale, (255, 255, 255), 2)
        
        # Émettre des particules supplémentaires périodiquement
        if not waiting_for_restart and int(elapsed * 10) % 3 == 0:
            self.ui_renderer.particle_system.emit_continuous(
                self.frame_width // 2, 
                self.frame_height // 2 + 50,
                (200, 220, 255),
                rate=3
            )
        
        # Message de félicitations
        if elapsed > 1.5:
            congrats = "JUTSU COMPLETE!"
            c_size = cv2.getTextSize(congrats, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            c_x = (self.frame_width - c_size[0]) // 2
            c_y = self.frame_height // 2 + 50
            
            # Animation de fade-in
            c_alpha = min(1.0, (elapsed - 1.5) * 2)
            c_color = tuple(int(c * c_alpha) for c in COLORS['success'])
            
            cv2.putText(frame, congrats, (c_x + 2, c_y + 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
            cv2.putText(frame, congrats, (c_x, c_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, c_color, 2)
        
        # Message pour recommencer (après 4 secondes)
        if waiting_for_restart:
            # Fond semi-transparent pour le message
            restart_text = "Appuyez sur ESPACE pour recommencer"
            r_size = cv2.getTextSize(restart_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
            r_x = (self.frame_width - r_size[0]) // 2
            r_y = self.frame_height - 80
            
            # Clignotement
            if int(elapsed * 2) % 2 == 0:
                cv2.putText(frame, restart_text, (r_x + 2, r_y + 2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 3)
                cv2.putText(frame, restart_text, (r_x, r_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, COLORS['chakra_orange'], 2)
            
            # Message Q pour quitter
            quit_text = "Q pour quitter"
            q_size = cv2.getTextSize(quit_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            q_x = (self.frame_width - q_size[0]) // 2
            q_y = self.frame_height - 40
            cv2.putText(frame, quit_text, (q_x, q_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['white'], 2)
        
        return frame
    
    def restart_game(self):
        """Redémarre le jeu avec une nouvelle séquence."""
        self.show_rasengan_effect = False
        self.ui_renderer.stop_rasengan()
        self.generate_new_sequence()
        self.last_confirmed_gesture = None
        print("\n🔄 Nouvelle partie!")
    
    def update_fps(self):
        """Met à jour le compteur FPS."""
        self.frame_count += 1
        elapsed = time.time() - self.fps_start_time
        if elapsed >= 1.0:
            self.fps = int(self.frame_count / elapsed)
            self.frame_count = 0
            self.fps_start_time = time.time()
    
    def cleanup(self):
        """Nettoyage des ressources."""
        print("\nFermeture...")
        if self.cap:
            self.cap.release()
        if self.hand_detector:
            self.hand_detector.release()
        if self.sound_effects:
            self.sound_effects.cleanup()
        cv2.destroyAllWindows()
        print("Au revoir! 🍥")


def main():
    app = RasenganChallenge()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrompu")
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
