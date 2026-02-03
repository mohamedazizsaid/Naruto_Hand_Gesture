# 🍥 Naruto Jutsu Trainer

```
                                                                                
    ███╗   ██╗ █████╗ ██████╗ ██╗   ██╗████████╗ ██████╗                        
    ████╗  ██║██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗                       
    ██╔██╗ ██║███████║██████╔╝██║   ██║   ██║   ██║   ██║                       
    ██║╚██╗██║██╔══██║██╔══██╗██║   ██║   ██║   ██║   ██║                       
    ██║ ╚████║██║  ██║██║  ██║╚██████╔╝   ██║   ╚██████╔╝                       
    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝                        
                                                                                
         ╦╦ ╦╔╦╗╔═╗╦ ╦  ╔╦╗╦═╗╔═╗╦╔╗╔╔═╗╦═╗                                     
         ║║ ║ ║ ╚═╗║ ║   ║ ╠╦╝╠═╣║║║║║╣ ╠╦╝                                     
        ╚╝╚═╝ ╩ ╚═╝╚═╝   ╩ ╩╚═╩ ╩╩╝╚╝╚═╝╩╚═                                     
                                                                                
                        🍥 RASENGAN CHALLENGE 🍥                                
                                                                                
                              ░░░░░░░░░                                         
                          ░░░░░░░░░░░░░░░░░                                     
                        ░░░░░░░▓▓▓▓▓░░░░░░░░                                    
                      ░░░░░░▓▓▓▓▓▓▓▓▓▓░░░░░░░                                   
                     ░░░░░▓▓▓▓▓███▓▓▓▓▓░░░░░░░                                  
                    ░░░░░▓▓▓▓██   ██▓▓▓▓░░░░░░                                  
                    ░░░░▓▓▓▓█  ●   █▓▓▓▓░░░░░░                                  
                    ░░░░░▓▓▓██   ██▓▓▓▓░░░░░░░                                  
                     ░░░░░▓▓▓▓███▓▓▓▓▓░░░░░░░                                   
                      ░░░░░░▓▓▓▓▓▓▓▓░░░░░░░░                                    
                        ░░░░░░▓▓▓▓░░░░░░░░                                      
                          ░░░░░░░░░░░░░░                                        
                              ░░░░░░░                                           
```

Application de reconnaissance de gestes en temps réel inspirée de l'univers Naruto. Reproduisez les signes de mains (mudras) pour débloquer le **RASENGAN** !

![Python](https://img.shields.io/badge/Python-3.12-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange)

## 🎮 Fonctionnalités

- **Détection des mains en temps réel** avec MediaPipe
- **Reconnaissance de 7 gestes** inspirés des signes ninja
- **Mode deux mains** - Les gestes nécessitent les deux mains jointes
- **Système de défi** - Reproduisez une séquence de 5 gestes
- **Effets visuels spectaculaires** - Particules, spirales, effet Rasengan
- **Sons de confirmation** - Feedback audio pour chaque geste validé

## 🥷 Les 7 Gestes

| Geste | Description | Position des doigts |
|-------|-------------|---------------------|
| **Tiger** 🐯 | Index + majeurs levés | ✌️ des deux mains |
| **Horse** 🐴 | Index pointés | ☝️ des deux mains |
| **Monkey** 🐵 | Mains ouvertes | 🖐️ tous doigts levés |
| **Dog** 🐕 | Poing + main ouverte | ✊ gauche + 🖐️ droite |
| **Snake** 🐍 | Poings fermés | ✊ des deux mains |
| **Dragon** 🐉 | Pouces + auriculaires | 🤟 signe rock |
| **Ox** 🐂 | Pouces levés | 👍 des deux mains |

## 📋 Prérequis

- Python 3.10 ou supérieur
- Webcam fonctionnelle
- Windows 10/11 (testé sur Windows)

## 🚀 Installation

1. **Cloner ou télécharger le projet**
```bash
cd C:\Users\user\Desktop\Naruto
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install opencv-python numpy mediapipe==0.10.14 pygame
```

## ▶️ Lancement

```bash
python main.py
```

Ou directement avec le chemin complet :
```bash
.\venv\Scripts\python.exe main.py
```

## 🎯 Comment Jouer

1. **Lancez l'application** - La caméra s'active automatiquement
2. **Observez la séquence** - 5 gestes apparaissent en bas de l'écran
3. **Joignez vos deux mains** devant la caméra
4. **Reproduisez chaque geste** dans l'ordre
5. **Maintenez le geste** ~0.5 seconde pour validation
6. **Complétez les 5 gestes** pour débloquer le RASENGAN !
7. **Appuyez sur ESPACE** pour recommencer avec une nouvelle séquence

## ⌨️ Contrôles

| Touche | Action |
|--------|--------|
| `ESPACE` | Confirmer geste / Recommencer après Rasengan |
| `R` | Nouvelle séquence aléatoire |
| `Q` ou `ESC` | Quitter l'application |

## 📁 Structure du Projet

```
Naruto/
├── main.py                 # Application principale
├── config.py               # Configuration (couleurs, dimensions)
├── hand_detector.py        # Détection des mains avec MediaPipe
├── gesture_recognizer.py   # Reconnaissance des gestes
├── visual_effects.py       # Effets visuels (particules, Rasengan)
├── sound_effects.py        # Effets sonores
├── assets/
│   └── images/             # Images des signes de mains
│       ├── image1.png      # Dragon
│       ├── image2.png      # Tiger
│       ├── image3.png      # Dog
│       ├── image6.png      # Horse
│       ├── image7.png      # Monkey
│       ├── image9.png      # Ox
│       └── image10.png     # Snake
├── venv/                   # Environnement virtuel Python
└── README.md               # Ce fichier
```

## 🔧 Configuration

Modifiez `config.py` pour personnaliser :

```python
WINDOW_WIDTH = 1280      # Largeur de la fenêtre
WINDOW_HEIGHT = 720      # Hauteur de la fenêtre
CAMERA_INDEX = 0         # Index de la caméra (0 = webcam par défaut)
```

## 🐛 Résolution des Problèmes

### La caméra ne s'ouvre pas
- Vérifiez que votre webcam est connectée
- Essayez de changer `CAMERA_INDEX` dans `config.py`

### Les gestes ne sont pas détectés
- Assurez-vous d'avoir un bon éclairage
- Placez vos mains bien en face de la caméra
- Joignez vos deux mains ensemble

### Une seule main est détectée
- Rapprochez davantage vos mains
- Le système fonctionne aussi avec les mains jointes

### Erreur MediaPipe
```bash
pip uninstall mediapipe
pip install mediapipe==0.10.14
```

## 📝 Dépendances

- **opencv-python** - Capture vidéo et rendu
- **numpy** - Calculs numériques
- **mediapipe** - Détection des mains et landmarks
- **pygame** - Effets sonores

## 🎨 Crédits

- Inspiré par l'univers **Naruto** de Masashi Kishimoto
- Détection des mains par **Google MediaPipe**
- Effets visuels personnalisés avec **OpenCV**

## 📄 Licence

Ce projet est à usage éducatif et personnel uniquement.

---

**Dattebayo! 🍥**
