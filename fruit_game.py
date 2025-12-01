import pygame
import cv2
import mediapipe as mp
import sys
import random

#hand tracking setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

#pygame setup
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Fruit Ninja")
clock = pygame.time.Clock()

#game variables
fruits = []
fruit_radius = 20
fruit_speed = 5
spawn_timer = 0
spawn_delay = 50
score = 0
font = pygame.font.SysFont("Arial", 32)

#colors
colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,165,0)]
bomb_color = (0,0,0)
bomb_chance = 0.1  #10% bombs

#main loop
while True:
    screen.fill((135,206,235))  #sky blue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    #webcam + gesture
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame,1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_pos = None
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            tip = handLms.landmark[8]  #index fingertip
            finger_pos = (int(tip.x * WIDTH), int(tip.y * HEIGHT))

    #spawn fruits
    spawn_timer +=1
    if spawn_timer > spawn_delay:
        spawn_timer = 0
        x_pos = random.randint(fruit_radius, WIDTH-fruit_radius)
        y_pos = 0
        color = random.choice(colors)
        is_bomb = random.random() < bomb_chance
        fruits.append({'pos':[x_pos, y_pos],'color':bomb_color if is_bomb else color,'bomb':is_bomb})

    #move fruits
    for fruit in fruits[:]:
        fruit['pos'][1] += fruit_speed
        pygame.draw.circle(screen, fruit['color'], (int(fruit['pos'][0]), int(fruit['pos'][1])), fruit_radius)

        #check slice
        if finger_pos:
            fx, fy = finger_pos
            dx = fx - fruit['pos'][0]
            dy = fy - fruit['pos'][1]
            dist = (dx**2 + dy**2)**0.5
            if dist < fruit_radius:
                if fruit['bomb']:
                    print("BOOM! Game Over! Score:", score)
                    pygame.time.delay(1000)
                    fruits = []
                    score = 0
                else:
                    score +=1
                    fruits.remove(fruit)

        #remove if off screen
        if fruit['pos'][1] > HEIGHT + fruit_radius:
            fruits.remove(fruit)

    #draw finger
    if finger_pos:
        pygame.draw.circle(screen, (255,0,255), finger_pos, 10)

    #draw score
    text = font.render(f"Score: {score}", True, (0,0,0))
    screen.blit(text, (10,10))

    pygame.display.update()
    clock.tick(60)
