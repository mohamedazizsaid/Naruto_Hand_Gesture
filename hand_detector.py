"""Hand detection module using MediaPipe."""

import cv2
import numpy as np
import mediapipe as mp
from typing import List, Dict, Tuple
from dataclasses import dataclass

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


@dataclass
class HandLandmarks:
    landmarks: List[Tuple[float, float, float]]
    handedness: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]


class HandDetector:
    WRIST = 0
    THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
    INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
    MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
    RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
    PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20
    
    def __init__(self, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=1
        )
        self.results = None
        self.frame_width = 0
        self.frame_height = 0
    
    def process_frame(self, frame: np.ndarray) -> bool:
        self.frame_height, self.frame_width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        return self.results.multi_hand_landmarks is not None
    
    def get_hands(self) -> List[HandLandmarks]:
        if not self.results or not self.results.multi_hand_landmarks:
            return []
        
        hands = []
        for idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
            handedness = "Right"
            confidence = 0.0
            if self.results.multi_handedness:
                handedness = self.results.multi_handedness[idx].classification[0].label
                confidence = self.results.multi_handedness[idx].classification[0].score
            
            landmarks = []
            x_coords, y_coords = [], []
            for lm in hand_landmarks.landmark:
                x = int(lm.x * self.frame_width)
                y = int(lm.y * self.frame_height)
                landmarks.append((x, y, lm.z))
                x_coords.append(x)
                y_coords.append(y)
            
            padding = 20
            bbox = (
                max(0, min(x_coords) - padding),
                max(0, min(y_coords) - padding),
                min(self.frame_width, max(x_coords) - min(x_coords) + 2*padding),
                min(self.frame_height, max(y_coords) - min(y_coords) + 2*padding)
            )
            
            hands.append(HandLandmarks(landmarks, handedness, confidence, bbox))
        return hands
    
    def get_finger_states(self, hand: HandLandmarks) -> Dict[str, bool]:
        """Détection améliorée de l'état des doigts avec marges de tolérance."""
        lm = hand.landmarks
        
        # Calculer la taille de la main pour adapter les seuils
        hand_size = self._get_hand_size(lm)
        threshold = hand_size * 0.05  # 5% de la taille de la main comme marge
        
        # Thumb - comparaison horizontale avec marge
        if hand.handedness == "Right":
            thumb = lm[self.THUMB_TIP][0] < lm[self.THUMB_IP][0] - threshold
        else:
            thumb = lm[self.THUMB_TIP][0] > lm[self.THUMB_IP][0] + threshold
        
        # Autres doigts - comparaison verticale avec marge plus stricte
        # Un doigt est considéré "levé" si le bout est significativement au-dessus du PIP
        index = lm[self.INDEX_TIP][1] < lm[self.INDEX_PIP][1] - threshold
        middle = lm[self.MIDDLE_TIP][1] < lm[self.MIDDLE_PIP][1] - threshold
        ring = lm[self.RING_TIP][1] < lm[self.RING_PIP][1] - threshold
        pinky = lm[self.PINKY_TIP][1] < lm[self.PINKY_PIP][1] - threshold
        
        return {
            'thumb': thumb,
            'index': index,
            'middle': middle,
            'ring': ring,
            'pinky': pinky
        }
    
    def _get_hand_size(self, landmarks) -> float:
        """Calcule la taille approximative de la main."""
        # Distance entre le poignet et le bout du majeur
        wrist = landmarks[self.WRIST]
        middle_tip = landmarks[self.MIDDLE_TIP]
        return ((wrist[0] - middle_tip[0])**2 + (wrist[1] - middle_tip[1])**2)**0.5
    
    def draw_landmarks(self, frame: np.ndarray) -> np.ndarray:
        if not self.results or not self.results.multi_hand_landmarks:
            return frame
        output = frame.copy()
        for hand_landmarks in self.results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                output, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
        return output
    
    def get_hand_center(self, hand: HandLandmarks) -> Tuple[int, int]:
        lm = hand.landmarks
        return (int(np.mean([l[0] for l in lm])), int(np.mean([l[1] for l in lm])))
    
    def release(self):
        self.hands.close()
