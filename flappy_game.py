import pygame
import cv2
import mediapipe as mp
import numpy as np
import sys
import random

#hand tracking setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

#game setup
pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Hand-Flappy Bird Easy Mode")

#bird properties
bird_x = 70
bird_y = HEIGHT // 2
bird_vel = 0
gravity = 0.5
flap_strength = -10  #higher jump

#pipes
pipe_gap = 200  #easier gap
pipe_width = 70
pipes = []
pipe_speed = 2  #slower pipes
spawn_timer = 0
spawn_delay = 100  #more space

#score
score = 0
font = pygame.font.SysFont("Arial", 32)

#track previous finger state
prev_finger_up = False

#spawn pipes
def spawn_pipe():
    height = random.randint(100, 400)
    top_rect = pygame.Rect(WIDTH, 0, pipe_width, height)
    bottom_rect = pygame.Rect(WIDTH, height + pipe_gap, pipe_width, HEIGHT)
    return top_rect, bottom_rect

#main loop
while True:
    screen.fill((135, 206, 250))  #the sky blue bg

    #quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    #webcam + gesture detect
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_up = False

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            tip = handLms.landmark[8]   #the index tip
            base = handLms.landmark[6]  #the index base

            #finger up check
            if tip.y < base.y - 0.02:
                finger_up = True

    #flap only on edge (down -> up)
    if finger_up and not prev_finger_up:
        bird_vel = flap_strength

    prev_finger_up = finger_up

    #bird physics
    bird_vel += gravity
    bird_y += bird_vel

    #draw bird
    pygame.draw.circle(screen, (255, 255, 0), (bird_x, int(bird_y)), 15)

    #pipe logic
    spawn_timer += 1
    if spawn_timer > spawn_delay:
        pipes.append(spawn_pipe())
        spawn_timer = 0

    new_pipes = []
    for top, bottom in pipes:
        top.x -= pipe_speed
        bottom.x -= pipe_speed

        pygame.draw.rect(screen, (0, 200, 0), top)
        pygame.draw.rect(screen, (0, 200, 0), bottom)

        bird_rect = pygame.Rect(bird_x - 15, bird_y - 15, 30, 30)

        #collision
        if bird_rect.colliderect(top) or bird_rect.colliderect(bottom):
            print("GAME OVER! Score:", score)
            pygame.time.delay(1000)
            bird_y = HEIGHT // 2
            bird_vel = 0
            pipes = []
            score = 0
            continue

        #keep pipes + scoring
        if top.x > -pipe_width:
            new_pipes.append((top, bottom))
        else:
            score += 1

    pipes = new_pipes

    #ground / ceiling check
    if bird_y <= 0 or bird_y >= HEIGHT:
        print("GAME OVER! Score:", score)
        pygame.time.delay(1000)
        bird_y = HEIGHT // 2
        bird_vel = 0
        pipes = []
        score = 0

    #score display
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(60)
