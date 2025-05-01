import asyncio
import random
import socket
from websockets import serve

# Global variables
paddleSpeed = 5
players = {}

# Game settings
WIDTH, HEIGHT = 600, 600
rectSize = 75
x = WIDTH // 2
y = HEIGHT // 2
speedX = random.uniform(-3, 5)
speedY = random.uniform(-3, 5)

# Get IP address of the local machine
ip = socket.gethostbyname(socket.gethostname())

# Handle WebSocket communication
async def respond(websocket, path):
    global x, y, speedX, speedY, players
    async for message in websocket:
        messages = message.split(",")
        opcode = messages[0]
        response = ""

        if opcode == "getId":
            playerId = str(hash(random.uniform(0, 10)))
            # Set player x coordinate based on existing players
            if len(players) > 0:
                x = WIDTH - 30  # If there are other players, place new player at the right
            else:
                x = 20  # First player gets placed at the left
            players[playerId] = [messages[1], str(x)]  # Store player info
            response = playerId + "," + players[playerId][0] + "," + players[playerId][1]

        elif opcode == "getOpp":
            opId = str(messages[1])
            # Check if the opponent ID exists, otherwise return empty
            if opId in players:
                response = players[opId][0] + "," + players[opId][1]
            else:
                response = "Opponent not found"

        elif opcode == "getIds":
            # Get a comma-separated list of player IDs
            response = ",".join(players.keys())

        elif opcode == "setCoor":
            playerId = messages[1]
            # Update the player's coordinate
            players[playerId][0] = messages[2]
            response = players[playerId][0] + "," + players[playerId][1]

        elif opcode == "getBall":
            playerids = list(players.keys())
            player = players[playerids[0]]  # Get the first player
            playerbtn = float(player[0]) - rectSize / 2
            playertop = float(player[0]) + rectSize / 2
            playerx = float(player[1])

            opp = players[playerids[1]]  # Get the second player
            oppbtn = float(opp[0]) - rectSize / 2
            opptop = float(opp[0]) + rectSize / 2
            oppx = float(opp[1])

            # Ball and paddle collision detection
            if playerx < x < playerx + 10 and playerbtn < y < playertop:
                speedX *= -1 
            if oppx < x < oppx + 10 and oppbtn < y < opptop:
                speedX *= -1

            # Ball boundary collision detection
            if y < 0 or y > HEIGHT:
                speedY *= -1

            # Update ball position
            x += speedX
            y += speedY
            response = str(x) + "," + str(y)

        elif opcode == "resetBall":
            # Reset ball position
            x = WIDTH // 2
            y = HEIGHT // 2
            speedX = random.uniform(-3, 5)
            speedY = random.uniform(-3, 5)
            response = str(x) + "," + str(y)

        # Send the response back to the client
        await websocket.send(response)

# WebSocket server setup
async def main():
    print(f"Server started on ws://{ip}:8765")
    async with serve(respond, ip, 8765):
        await asyncio.Future()  # run forever

# Run the server
if __name__ == "__main__":
    asyncio.run(main())
