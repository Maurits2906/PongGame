import socket
import json
import threading
import time
import random

# Game Constants
WIDTH, HEIGHT = 800, 600
BALL_SIZE = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SPEED = 4
PADDLE_X_OFFSET = 50

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception as e:
        ip_address = f"Fout bij ophalen IP-adres: {e}"

    return ip_address

class PongServer:
    def __init__(self, host=get_ip_address(), port=5555):
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.server_socket.bind(self.server_address)
            print(f"Server started on {host}:{port}")
        except Exception as e:
            print(f"Error: Failed to bind server to {host}:{port} - {e}")
            return

        # Initialize these attributes before starting any threads
        self.clients = {}  # {addr: player_number}
        self.paddles = {1: HEIGHT // 2 - PADDLE_HEIGHT // 2, 2: HEIGHT // 2 - PADDLE_HEIGHT // 2}
        self.scores = {1: 0, 2: 0}

        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_speed_x = random.choice([-BALL_SPEED, BALL_SPEED])
        self.ball_speed_y = random.choice([-BALL_SPEED, BALL_SPEED])

        self.waiting_for_players = True  # Flag to wait until both players are connected
        self.game_thread = None  # Store the thread reference

    first_time = True

    def handle_ball_movement(self):
        """Continuously moves the ball and handles collisions."""
        while True:
            if self.waiting_for_players:
                # Wait until both players are connected
                time.sleep(0.1)
                continue

            if self.first_time:
                self.first_time = False
                # Send countdown signal to clients
                for countdown_value in range(3, 0, -1):
                    countdown_state = {
                        "countdown": countdown_value
                    }
                    encoded_state = json.dumps(countdown_state).encode()
                    for client_addr in self.clients.keys():
                        self.server_socket.sendto(encoded_state, client_addr)
                    time.sleep(1)  # Wait 1 second per countdown step

            self.ball_x += self.ball_speed_x
            self.ball_y += self.ball_speed_y

            if self.ball_y <= 0 or self.ball_y >= HEIGHT - BALL_SIZE:
                self.ball_speed_y *= -1

            paddle1_y = self.paddles[1]
            paddle2_y = self.paddles[2]

            if self.ball_x <= PADDLE_X_OFFSET + PADDLE_WIDTH and paddle1_y < self.ball_y < paddle1_y + PADDLE_HEIGHT:
                self.ball_speed_x *= -1
                print("Ball hit Player 1's paddle")

            if self.ball_x >= WIDTH - PADDLE_X_OFFSET - PADDLE_WIDTH - BALL_SIZE and paddle2_y < self.ball_y < paddle2_y + PADDLE_HEIGHT:
                self.ball_speed_x *= -1
                print("Ball hit Player 2's paddle")

            if self.ball_x <= 0:
                self.scores[2] += 1
                print("Player 2 scored!")
                self.reset_ball(2)  # Pass scorer as 2 (Player 2 scored)
            elif self.ball_x >= WIDTH:
                self.scores[1] += 1
                print("Player 1 scored!")
                self.reset_ball(1)  # Pass scorer as 1 (Player 1 scored)

            self.send_game_state()
            time.sleep(0.016)

    def reset_ball(self, scorer):
        """Resets the ball after a score with a cooldown before resuming play."""
        print(f"Player {scorer} scored! Waiting before resuming...")

        # Send countdown signal to clients
        for countdown_value in range(3, 0, -1):
            countdown_state = {
                "countdown": countdown_value
            }
            encoded_state = json.dumps(countdown_state).encode()
            for client_addr in self.clients.keys():
                self.server_socket.sendto(encoded_state, client_addr)
            time.sleep(1)  # Wait 1 second per countdown step

        # Reset ball position
        if scorer == 1:
            self.ball_x = PADDLE_X_OFFSET + PADDLE_WIDTH
            self.ball_y = self.paddles[1] + PADDLE_HEIGHT // 2 - BALL_SIZE // 2
            self.ball_speed_x = BALL_SPEED  # Ball moves toward Player 2
        else:
            self.ball_x = WIDTH - PADDLE_X_OFFSET - PADDLE_WIDTH - BALL_SIZE
            self.ball_y = self.paddles[2] + PADDLE_HEIGHT // 2 - BALL_SIZE // 2
            self.ball_speed_x = -BALL_SPEED  # Ball moves toward Player 1

        self.ball_speed_y = random.choice([-BALL_SPEED, BALL_SPEED])  # Random vertical direction
        print(f"Ball reset, spawn position: {self.ball_x}, {self.ball_y}")

        # Send final game state update
        self.send_game_state()

    def send_game_state(self):
        """Sends the current game state to all connected clients."""
        game_state = {
            "ball_x": self.ball_x,
            "ball_y": self.ball_y,
            "paddle1_y": self.paddles[1],
            "paddle2_y": self.paddles[2],
            "score": [self.scores[1], self.scores[2]]
        }
        encoded_state = json.dumps(game_state).encode()

        for client_addr in self.clients.keys():
            self.server_socket.sendto(encoded_state, client_addr)

    def handle_client(self, data, addr):
        """Processes paddle movement updates from clients."""
        if addr not in self.clients:
            if len(self.clients) < 2:
                player_number = 1 if len(self.clients) == 0 else 2
                self.clients[addr] = player_number
                response = json.dumps({"player_number": player_number})
                self.server_socket.sendto(response.encode(), addr)
                print(f"Player {player_number} connected from {addr}")
            else:
                print(f"Rejected connection from {addr}: Game full")
                return

        # Check if both players are connected before starting the game
        if len(self.clients) == 2 and self.waiting_for_players:
            self.waiting_for_players = False  # Both players are connected, start the game


        try:
            message = json.loads(data.decode())
            if "paddle_y" in message:
                player_number = self.clients[addr]
                self.paddles[player_number] = message["paddle_y"]
        except json.JSONDecodeError:
            print(f"Error decoding message from {addr}")

    def start(self):
        """Starts the server and listens for clients."""
        print("Pong Server is running...")

        # Start the ball movement thread
        self.game_thread = threading.Thread(target=self.handle_ball_movement, daemon=True)
        self.game_thread.start()

        # Main game loop
        while True:
            try:
                # Process incoming data (paddle movement)
                data, addr = self.server_socket.recvfrom(1024)
                self.handle_client(data, addr)
            except Exception as e:
                print(f"Error receiving data: {e}")
                continue  # Continue listening for new data


if __name__ == "__main__":
    server = PongServer()
    server.start()