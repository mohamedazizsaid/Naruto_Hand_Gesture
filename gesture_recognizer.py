"""Gesture recognition module for Naruto hand signs - Version avec deux mains."""

import time
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Définitions des gestes avec DEUX MAINS - 7 gestes faciles
# Basé sur les vrais signes de Naruto où les deux mains forment ensemble le geste
GESTURE_DEFINITIONS = {
    'tiger': {
        'name': 'Tiger',
        'description': 'Index et majeurs levés des deux mains (pistolet)',
        'left_hand': {'thumb': False, 'index': True, 'middle': True, 'ring': False, 'pinky': False},
        'right_hand': {'thumb': False, 'index': True, 'middle': True, 'ring': False, 'pinky': False},
        'hands_close': True,
        'priority': 10
    },
    'horse': {
        'name': 'Horse',
        'description': 'Index pointés des deux mains',
        'left_hand': {'thumb': False, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'right_hand': {'thumb': False, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'hands_close': True,
        'priority': 10
    },
    'monkey': {
        'name': 'Monkey',
        'description': 'Mains ouvertes (tous doigts levés)',
        'left_hand': {'thumb': True, 'index': True, 'middle': True, 'ring': True, 'pinky': True},
        'right_hand': {'thumb': True, 'index': True, 'middle': True, 'ring': True, 'pinky': True},
        'hands_close': True,
        'priority': 9
    },
    'dog': {
        'name': 'Dog',
        'description': 'Poing gauche + main droite ouverte',
        'left_hand': {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': False},
        'right_hand': {'thumb': True, 'index': True, 'middle': True, 'ring': True, 'pinky': True},
        'hands_close': True,
        'priority': 10
    },
    'snake': {
        'name': 'Snake',
        'description': 'Poings fermés (tous doigts baissés)',
        'left_hand': {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': False},
        'right_hand': {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': False},
        'hands_close': True,
        'priority': 10
    },
    'dragon': {
        'name': 'Dragon',
        'description': 'Pouces et auriculaires levés (rock)',
        'left_hand': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': True},
        'right_hand': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': True},
        'hands_close': True,
        'priority': 10
    },
    'ox': {
        'name': 'Ox',
        'description': 'Pouces levés des deux mains',
        'left_hand': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': False},
        'right_hand': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': False},
        'hands_close': True,
        'priority': 10
    },
}


@dataclass
class GestureResult:
    sign_name: str
    confidence: float
    timestamp: float
    finger_states: Dict[str, bool]
    is_confirmed: bool = False


class GestureRecognizer:
    """Reconnaissance de gestes avec DEUX MAINS - mode hybride pour mains jointes."""
    
    def __init__(self, confidence_threshold=0.75, hold_time=0.5, cooldown=0.6):
        self.confidence_threshold = confidence_threshold
        self.hold_time = hold_time
        self.cooldown = cooldown
        self.current_gesture = None
        self.gesture_start_time = None
        self.last_confirmed_time = 0
        self.last_landmarks = None
        self.hands_distance_threshold = 350  # Distance max entre les mains
        self.single_hand_min_width = 150  # Largeur min pour considérer comme 2 mains jointes
    
    def recognize_two_hands(self, hands: List, detector) -> Optional[GestureResult]:
        """Reconnaissance avec deux mains - mode hybride pour mains très proches."""
        current_time = time.time()
        
        if len(hands) == 0:
            self.current_gesture = None
            self.gesture_start_time = None
            return None
        
        # Mode 2 mains détectées
        if len(hands) >= 2:
            return self._recognize_two_separate_hands(hands, detector, current_time)
        
        # Mode 1 main détectée - vérifier si c'est probablement 2 mains jointes
        if len(hands) == 1:
            return self._recognize_joined_hands(hands[0], detector, current_time)
        
        return None
    
    def _recognize_two_separate_hands(self, hands: List, detector, current_time: float) -> Optional[GestureResult]:
        """Reconnaissance quand 2 mains sont détectées séparément."""
        hand1, hand2 = hands[0], hands[1]
        
        # Identifier main gauche et droite (INVERSER à cause de l'effet miroir!)
        # MediaPipe "Left" = main DROITE de l'utilisateur en miroir
        if hand1.handedness == "Left":
            left_hand, right_hand = hand2, hand1  # Inversé!
        else:
            left_hand, right_hand = hand1, hand2  # Inversé!
        
        # Vérifier que les mains sont proches
        center1 = self._get_center(left_hand.landmarks)
        center2 = self._get_center(right_hand.landmarks)
        distance = math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        if distance > self.hands_distance_threshold:
            self.current_gesture = None
            self.gesture_start_time = None
            return None
        
        # Obtenir l'état des doigts des deux mains
        left_states = detector.get_finger_states(left_hand)
        right_states = detector.get_finger_states(right_hand)
        
        return self._find_best_gesture(left_states, right_states, current_time)
    
    def _recognize_joined_hands(self, hand, detector, current_time: float) -> Optional[GestureResult]:
        """Reconnaissance quand les mains sont tellement jointes qu'une seule est détectée."""
        # Vérifier si la bounding box est assez large (indique 2 mains)
        x, y, w, h = hand.bounding_box
        
        # Si la bounding box est large, c'est probablement 2 mains jointes
        if w >= self.single_hand_min_width:
            # Utiliser les mêmes états pour les deux mains (mains jointes = même position)
            finger_states = detector.get_finger_states(hand)
            
            # Pour les mains jointes, on considère les mêmes états pour gauche et droite
            return self._find_best_gesture(finger_states, finger_states, current_time, joined_mode=True)
        
        # Sinon, vérifier si les landmarks montrent une main avec beaucoup de doigts visibles
        # (indice de mains superposées)
        finger_states = detector.get_finger_states(hand)
        fingers_up = sum(1 for v in finger_states.values() if v)
        
        # Si au moins 3 doigts sont levés et la zone est moyennement grande
        if fingers_up >= 3 and w >= 120:
            return self._find_best_gesture(finger_states, finger_states, current_time, joined_mode=True)
        
        self.current_gesture = None
        self.gesture_start_time = None
        return None
    
    def _find_best_gesture(self, left_states: Dict, right_states: Dict, 
                           current_time: float, joined_mode: bool = False) -> Optional[GestureResult]:
        """Trouve le meilleur geste correspondant."""
        # Calculer les scores pour tous les gestes
        scores = []
        for sign_name, sign_def in GESTURE_DEFINITIONS.items():
            confidence = self._calc_two_hand_confidence(left_states, right_states, sign_def, joined_mode)
            if confidence > 0:
                scores.append((sign_name, confidence, sign_def.get('priority', 5)))
        
        # Trier par confiance puis par priorité
        scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        threshold = self.confidence_threshold - (0.05 if joined_mode else 0)  # Légèrement plus tolérant en mode joint
        
        if scores and scores[0][1] >= threshold:
            best_match = scores[0][0]
            best_confidence = scores[0][1]
            
            combined_states = {**left_states, **{f"right_{k}": v for k, v in right_states.items()}}
            
            result = GestureResult(
                sign_name=best_match,
                confidence=best_confidence,
                timestamp=current_time,
                finger_states=combined_states,
                is_confirmed=False
            )
            
            # Vérifier si le geste est maintenu
            if self.current_gesture and self.current_gesture.sign_name == best_match:
                hold_duration = current_time - self.gesture_start_time
                if hold_duration >= self.hold_time:
                    if current_time - self.last_confirmed_time >= self.cooldown:
                        result.is_confirmed = True
                        self.last_confirmed_time = current_time
            else:
                self.current_gesture = result
                self.gesture_start_time = current_time
            
            return result
        
        self.current_gesture = None
        self.gesture_start_time = None
        return None
    
    def recognize(self, hand, detector) -> Optional[GestureResult]:
        """Méthode legacy pour une seule main - redirige vers two_hands si possible."""
        # Cette méthode est gardée pour compatibilité mais ne fait rien
        # La reconnaissance nécessite maintenant deux mains
        return None
    
    def _get_center(self, landmarks) -> Tuple[float, float]:
        """Obtient le centre d'une main."""
        x = sum(lm[0] for lm in landmarks) / len(landmarks)
        y = sum(lm[1] for lm in landmarks) / len(landmarks)
        return (x, y)
    
    def _calc_two_hand_confidence(self, left_states: Dict, right_states: Dict, 
                                    sign_def: Dict, joined_mode: bool = False) -> float:
        """Calcule la confiance pour un geste à deux mains."""
        
        left_expected = sign_def.get('left_hand', {})
        right_expected = sign_def.get('right_hand', {})
        
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        # Compter les correspondances pour chaque main
        left_matches = 0
        right_matches = 0
        
        for name in finger_names:
            if name in left_expected:
                if left_states.get(name, False) == left_expected[name]:
                    left_matches += 1
            if name in right_expected:
                if right_states.get(name, False) == right_expected[name]:
                    right_matches += 1
        
        # Calculer le score moyen des deux mains
        left_score = left_matches / 5 if left_expected else 1.0
        right_score = right_matches / 5 if right_expected else 1.0
        
        total_score = (left_score + right_score) / 2
        
        # En mode joint (mains très proches), être plus tolérant
        min_matches = 2 if joined_mode else 3
        
        # Bonus pour correspondance parfaite
        if left_matches == 5 and right_matches == 5:
            total_score = 1.0
        elif left_matches >= 4 and right_matches >= 4:
            total_score = max(total_score, 0.85)
        elif left_matches >= 3 and right_matches >= 3:
            total_score = max(total_score, 0.70)
        elif left_matches >= min_matches and right_matches >= min_matches:
            total_score = max(total_score, 0.60)
        elif left_matches < min_matches or right_matches < min_matches:
            return 0  # Pas assez de correspondances
        
        return min(total_score, 1.0)
    
    def _calc_confidence(self, states: Dict[str, bool], sign_def: Dict, landmarks: List) -> float:
        """Legacy - non utilisé."""
        return 0
    
    def _are_fingers_spread(self, landmarks: List) -> bool:
        """Vérifie si les doigts sont écartés."""
        if len(landmarks) < 21:
            return False
        tip_indices = [4, 8, 12, 16, 20]
        total_distance = 0
        for i in range(len(tip_indices) - 1):
            p1 = landmarks[tip_indices[i]]
            p2 = landmarks[tip_indices[i + 1]]
            total_distance += math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        return (total_distance / 4) > 50
    
    def get_hold_progress(self) -> float:
        if not self.gesture_start_time:
            return 0.0
        return min((time.time() - self.gesture_start_time) / self.hold_time, 1.0)
    
    def reset(self):
        self.current_gesture = None
        self.gesture_start_time = None


class GestureStabilizer:
    """Stabilise la reconnaissance en utilisant un buffer et un vote majoritaire."""
    
    def __init__(self, buffer_size=8):
        self.buffer_size = buffer_size
        self.gesture_buffer = []
        self.confidence_buffer = []
    
    def add_gesture(self, gesture_name: Optional[str], confidence: float = 0):
        self.gesture_buffer.append(gesture_name)
        self.confidence_buffer.append(confidence)
        
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
            self.confidence_buffer.pop(0)
    
    def get_stable_gesture(self) -> Optional[str]:
        """Retourne le geste le plus stable avec un vote majoritaire pondéré."""
        if not self.gesture_buffer:
            return None
        
        # Compter les occurrences avec pondération par confiance
        weighted_counts = {}
        for i, gesture in enumerate(self.gesture_buffer):
            if gesture:
                confidence = self.confidence_buffer[i] if i < len(self.confidence_buffer) else 0.5
                weighted_counts[gesture] = weighted_counts.get(gesture, 0) + confidence
        
        if not weighted_counts:
            return None
        
        # Trouver le geste avec le score le plus élevé
        best_gesture = max(weighted_counts, key=weighted_counts.get)
        
        # Vérifier que ce geste apparaît dans au moins 60% du buffer
        count = sum(1 for g in self.gesture_buffer if g == best_gesture)
        if count >= self.buffer_size * 0.6:
            return best_gesture
        
        return None
    
    def clear(self):
        self.gesture_buffer.clear()
        self.confidence_buffer.clear()
    
    def get_consistency(self) -> float:
        """Retourne le niveau de consistance du buffer (0-1)."""
        if not self.gesture_buffer:
            return 0
        
        non_none = [g for g in self.gesture_buffer if g is not None]
        if not non_none:
            return 0
        
        most_common = max(set(non_none), key=non_none.count)
        return non_none.count(most_common) / len(self.gesture_buffer)