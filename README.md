# Eshara

This repository contains **5 classic arcade games** that can be controlled using hand gestures via **OpenCV** and **Mediapipe**. Each game uses **Pygame** for graphics and game logic.

## Games Included

1. **DX Ball** (`dx_game.py`)  
   Break the bricks with a ball while controlling the paddle using your hand.

2. **Flappy Bird** (`flappy_game.py`)  
   Make the bird jump through pipes with a single hand gesture per flap.

3. **Fruit Ninja** (`fruit_game.py`)  
   Slice falling fruits with your hand while avoiding bombs.

4. **Snake Game** (`snake_game.py`)  
   Control the snake using hand gestures to eat food and grow.

5. **Tetris** (`tetris_game.py`)  
   Move Tetris blocks left and right using hand gestures. Blocks fall automatically.

## Requirements

* Python 3.x  
* Pygame  
* OpenCV (`opencv-python`)  
* Mediapipe  

Install dependencies using:

```bash
pip install pygame opencv-python mediapipe
````

## How to Run

Run any game with:

```bash
python <game_file>.py
```

For example:

```bash
python dx_game.py
```

Make sure your webcam is connected and accessible.

## Controls

All games use **hand gestures** detected by Mediapipe:

* **DX Ball:** Move paddle left/right with your hand.
* **Flappy Bird:** One jump per finger raise.
* **Fruit Ninja:** Slice fruits with your finger.
* **Snake:** Move the snake in the desired direction.
* **Tetris:** Move blocks left/right using finger position.

## Notes

* For best experience, keep your hand visible to the webcam.
* Lighting conditions affect gesture detection accuracy.
* Adjust game difficulty or sensitivity by modifying the respective game files.
