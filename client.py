import socket
import json
import time
import random


class PongClient:
    def __init__(self, server_ip="20.229.177.105", server_port=5555):
        self.server_address = (server_ip, server_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP
        self.player_number = None
        self.last_game_state = {
            "ball_x": 400,  # Default center position
            "ball_y": 300,
            "paddle1_y": 250,
            "paddle2_y": 250,
            "score": [0, 0]
        }

    def connect(self):
        """Connects to the server and receives the assigned player number."""
        # Send an initial message to let the server assign a player number
        initial_message = {"paddle_y": 150}  # Default paddle position
        self.client_socket.sendto(json.dumps(initial_message).encode(), self.server_address)

        # Receive the response with the assigned player number
        data, _ = self.client_socket.recvfrom(1024)
        game_state = json.loads(data.decode())
        self.player_number = game_state["player_number"]
        return f"Connected as Player {self.player_number}"

    def update_paddle_y(self, paddle_y):
        """Sends the paddle's updated position to the server."""
        if self.player_number is None:
            print("Error: Not connected to the server!")
            return

        message = {"paddle_y": paddle_y}
        self.client_socket.sendto(json.dumps(message).encode(), self.server_address)

    def get_state(self):
        """Retrieves the latest game state from the server, including countdown messages."""
        try:
            self.client_socket.setblocking(False)
            try:
                data, _ = self.client_socket.recvfrom(1024)
                message = json.loads(data.decode())

                if "countdown" in message:
                    return {"countdown" : message["countdown"]}  # Show countdown on screen
                elif "ball_x" in message:
                    self.last_game_state = message
            except BlockingIOError:
                pass
            except Exception as e:
                print(f"Error receiving game state: {e}")

            self.client_socket.setblocking(True)
            return self.last_game_state
        except Exception as e:
            print(f"Error in get_state: {e}")
            return self.last_game_state
