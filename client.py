import pygame
import random
import sys
import time
from websocket import create_connection, WebSocketConnectionClosedException

# Init
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Airhockey")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# Game state
x = WIDTH // 2
y = HEIGHT // 2
speedX = random.uniform(-3, 5)
speedY = random.uniform(-3, 5)

diam = 10
rectSize = 75
playerScore = 0
aiScore = 0

playerY = HEIGHT // 2
opponentY = HEIGHT // 2
playerX = 0
opponentX = 0
paddleSpeed = 5
id = ""
opponentId = ""

server_ip = "ws://localhost:8765"
connected = False
ws = None  # WebSocket connection object


def connect_to_server():
    global ws, connected
    try:
        ws = create_connection(server_ip)
        connected = True
    except Exception as e:
        print(f"Failed to connect: {e}")
        connected = False


def request(msg):
    global ws, connected
    if not connected:
        connect_to_server()
    
    try:
        ws.send(msg)
        response = ws.recv()
        return response.split(",")
    except WebSocketConnectionClosedException:
        print("Connection closed. Reconnecting...")
        connect_to_server()
        return ["0", "0", "0"]
    except Exception as e:
        print(f"Error during WebSocket communication: {e}")
        return ["0", "0", "0"]


def reset():
    request("resetBall")


def close():
    pygame.quit()
    sys.exit()


def draw_menu(selected_option):
    screen.fill((0, 0, 0))
    options = ["Connect", "Start Game", "Change Server IP", "Exit"]
    menuLength = len(options[0]) * 5
    menuHeight = len(options) * 20
    for idx, option in enumerate(options):
        if idx == 0 and connected:
            color = (0, 255, 0)  # Green if connected
        elif idx == selected_option:
            color = (255, 255, 0)
        else:
            color = (255, 255, 255)
        text = font.render(option, True, color)
        screen.blit(text, (WIDTH / 2 - menuLength, HEIGHT / 2 - menuHeight + idx * 40))
    pygame.display.flip()


def game_loop():
    global x, y, speedX, speedY, playerScore, aiScore, playerY, opponentY, opponentId, playerX, opponentX
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                reset()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            playerY -= paddleSpeed
        elif keys[pygame.K_DOWN]:
            playerY += paddleSpeed

        player = request(f"setCoor,{id},{playerY}")
        playerY = float(player[0])
        playerX = float(player[1])

        opponent = request(f"getOpp,{opponentId}")
        opponentY = float(opponent[0])
        opponentX = float(opponent[1])

        playerY = max(rectSize // 2, min(HEIGHT - rectSize // 2, playerY))
        opponentY = max(rectSize // 2, min(HEIGHT - rectSize // 2, opponentY))

        if x < 0:
            playerScore += 1
            reset()
        if x > WIDTH:
            aiScore += 1
            reset()

        score_text = f"{aiScore}  :  {playerScore}"
        screen.blit(font.render(score_text, True, (0, 255, 0)), (WIDTH // 2 - 30, 10))

        pygame.draw.ellipse(screen, (255, 255, 255), (x, y, diam, diam))  # Ball
        pygame.draw.rect(screen, (0, 255, 0), (playerX, playerY - rectSize // 2, 10, rectSize))
        pygame.draw.rect(screen, (255, 0, 0), (opponentX, opponentY - rectSize // 2, 10, rectSize))

        ballPoss = request("getBall")
        x = float(ballPoss[0])
        y = float(ballPoss[1])

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    selected = 0
    in_menu = True
    while in_menu:
        draw_menu(selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 4
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % 4
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        if id == "":
                            player = request("getId," + str(playerY))
                            id = player[0]
                            playerY = float(player[1])
                            playerX = float(player[2])
                            connected = True
                    elif selected == 1:
                        counter = 0
                        while opponentId == "":
                            ids = request("getIds")
                            for newid in ids:
                                if str(newid) != str(id):
                                    opponentId = newid
                                    counter = 10
                                    opponent = request("getOpp," + opponentId)
                                    opponentY = float(opponent[0])
                                    opponentX = float(opponent[1])
                                    game_loop()
                            counter += 1
                            if counter < 10:
                                time.sleep(1)
                            elif counter > 10:
                                break
                    elif selected == 2:
                        server_ip = input("Enter new Server IP (e.g., ws://localhost:8765): ")
                    elif selected == 3:
                        in_menu = False
                elif event.key == pygame.K_ESCAPE:
                    close()
    close()
