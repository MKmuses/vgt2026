# vgt2026
Ophthalmological applications for remote gaze tracking

**Target Generator**
In hyperperimetry tests to test the saccadic and pursuit sensitivity of an individual's vision, several targets are presented on the screen and gaze tracking is used to track the sensitivity of the individual. The targetgenerator.py python code generates 12 different .gif animations with 300x300 pixels and 25fps for 10 seconds demonstrating: 

1. Smooth Pursuit: pursue a generated target moving in a sinusoidal pattern
2. Linear pursuit: a target dot travels in a star path on the screen 
3. Static Perimetry Sensitivity Assessment (SPSA): single static dots appears on the screen and grows and disappears before the next target appears. 
4. Static Fixation Evaluation (SFE): a large circle appears on the screen that shrinks into a small dot
5. Static Perimetry Assessment (SPA): single static dots appears on the screen and stays visible for 3 seconds
6. Out of time: Target appears at the centre, then appears or moves to the edge and back.
7. Teleporter: Single target moving abruptly disappears and reappears on another line in the same direction 
8. Popcorn: Single target moving abruptly branches 90° and returns to the line repeatedly. 
9. Catch me if you can: The target appears and waits for the user’s gaze to intersect before “running” away to another spot.
10. Bouncing off the screen: This is a variant of pursuit but constantly moves in a straight or parabolic trajectory bouncing off the screen
11. Can’t touch this: An invisible radius boundary prevents the gaze from ever reaching the target. 
12. Dynamic Pursuit Sensitivity Assessment (DPSA) “Asteroids flying towards you” - Targets “fly and enlarge” towards the screen in straight vector
