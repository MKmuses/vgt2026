#######################################################################################
#          Hyperperimetry VGT Test Animations Generator v1.0 by MKMUses 2026          #
# Generates 12 different GIF animations for saccadic and pursuit sensitivity testing. # 
# Each animation is 300x300 pixels, 25fps, 10 seconds duration (250 frames total).    #
#######################################################################################

import numpy as np
import cv2
from PIL import Image
import os
from random import randint, shuffle, choice
import math

# Global parameters
WIDTH, HEIGHT = 300, 300
FPS = 25
DURATION = 10  # seconds
TOTAL_FRAMES = FPS * DURATION  # 250 frames
FRAME_DURATION_MS = 1000 // FPS  # 40ms per frame

# Common colors (BGR for OpenCV, but we convert to RGB for PIL)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Target parameters
TARGET_RADIUS = 15
SMALL_RADIUS = 5
LARGE_RADIUS = 40

OUTPUT_DIR = "/home/claude/perimetry_gifs"


def create_frame():
    """Create a blank black frame."""
    return np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)


def save_gif(frames, filename):
    """Save frames as a GIF file."""
    pil_frames = [Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)) for f in frames]
    filepath = os.path.join(OUTPUT_DIR, filename)
    pil_frames[0].save(
        filepath,
        save_all=True,
        append_images=pil_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0
    )
    print(f"Saved: {filepath}")
    return filepath


def generate_smooth_pursuit():
    """
    1. Smooth Pursuit: Target moving in a sinusoidal pattern.
    The target moves horizontally while oscillating vertically in a sine wave.
    """
    frames = []
    center_y = HEIGHT // 2
    amplitude = HEIGHT // 3
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        # Horizontal position moves back and forth
        t = i / TOTAL_FRAMES
        cycles = 3  # Number of complete horizontal cycles
        x_progress = (math.sin(2 * math.pi * cycles * t) + 1) / 2
        x = int(TARGET_RADIUS + x_progress * (WIDTH - 2 * TARGET_RADIUS))
        
        # Vertical sinusoidal oscillation
        vertical_cycles = 8
        y = int(center_y + amplitude * math.sin(2 * math.pi * vertical_cycles * t))
        y = max(TARGET_RADIUS, min(HEIGHT - TARGET_RADIUS, y))
        
        cv2.circle(frame, (x, y), TARGET_RADIUS, WHITE, -1)
        frames.append(frame)
    
    return save_gif(frames, "01_smooth_pursuit.gif")


def generate_linear_pursuit():
    """
    2. Linear Pursuit: Target travels in a star path on the screen.
    """
    frames = []
    center = (WIDTH // 2, HEIGHT // 2)
    outer_radius = 120
    inner_radius = 50
    num_points = 5
    
    # Calculate star points
    star_points = []
    angle_step = math.pi / num_points
    for i in range(2 * num_points):
        angle = i * angle_step - math.pi / 2  # Start from top
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = int(center[0] + radius * math.cos(angle))
        y = int(center[1] + radius * math.sin(angle))
        star_points.append((x, y))
    
    # Calculate total path length and segment lengths
    segments = []
    total_length = 0
    for i in range(len(star_points)):
        start = star_points[i]
        end = star_points[(i + 1) % len(star_points)]
        length = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        segments.append((start, end, length))
        total_length += length
    
    for frame_idx in range(TOTAL_FRAMES):
        frame = create_frame()
        
        # Draw the star path
        for i in range(len(star_points)):
            start = star_points[i]
            end = star_points[(i + 1) % len(star_points)]
            cv2.line(frame, start, end, GREEN, 1)
        
        # Calculate position along path
        progress = (frame_idx / TOTAL_FRAMES) * total_length * 2  # 2 complete cycles
        progress = progress % total_length
        
        # Find which segment we're on
        cumulative = 0
        for start, end, length in segments:
            if cumulative + length >= progress:
                t = (progress - cumulative) / length
                x = int(start[0] + t * (end[0] - start[0]))
                y = int(start[1] + t * (end[1] - start[1]))
                break
            cumulative += length
        
        cv2.circle(frame, (x, y), TARGET_RADIUS, WHITE, -1)
        frames.append(frame)
    
    return save_gif(frames, "02_linear_pursuit.gif")


def generate_spsa():
    """
    3. Static Perimetry Sensitivity Assessment (SPSA):
    Single static dots appear, grow, and disappear before the next target appears.
    """
    frames = []
    
    # Generate target positions
    margin = 30
    positions = [
        (margin, margin), (WIDTH//2, margin), (WIDTH-margin, margin),
        (margin, HEIGHT//2), (WIDTH//2, HEIGHT//2), (WIDTH-margin, HEIGHT//2),
        (margin, HEIGHT-margin), (WIDTH//2, HEIGHT-margin), (WIDTH-margin, HEIGHT-margin),
        (WIDTH//4, HEIGHT//4), (3*WIDTH//4, HEIGHT//4),
        (WIDTH//4, 3*HEIGHT//4), (3*WIDTH//4, 3*HEIGHT//4)
    ]
    shuffle(positions)
    
    # Each target cycle: grow (15 frames), hold (5 frames), shrink (5 frames) = 25 frames per target
    # 250 frames / 25 = 10 targets
    frames_per_target = 25
    grow_frames = 15
    hold_frames = 5
    shrink_frames = 5
    
    target_idx = 0
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        cycle_frame = i % frames_per_target
        pos = positions[target_idx % len(positions)]
        
        if cycle_frame < grow_frames:
            # Growing phase
            t = cycle_frame / grow_frames
            radius = int(SMALL_RADIUS + t * (LARGE_RADIUS - SMALL_RADIUS))
        elif cycle_frame < grow_frames + hold_frames:
            # Hold at max size
            radius = LARGE_RADIUS
        else:
            # Shrinking phase
            t = (cycle_frame - grow_frames - hold_frames) / shrink_frames
            radius = int(LARGE_RADIUS - t * (LARGE_RADIUS - SMALL_RADIUS))
        
        cv2.circle(frame, pos, max(1, radius), WHITE, -1)
        frames.append(frame)
        
        if (i + 1) % frames_per_target == 0:
            target_idx += 1
    
    return save_gif(frames, "03_spsa.gif")


def generate_sfe():
    """
    4. Static Fixation Evaluation (SFE):
    A large circle appears on the screen that shrinks into a small dot.
    """
    frames = []
    center = (WIDTH // 2, HEIGHT // 2)
    
    max_radius = 100
    min_radius = 5
    
    # Multiple shrink cycles
    cycles = 5
    frames_per_cycle = TOTAL_FRAMES // cycles
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        cycle_frame = i % frames_per_cycle
        t = cycle_frame / frames_per_cycle
        
        # Shrink from large to small
        radius = int(max_radius - t * (max_radius - min_radius))
        
        # Draw outer ring and filled center
        cv2.circle(frame, center, radius, WHITE, 2)
        cv2.circle(frame, center, min_radius, WHITE, -1)
        
        frames.append(frame)
    
    return save_gif(frames, "04_sfe.gif")


def generate_spa():
    """
    5. Static Perimetry Assessment (SPA):
    Single static dots appear on the screen and stay visible for ~3 seconds.
    """
    frames = []
    
    # Generate target positions
    margin = 30
    positions = [
        (margin, margin), (WIDTH//2, margin), (WIDTH-margin, margin),
        (margin, HEIGHT//2), (WIDTH-margin, HEIGHT//2),
        (margin, HEIGHT-margin), (WIDTH//2, HEIGHT-margin), (WIDTH-margin, HEIGHT-margin),
        (WIDTH//2, HEIGHT//2)
    ]
    shuffle(positions)
    
    # 3 seconds per target at 25fps = 75 frames per target
    # For 10 seconds, we get ~3 targets
    frames_per_target = 75
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        target_idx = i // frames_per_target
        pos = positions[target_idx % len(positions)]
        
        cv2.circle(frame, pos, TARGET_RADIUS, GREEN, -1)
        frames.append(frame)
    
    return save_gif(frames, "05_spa.gif")


def generate_out_of_time():
    """
    6. Out of Time:
    Target appears at the centre, then moves to the edge and back.
    """
    frames = []
    center = (WIDTH // 2, HEIGHT // 2)
    
    # Different directions to edges
    directions = [
        (0, -1),   # Up
        (1, -1),   # Up-right
        (1, 0),    # Right
        (1, 1),    # Down-right
        (0, 1),    # Down
        (-1, 1),   # Down-left
        (-1, 0),   # Left
        (-1, -1),  # Up-left
    ]
    
    # Each cycle: center (10 frames), move out (15 frames), move back (15 frames), center (10 frames) = 50 frames
    frames_per_cycle = 50
    center_hold = 10
    move_frames = 15
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        cycle = i // frames_per_cycle
        cycle_frame = i % frames_per_cycle
        direction = directions[cycle % len(directions)]
        
        # Calculate max distance to edge
        max_dist = min(WIDTH // 2 - TARGET_RADIUS, HEIGHT // 2 - TARGET_RADIUS)
        
        if cycle_frame < center_hold:
            # Hold at center
            pos = center
        elif cycle_frame < center_hold + move_frames:
            # Move out
            t = (cycle_frame - center_hold) / move_frames
            x = int(center[0] + t * direction[0] * max_dist)
            y = int(center[1] + t * direction[1] * max_dist)
            pos = (x, y)
        elif cycle_frame < center_hold + 2 * move_frames:
            # Move back
            t = (cycle_frame - center_hold - move_frames) / move_frames
            x = int(center[0] + (1 - t) * direction[0] * max_dist)
            y = int(center[1] + (1 - t) * direction[1] * max_dist)
            pos = (x, y)
        else:
            # Hold at center
            pos = center
        
        cv2.circle(frame, pos, TARGET_RADIUS, WHITE, -1)
        frames.append(frame)
    
    return save_gif(frames, "06_out_of_time.gif")


def generate_teleporter():
    """
    7. Teleporter:
    Single target moving abruptly disappears and reappears on another line in the same direction.
    """
    frames = []
    
    # Define movement patterns (start, direction)
    patterns = [
        ((TARGET_RADIUS, HEIGHT//2), (1, 0)),    # Left to right
        ((WIDTH-TARGET_RADIUS, HEIGHT//2), (-1, 0)),  # Right to left
        ((WIDTH//2, TARGET_RADIUS), (0, 1)),     # Top to bottom
        ((WIDTH//2, HEIGHT-TARGET_RADIUS), (0, -1)),  # Bottom to top
    ]
    
    speed = 4
    teleport_interval = 15  # Frames between teleports
    
    pattern_idx = 0
    current_pos = list(patterns[0][0])
    direction = patterns[0][1]
    frame_counter = 0
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        # Move target
        current_pos[0] += direction[0] * speed
        current_pos[1] += direction[1] * speed
        
        # Check boundaries
        if (current_pos[0] < TARGET_RADIUS or current_pos[0] > WIDTH - TARGET_RADIUS or
            current_pos[1] < TARGET_RADIUS or current_pos[1] > HEIGHT - TARGET_RADIUS):
            pattern_idx = (pattern_idx + 1) % len(patterns)
            current_pos = list(patterns[pattern_idx][0])
            direction = patterns[pattern_idx][1]
            frame_counter = 0
        
        # Teleport to parallel line
        frame_counter += 1
        if frame_counter >= teleport_interval:
            frame_counter = 0
            if direction[0] != 0:  # Horizontal movement
                current_pos[1] = randint(TARGET_RADIUS + 20, HEIGHT - TARGET_RADIUS - 20)
            else:  # Vertical movement
                current_pos[0] = randint(TARGET_RADIUS + 20, WIDTH - TARGET_RADIUS - 20)
        
        cv2.circle(frame, (int(current_pos[0]), int(current_pos[1])), TARGET_RADIUS, WHITE, -1)
        frames.append(frame)
    
    return save_gif(frames, "07_teleporter.gif")


def generate_popcorn():
    """
    8. Popcorn:
    Single target moving abruptly branches 90° and returns to the line repeatedly.
    """
    frames = []
    
    center_y = HEIGHT // 2
    x = TARGET_RADIUS
    direction = 1  # 1 = right, -1 = left
    speed = 3
    
    # Popcorn parameters
    branch_interval = 20  # Frames between branches
    branch_distance = 40  # How far to branch
    branch_frames = 10    # Frames for each branch movement
    
    frame_counter = 0
    branching = False
    branch_frame = 0
    branch_direction = 1  # 1 = up, -1 = down
    base_y = center_y
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        # Main horizontal movement
        x += direction * speed
        if x > WIDTH - TARGET_RADIUS:
            direction = -1
        elif x < TARGET_RADIUS:
            direction = 1
        
        # Calculate y position
        if branching:
            branch_frame += 1
            if branch_frame <= branch_frames // 2:
                # Moving away from line
                t = branch_frame / (branch_frames // 2)
                y = int(base_y + branch_direction * branch_distance * t)
            else:
                # Moving back to line
                t = (branch_frame - branch_frames // 2) / (branch_frames // 2)
                y = int(base_y + branch_direction * branch_distance * (1 - t))
            
            if branch_frame >= branch_frames:
                branching = False
                branch_frame = 0
        else:
            y = base_y
            frame_counter += 1
            if frame_counter >= branch_interval:
                frame_counter = 0
                branching = True
                branch_direction = choice([-1, 1])
        
        y = max(TARGET_RADIUS, min(HEIGHT - TARGET_RADIUS, y))
        
        cv2.circle(frame, (int(x), int(y)), TARGET_RADIUS, WHITE, -1)
        frames.append(frame)
    
    return save_gif(frames, "08_popcorn.gif")


def generate_catch_me():
    """
    9. Catch Me If You Can:
    The target appears and simulates waiting for gaze intersection before running away.
    """
    frames = []
    
    margin = TARGET_RADIUS + 10
    positions = [
        (margin, margin), (WIDTH//2, margin), (WIDTH-margin, margin),
        (margin, HEIGHT//2), (WIDTH//2, HEIGHT//2), (WIDTH-margin, HEIGHT//2),
        (margin, HEIGHT-margin), (WIDTH//2, HEIGHT-margin), (WIDTH-margin, HEIGHT-margin)
    ]
    
    # Simulate gaze approaching (visual indicator)
    wait_frames = 30  # Wait at position
    flee_frames = 20  # Flee animation
    frames_per_target = wait_frames + flee_frames
    
    current_pos = list(positions[0])
    target_idx = 0
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        cycle_frame = i % frames_per_target
        current_target = positions[target_idx % len(positions)]
        next_target = positions[(target_idx + 1) % len(positions)]
        
        if cycle_frame < wait_frames:
            # Waiting phase - target pulses slightly
            pulse = 1 + 0.1 * math.sin(cycle_frame * 0.5)
            radius = int(TARGET_RADIUS * pulse)
            pos = current_target
            
            # Draw outer ring indicating "active zone"
            cv2.circle(frame, pos, int(TARGET_RADIUS * 2), GREEN, 1)
        else:
            # Fleeing phase
            t = (cycle_frame - wait_frames) / flee_frames
            # Quick acceleration (ease-out)
            t = 1 - (1 - t) ** 3
            x = int(current_target[0] + t * (next_target[0] - current_target[0]))
            y = int(current_target[1] + t * (next_target[1] - current_target[1]))
            pos = (x, y)
            radius = TARGET_RADIUS
        
        cv2.circle(frame, pos, radius, WHITE, -1)
        frames.append(frame)
        
        if (i + 1) % frames_per_target == 0:
            target_idx += 1
    
    return save_gif(frames, "09_catch_me.gif")


def generate_bouncing():
    """
    10. Bouncing Off the Screen:
    Target constantly moves in straight or parabolic trajectory bouncing off edges.
    """
    frames = []
    
    # Initial position and velocity
    x, y = WIDTH // 2, HEIGHT // 2
    vx, vy = 5, 3
    gravity = 0.15  # For parabolic effect
    bounce_damping = 0.95
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        # Apply gravity
        vy += gravity
        
        # Update position
        x += vx
        y += vy
        
        # Bounce off walls
        if x <= TARGET_RADIUS:
            x = TARGET_RADIUS
            vx = -vx * bounce_damping
        elif x >= WIDTH - TARGET_RADIUS:
            x = WIDTH - TARGET_RADIUS
            vx = -vx * bounce_damping
        
        # Bounce off floor/ceiling
        if y <= TARGET_RADIUS:
            y = TARGET_RADIUS
            vy = -vy * bounce_damping
        elif y >= HEIGHT - TARGET_RADIUS:
            y = HEIGHT - TARGET_RADIUS
            vy = -vy * bounce_damping
            # Add some energy back on floor bounce for continuous motion
            if abs(vy) < 3:
                vy = -5
        
        # Draw motion trail
        trail_color = (100, 100, 100)
        cv2.circle(frame, (int(x), int(y)), TARGET_RADIUS, WHITE, -1)
        
        frames.append(frame)
    
    return save_gif(frames, "10_bouncing.gif")


def generate_cant_touch_this():
    """
    11. Can't Touch This:
    An invisible radius boundary prevents the gaze from ever reaching the target.
    Visual: target with outer boundary ring showing the "exclusion zone".
    """
    frames = []
    
    boundary_radius = TARGET_RADIUS * 2
    
    # Target moves around the screen
    center = [WIDTH // 2, HEIGHT // 2]
    angle = 0
    orbit_radius = 80
    angular_speed = 0.05
    
    # Simulated gaze position
    gaze_x, gaze_y = WIDTH // 2, HEIGHT // 2
    gaze_speed = 3
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        # Target orbits around center
        angle += angular_speed
        target_x = int(WIDTH // 2 + orbit_radius * math.cos(angle))
        target_y = int(HEIGHT // 2 + orbit_radius * math.sin(angle))
        
        # Simulated gaze follows target but can't enter boundary
        dx = target_x - gaze_x
        dy = target_y - gaze_y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        
        if dist > 0:
            # Move gaze towards target
            gaze_x += (dx / dist) * gaze_speed
            gaze_y += (dy / dist) * gaze_speed
            
            # But keep outside boundary
            new_dist = math.sqrt((target_x - gaze_x) ** 2 + (target_y - gaze_y) ** 2)
            if new_dist < boundary_radius:
                # Push gaze back to boundary
                gaze_x = target_x - (dx / dist) * boundary_radius
                gaze_y = target_y - (dy / dist) * boundary_radius
        
        # Draw boundary ring
        cv2.circle(frame, (target_x, target_y), boundary_radius, GREEN, 1)
        
        # Draw target
        cv2.circle(frame, (target_x, target_y), TARGET_RADIUS, WHITE, -1)
        
        # Draw simulated gaze position
        cv2.circle(frame, (int(gaze_x), int(gaze_y)), 5, (0, 255, 255), -1)
        
        frames.append(frame)
    
    return save_gif(frames, "11_cant_touch_this.gif")


def generate_dpsa_asteroids():
    """
    12. Dynamic Pursuit Sensitivity Assessment (DPSA) "Asteroids":
    Targets "fly and enlarge" towards the screen in straight vectors.
    """
    frames = []
    
    class Asteroid:
        def __init__(self):
            self.reset()
        
        def reset(self):
            # Start from edges or corners
            edge = randint(0, 3)
            if edge == 0:  # Top
                self.x = randint(0, WIDTH)
                self.y = -20
            elif edge == 1:  # Right
                self.x = WIDTH + 20
                self.y = randint(0, HEIGHT)
            elif edge == 2:  # Bottom
                self.x = randint(0, WIDTH)
                self.y = HEIGHT + 20
            else:  # Left
                self.x = -20
                self.y = randint(0, HEIGHT)
            
            # Target center
            target_x = WIDTH // 2 + randint(-50, 50)
            target_y = HEIGHT // 2 + randint(-50, 50)
            
            # Direction towards center
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            self.vx = (dx / dist) * 3
            self.vy = (dy / dist) * 3
            
            self.size = 5
            self.growth_rate = 0.5
            self.active = True
        
        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.size += self.growth_rate
            
            # Reset when too large or past center
            if self.size > 50 or self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
                self.reset()
        
        def draw(self, frame):
            if self.active:
                cv2.circle(frame, (int(self.x), int(self.y)), int(self.size), WHITE, -1)
    
    # Create multiple asteroids
    asteroids = [Asteroid() for _ in range(3)]
    # Stagger their starts
    for i, ast in enumerate(asteroids):
        for _ in range(i * 30):
            ast.update()
    
    for i in range(TOTAL_FRAMES):
        frame = create_frame()
        
        for ast in asteroids:
            ast.update()
            ast.draw(frame)
        
        frames.append(frame)
    
    return save_gif(frames, "12_dpsa_asteroids.gif")


def main():
    """Generate all 12 perimetry test animations."""
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Generating Hyperperimetry Test Animations...")
    print(f"Parameters: {WIDTH}x{HEIGHT} pixels, {FPS} fps, {DURATION} seconds ({TOTAL_FRAMES} frames)")
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    generated_files = []
    
    print("1/12 - Smooth Pursuit (sinusoidal pattern)...")
    generated_files.append(generate_smooth_pursuit())
    
    print("2/12 - Linear Pursuit (star path)...")
    generated_files.append(generate_linear_pursuit())
    
    print("3/12 - Static Perimetry Sensitivity Assessment (SPSA)...")
    generated_files.append(generate_spsa())
    
    print("4/12 - Static Fixation Evaluation (SFE)...")
    generated_files.append(generate_sfe())
    
    print("5/12 - Static Perimetry Assessment (SPA)...")
    generated_files.append(generate_spa())
    
    print("6/12 - Out of Time (center to edge)...")
    generated_files.append(generate_out_of_time())
    
    print("7/12 - Teleporter (disappear/reappear)...")
    generated_files.append(generate_teleporter())
    
    print("8/12 - Popcorn (90° branches)...")
    generated_files.append(generate_popcorn())
    
    print("9/12 - Catch Me If You Can...")
    generated_files.append(generate_catch_me())
    
    print("10/12 - Bouncing Off the Screen...")
    generated_files.append(generate_bouncing())
    
    print("11/12 - Can't Touch This (exclusion zone)...")
    generated_files.append(generate_cant_touch_this())
    
    print("12/12 - DPSA Asteroids (flying towards screen)...")
    generated_files.append(generate_dpsa_asteroids())
    
    print(f"\n✓ All 12 animations generated successfully!")
    print(f"Files saved to: {OUTPUT_DIR}")
    
    return generated_files


if __name__ == "__main__":
    main()
