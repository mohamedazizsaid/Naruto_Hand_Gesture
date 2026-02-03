"""Visual effects for the Jutsu Trainer - Enhanced Realistic Version."""

import cv2
import numpy as np
import time
import random
import math
from typing import List, Tuple


class Particle:
    """Particule réaliste avec physique et effets de lumière."""
    
    def __init__(self, x, y, color, velocity=None, lifetime=2.0, size=3, 
                 gravity=0.15, trail=True, glow=True):
        self.x, self.y = float(x), float(y)
        self.color = color
        self.velocity = list(velocity) if velocity else [random.uniform(-3, 3), random.uniform(-5, -1)]
        self.lifetime = self.max_lifetime = lifetime
        self.initial_size = size
        self.size = size
        self.alpha = 1.0
        self.gravity = gravity
        self.trail = trail
        self.glow = glow
        self.trail_positions = []
        self.rotation = random.uniform(0, 2 * math.pi)
        self.spin = random.uniform(-0.2, 0.2)
    
    def update(self, dt):
        # Sauvegarder position pour trail
        if self.trail and len(self.trail_positions) < 8:
            self.trail_positions.append((self.x, self.y, self.size, self.alpha))
        elif self.trail:
            self.trail_positions.pop(0)
            self.trail_positions.append((self.x, self.y, self.size, self.alpha))
        
        # Physique
        self.velocity[1] += self.gravity  # Gravité
        self.velocity[0] *= 0.99  # Friction air
        self.velocity[1] *= 0.99
        
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        self.lifetime -= dt
        self.alpha = max(0, (self.lifetime / self.max_lifetime) ** 0.5)
        self.size = max(1, int(self.initial_size * self.alpha))
        self.rotation += self.spin
    
    def is_alive(self): 
        return self.lifetime > 0 and self.alpha > 0.01
    
    def draw(self, frame):
        if self.alpha <= 0:
            return
            
        # Dessiner le trail
        if self.trail:
            for i, (tx, ty, ts, ta) in enumerate(self.trail_positions):
                trail_alpha = ta * (i / len(self.trail_positions)) * 0.5
                if trail_alpha > 0.05:
                    trail_color = tuple(int(c * trail_alpha) for c in self.color)
                    trail_size = max(1, int(ts * 0.5))
                    cv2.circle(frame, (int(tx), int(ty)), trail_size, trail_color, -1)
        
        # Glow effect
        if self.glow and self.size > 2:
            for i in range(3, 0, -1):
                glow_alpha = self.alpha * 0.15 / i
                glow_color = tuple(int(c * glow_alpha) for c in self.color)
                glow_size = self.size + i * 3
                cv2.circle(frame, (int(self.x), int(self.y)), glow_size, glow_color, -1)
        
        # Particule principale
        color = tuple(int(c * self.alpha) for c in self.color)
        cv2.circle(frame, (int(self.x), int(self.y)), self.size, color, -1)
        
        # Point lumineux au centre
        if self.size > 3:
            bright_color = tuple(min(255, int(c * self.alpha * 1.5)) for c in self.color)
            cv2.circle(frame, (int(self.x), int(self.y)), max(1, self.size // 3), bright_color, -1)


class ChakraParticle(Particle):
    """Particule de chakra avec effet spirale."""
    
    def __init__(self, x, y, color, center, **kwargs):
        super().__init__(x, y, color, **kwargs)
        self.center = center
        self.angle = math.atan2(y - center[1], x - center[0])
        self.radius = math.sqrt((x - center[0])**2 + (y - center[1])**2)
        self.spiral_speed = random.uniform(3, 6)
        self.expand_speed = random.uniform(1, 3)
    
    def update(self, dt):
        # Mouvement en spirale
        self.angle += self.spiral_speed * dt
        self.radius += self.expand_speed
        
        self.x = self.center[0] + math.cos(self.angle) * self.radius
        self.y = self.center[1] + math.sin(self.angle) * self.radius
        
        self.lifetime -= dt
        self.alpha = max(0, (self.lifetime / self.max_lifetime) ** 0.7)
        self.size = max(1, int(self.initial_size * self.alpha))
        
        # Trail
        if self.trail:
            if len(self.trail_positions) < 12:
                self.trail_positions.append((self.x, self.y, self.size, self.alpha))
            else:
                self.trail_positions.pop(0)
                self.trail_positions.append((self.x, self.y, self.size, self.alpha))


class ParticleSystem:
    """Système de particules amélioré."""
    
    def __init__(self, max_particles=500):
        self.particles = []
        self.max_particles = max_particles
        self.last_update = time.time()
    
    def emit_burst(self, x, y, color, count=50, spread=10, lifetime=2.0):
        """Émet une explosion de particules."""
        for _ in range(min(count, self.max_particles - len(self.particles))):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, spread)
            self.particles.append(Particle(
                x + random.uniform(-10, 10), 
                y + random.uniform(-10, 10), 
                color,
                velocity=[math.cos(angle) * speed, math.sin(angle) * speed],
                lifetime=random.uniform(lifetime * 0.5, lifetime),
                size=random.randint(3, 10),
                gravity=random.uniform(0.05, 0.2),
                trail=True,
                glow=True
            ))
    
    def emit_chakra_spiral(self, center, color, count=30, radius=50):
        """Émet des particules en spirale de chakra."""
        for i in range(min(count, self.max_particles - len(self.particles))):
            angle = (i / count) * 2 * math.pi
            x = center[0] + math.cos(angle) * radius * random.uniform(0.5, 1.0)
            y = center[1] + math.sin(angle) * radius * random.uniform(0.5, 1.0)
            self.particles.append(ChakraParticle(
                x, y, color, center,
                lifetime=random.uniform(1.0, 2.5),
                size=random.randint(4, 8),
                gravity=0,
                trail=True,
                glow=True
            ))
    
    def emit_continuous(self, x, y, color, rate=5):
        """Émet des particules en continu."""
        for _ in range(rate):
            if len(self.particles) < self.max_particles:
                self.particles.append(Particle(
                    x + random.uniform(-20, 20),
                    y + random.uniform(-20, 20),
                    color,
                    velocity=[random.uniform(-1, 1), random.uniform(-3, -1)],
                    lifetime=random.uniform(0.8, 1.5),
                    size=random.randint(2, 5),
                    gravity=-0.1,  # Monte vers le haut
                    trail=True,
                    glow=True
                ))
    
    def update(self):
        dt = time.time() - self.last_update
        self.last_update = time.time()
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive()]
    
    def draw(self, frame):
        for p in self.particles:
            p.draw(frame)


class GlowEffect:
    """Effets de lumière et de brillance."""
    
    @staticmethod
    def draw_glow_text(frame, text, pos, font_scale=1.0, color=(255,255,255), 
                       glow_color=None, thickness=2):
        glow_color = glow_color or tuple(int(c * 0.6) for c in color)
        
        # Glow layers
        for i in range(6, 0, -1):
            alpha = 0.15 / i
            glow_c = tuple(int(c * alpha) for c in glow_color)
            cv2.putText(frame, text, (pos[0] - i, pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, glow_c, thickness + i*2, cv2.LINE_AA)
            cv2.putText(frame, text, (pos[0] + i, pos[1]), cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale, glow_c, thickness + i*2, cv2.LINE_AA)
        
        # Main text
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 
                   color, thickness, cv2.LINE_AA)
    
    @staticmethod
    def draw_glow_circle(frame, center, radius, color, intensity=0.5):
        """Dessine un cercle avec effet de brillance."""
        overlay = frame.copy()
        
        # Glow externe
        for i in range(8, 0, -1):
            glow_radius = radius + i * 8
            alpha = intensity * 0.08 / i
            cv2.circle(overlay, center, glow_radius, color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            overlay = frame.copy()
        
        # Cercle principal
        cv2.circle(frame, center, radius, color, -1)
    
    @staticmethod
    def draw_energy_ring(frame, center, radius, color, thickness=3, segments=60):
        """Dessine un anneau d'énergie animé."""
        t = time.time() * 3
        for i in range(segments):
            angle1 = (i / segments) * 2 * math.pi + t
            angle2 = ((i + 1) / segments) * 2 * math.pi + t
            
            # Variation d'intensité
            intensity = 0.5 + 0.5 * math.sin(angle1 * 3 + t * 2)
            seg_color = tuple(int(c * intensity) for c in color)
            
            x1 = int(center[0] + math.cos(angle1) * radius)
            y1 = int(center[1] + math.sin(angle1) * radius)
            x2 = int(center[0] + math.cos(angle2) * radius)
            y2 = int(center[1] + math.sin(angle2) * radius)
            
            cv2.line(frame, (x1, y1), (x2, y2), seg_color, thickness)


class RasenganEffect:
    """Effet Rasengan réaliste avec spirales et énergie."""
    
    def __init__(self, center, base_radius=60):
        self.center = center
        self.base_radius = base_radius
        self.start_time = time.time()
        self.particles = ParticleSystem(max_particles=300)
        self.spiral_angles = [0, math.pi/2, math.pi, 3*math.pi/2]
    
    def update(self):
        self.particles.update()
        elapsed = time.time() - self.start_time
        
        # Émettre des particules en spirale
        if random.random() < 0.8:
            self.particles.emit_chakra_spiral(
                self.center, 
                (255, 200, 100),  # Orange-jaune chakra
                count=3,
                radius=self.base_radius * 0.3
            )
    
    def draw(self, frame):
        elapsed = time.time() - self.start_time
        pulse = 1.0 + 0.15 * math.sin(elapsed * 12)
        radius = int(self.base_radius * pulse)
        
        # Aura externe diffuse
        for i in range(10, 0, -1):
            aura_radius = radius + i * 12
            alpha = 0.03 / (i * 0.5)
            overlay = frame.copy()
            cv2.circle(overlay, self.center, aura_radius, (255, 180, 50), -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Anneaux d'énergie tournants
        for ring_offset in range(3):
            ring_radius = radius + ring_offset * 20
            GlowEffect.draw_energy_ring(
                frame, self.center, ring_radius, 
                (200, 220, 255), thickness=2, segments=40
            )
        
        # Spirales internes
        num_spirals = 6
        for s in range(num_spirals):
            base_angle = (s / num_spirals) * 2 * math.pi + elapsed * 8
            
            for j in range(25):
                t = j / 25
                r_spiral = radius * t * 0.9
                angle = base_angle + t * 4  # Torsion de la spirale
                
                px = int(self.center[0] + math.cos(angle) * r_spiral)
                py = int(self.center[1] + math.sin(angle) * r_spiral)
                
                # Taille et luminosité décroissantes
                size = max(1, int(6 * (1 - t * 0.7)))
                brightness = 1 - t * 0.3
                color = (
                    int(255 * brightness),
                    int(255 * brightness),
                    int(255 * brightness)
                )
                
                cv2.circle(frame, (px, py), size, color, -1)
        
        # Noyau central brillant
        GlowEffect.draw_glow_circle(frame, self.center, radius // 2, (255, 255, 255), 0.6)
        
        # Reflet central
        cv2.circle(frame, self.center, radius // 4, (255, 255, 255), -1)
        
        # Particules
        self.particles.draw(frame)
        
        return frame


class UIRenderer:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.particle_system = ParticleSystem(max_particles=500)
        self.active_effects = []
        self.rasengan_effect = None
    
    def start_rasengan(self, center):
        """Démarre l'effet Rasengan."""
        self.rasengan_effect = RasenganEffect(center)
    
    def stop_rasengan(self):
        """Arrête l'effet Rasengan."""
        self.rasengan_effect = None
    
    def update_effects(self):
        self.particle_system.update()
        if self.rasengan_effect:
            self.rasengan_effect.update()
    
    def draw_effects(self, frame):
        self.particle_system.draw(frame)
        if self.rasengan_effect:
            self.rasengan_effect.draw(frame)

