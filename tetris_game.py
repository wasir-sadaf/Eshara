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

#game setup
pygame.init()
WIDTH, HEIGHT = 300, 600
CELL_SIZE = 30
COLUMNS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Hand Tetris Easy")

#colors
colors = [
    (0,255,255), (0,0,255), (255,165,0), (255,255,0),
    (0,255,0), (128,0,128), (255,0,0)
]

#Tetrimino shapes
SHAPES = [
    [[1,1,1,1]],               #I
    [[1,1,0],[0,1,1]],         #Z
    [[0,1,1],[1,1,0]],         #S
    [[1,1,1],[0,1,0]],         #T
    [[1,1],[1,1]],             #O
    [[1,0,0],[1,1,1]],         #L
    [[0,0,1],[1,1,1]]          #J
]

#grid
grid = [[(0,0,0) for _ in range(COLUMNS)] for _ in range(ROWS)]

#current piece
class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS//2 - len(shape[0])//2
        self.y = 0

#spawn new piece
def new_piece():
    shape = random.choice(SHAPES)
    color = random.choice(colors)
    return Piece(shape, color)

current_piece = new_piece()
drop_counter = 0
drop_speed = 30

#check collision
def valid_move(shape, offset_x, offset_y):
    for y,row in enumerate(shape):
        for x,val in enumerate(row):
            if val:
                new_x = x + offset_x
                new_y = y + offset_y
                if new_x <0 or new_x>=COLUMNS or new_y>=ROWS:
                    return False
                if grid[new_y][new_x] != (0,0,0):
                    return False
    return True

#lock piece
def lock_piece(piece):
    for y,row in enumerate(piece.shape):
        for x,val in enumerate(row):
            if val:
                grid[piece.y+y][piece.x+x] = piece.color

#clear lines
def clear_lines():
    global grid
    new_grid = [row for row in grid if (0,0,0) in row]
    lines_cleared = ROWS - len(new_grid)
    for _ in range(lines_cleared):
        new_grid.insert(0, [(0,0,0) for _ in range(COLUMNS)])
    grid = new_grid

#draw grid
def draw_grid():
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(screen, grid[y][x], (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (50,50,50), (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE),1)

#draw current piece
def draw_piece(piece):
    for y,row in enumerate(piece.shape):
        for x,val in enumerate(row):
            if val:
                pygame.draw.rect(screen, piece.color, ((piece.x+x)*CELL_SIZE, (piece.y+y)*CELL_SIZE, CELL_SIZE, CELL_SIZE))

#main loop
while True:
    screen.fill((0,0,0))

    #quit
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
    finger_x_norm = 0.5
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            tip = handLms.landmark[8]   #index tip
            finger_x_norm = tip.x

    #instant horizontal movement
    target_x = int(finger_x_norm * COLUMNS)
    if target_x != current_piece.x and valid_move(current_piece.shape, target_x, current_piece.y):
        current_piece.x = target_x

    #drop piece
    drop_counter +=1
    if drop_counter > drop_speed:
        drop_counter = 0
        if valid_move(current_piece.shape, current_piece.x, current_piece.y+1):
            current_piece.y +=1
        else:
            lock_piece(current_piece)
            clear_lines()
            current_piece = new_piece()
            if not valid_move(current_piece.shape, current_piece.x, current_piece.y):
                print("GAME OVER")
                pygame.time.delay(1000)
                grid = [[(0,0,0) for _ in range(COLUMNS)] for _ in range(ROWS)]
                current_piece = new_piece()

    #draw
    draw_grid()
    draw_piece(current_piece)
    pygame.display.update()
    clock.tick(60)
