import pygame
import sys
import time
import random
from client import PongClient

# Initialize pygame
pygame.init()
pygame.mixer.init()
pong_sound = pygame.mixer.Sound('sound.mp3')

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Load background image
background = pygame.image.load("Designer.jpeg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Default keybinds
keybinds = {
    "P1 Up": pygame.K_z,
    "P1 Down": pygame.K_s,
}

logo = pygame.image.load("logo.png")
pygame.display.set_icon(logo)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
LIGHT_GREEN = (173, 255, 47)
DARK_GREEN = (34, 139, 34)
HOVER_GREEN = (144, 238, 144)
CLICK_GREEN = (0, 100, 0)
OUTLINE_COLOR = (0, 80, 0)
SHADOW_COLOR = (20, 100, 20)

# Fonts
font_title = pygame.font.Font(None, 74)
font = pygame.font.Font(None, 48)
font_text = pygame.font.Font(None, 36)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 10


# Button class
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, screen):
        """Draws the green button with a 3D effect"""
        mouse_pos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]  # Left mouse button

        # Button state logic (Normal, Hover, Click)
        if self.rect.collidepoint(mouse_pos):
            if pressed:
                base_color = CLICK_GREEN
                top_color = OUTLINE_COLOR
            else:
                base_color = HOVER_GREEN
                top_color = LIGHT_GREEN
        else:
            base_color = DARK_GREEN
            top_color = LIGHT_GREEN

            # Shadow effect
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=10)

        # Bottom part (darker green)
        pygame.draw.rect(screen, base_color, self.rect, border_radius=10)

        # Top highlight
        inner_rect = self.rect.inflate(-10, -10)
        pygame.draw.rect(screen, top_color, inner_rect, border_radius=8)

        # Text
        text_surface = font_text.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        """Checks if the button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return self.action
        return None

    # Start screen function


def start_screen():
    singleplayer_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Single Player", "single")
    multiplayer_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Two Players", "multi")
    accessibility_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50, "Accessibility", "accessibility")
    info_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 210, 200, 50, "Info", "info")

    while True:
        screen.blit(background, (0, 0))
        title_text = font_title.render("Pong Game", True, BLACK)
        screen.blit(logo, (WIDTH // 5.2, HEIGHT // 128 - 50))

        singleplayer_button.draw(screen)
        multiplayer_button.draw(screen)
        accessibility_button.draw(screen)
        info_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "single"
                if event.key == pygame.K_2:
                    return "multi"

                    # Check if buttons are clicked
            action = singleplayer_button.is_clicked(event) or multiplayer_button.is_clicked(
                event) or accessibility_button.is_clicked(event) or info_button.is_clicked(event)
            if action:
                return action


def accessibility_screen():
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50, "Back", "back")
    keybinds_button = Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 50, "Change Keybinds", "change_keybinds")

    while True:
        screen.fill(GRAY)  # Light background for better contrast

        # Title
        title_font = pygame.font.Font(None, 80)  # Larger font for title
        title = title_font.render("Accessibility Settings", True, BLACK)  # Black for contrast
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 6))

        # Buttons
        keybinds_button.draw(screen)
        back_button.draw(screen)

        # Draw separator line
        pygame.draw.line(screen, DARK_GRAY, (WIDTH // 4, HEIGHT // 2.5), (WIDTH * 3 // 4, HEIGHT // 2.5), 3)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            action = keybinds_button.is_clicked(event) or back_button.is_clicked(event)

            if action == "change_keybinds":
                change_keybinds_screen()

            if action == "back":
                return  # Go back to the main menu


def info_screen():
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50, "Back", "back")

    while True:
        screen.fill(GRAY)  # Light background for better contrast

        # Title
        title_font = pygame.font.Font(None, 80)  # Larger font for title
        title = title_font.render("Info", True, BLACK)  # Black for contrast
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 6))

        text_font = pygame.font.Font(None, 40)
        #text = text_font.render("Je gaat met de Z omhoog en de S naar beneden je moet ervoor zorgen dat het balletje niet voorbij jou padle komt", True, BLACK)
        #screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

        lines = [
            "Je gaat met de Z omhoog en de S naar beneden.",
            "Je moet ervoor zorgen dat het balletje",
            "niet voorbij jouw paddle komt."
        ]

        # Display the text as a paragraph
        y = HEIGHT // 2  # Starting Y position
        for line in lines:
            text = text_font.render(line, True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += text_font.get_height() + 5  # Move down for the next line

        back_button.draw(screen)

        # Draw separator line
        pygame.draw.line(screen, DARK_GRAY, (WIDTH // 4, HEIGHT // 2.5), (WIDTH * 3 // 4, HEIGHT // 2.5), 3)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            action = back_button.is_clicked(event)

            if action == "back":
                return  # Go back to the main menu


def change_keybinds_screen():
    global keybinds

    selected_key = None  # Track which button is active
    error_message = None  # Store error message

    # Store default keybinds for resetting conflicts
    default_keybinds = {
        "P1 Up": pygame.K_z,
        "P1 Down": pygame.K_s,
    }

    # Create buttons for keybinds
    key_buttons = {
        "P1 Up": Button(WIDTH // 2 - 150, HEIGHT // 3, 300, 50, f"P1 Up: {pygame.key.name(keybinds['P1 Up'])}"),
        "P1 Down": Button(WIDTH // 2 - 150, HEIGHT // 3 + 70, 300, 50,
                          f"P1 Down: {pygame.key.name(keybinds['P1 Down'])}"),
    }
    back_button = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50, "Back", "back")
    while True:
        screen.fill(GRAY)  # Background color for readability
        # Title
        title_font = pygame.font.Font(None, 80)
        title = title_font.render("Change Keybinds", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 10))

        # Draw all keybind buttons
        for action, button in key_buttons.items():
            if selected_key == action:
                button.text = f"Press any key..."
            else:
                button.text = f"{action}: {pygame.key.name(keybinds[action])}"
            button.draw(screen)

            # Draw error message if there's a key conflict
        if error_message:
            error_font = pygame.font.Font(None, 50)
            error_text = error_font.render(error_message, True, (255, 0, 0))
            screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 4))

            # Draw back button
        back_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for action, button in key_buttons.items():
                    if button.rect.collidepoint(event.pos):  # Check if a button is clicked
                        selected_key = action

                if back_button.is_clicked(event) == "back":
                    return  # Go back to accessibility screen

            # Key press handling
            if event.type == pygame.KEYDOWN and selected_key:
                new_key = event.key

                # Check if the key is already assigned to another action
                conflicting_action = None
                for action, bound_key in keybinds.items():
                    if bound_key == new_key and action != selected_key:
                        conflicting_action = action
                        break  # Stop as soon as a conflict is found

                if conflicting_action:
                    # Reset only the conflicting keys, not everything
                    keybinds[selected_key] = default_keybinds[selected_key]
                    keybinds[conflicting_action] = default_keybinds[conflicting_action]
                    error_message = f"Conflict! Resetting {selected_key} & {conflicting_action}."
                else:
                    keybinds[selected_key] = new_key  # Update keybinding
                    error_message = None  # Clear error message

                selected_key = None  # Reset selection


def display_countdown(countdown_value):
    """Displays the countdown on the client side."""
    countdown_text = font_title.render(str(countdown_value), True, WHITE)
    screen.fill(BLACK)  # Clear the screen
    screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2))
    pygame.display.flip()  # Update the screen with the countdown
    time.sleep(1)  # Wait for 1 second between countdown updates


# Difficulty screen function
def difficulty_screen():
    easy_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Easy", 2)
    medium_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Medium", 4)
    hard_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 140, 200, 50, "Hard", 6)

    while True:
        screen.blit(background, (0, 0))
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 2
                if event.key == pygame.K_2:
                    return 2
                if event.key == pygame.K_3:
                    return 4

                    # Check if buttons are clicked
            easy_clicked = easy_button.is_clicked(event)
            medium_clicked = medium_button.is_clicked(event)
            hard_clicked = hard_button.is_clicked(event)

            if easy_clicked:
                return 2
            if medium_clicked:
                return 2.5
            if hard_clicked:
                return 6

            # Countdown before game starts


def countdown():
    font = pygame.font.Font(None, 74)
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        countdown_text = font.render(str(i), True, WHITE)
        screen.blit(countdown_text, (WIDTH // 2 - 10, HEIGHT // 2 - 20))
        pygame.display.flip()
        time.sleep(1)

    # Reset round function


def reset_round():
    global ball_speed_x, ball_speed_y
    ball.x, ball.y = WIDTH // 2, HEIGHT // 2
    paddle1.y, paddle2.y = HEIGHT // 2 - PADDLE_HEIGHT // 2, HEIGHT // 2 - PADDLE_HEIGHT // 2
    pong_sound.play()

    # Call countdown before the game starts again
    for countdown_value in range(3, 0, -1):
        display_countdown(countdown_value)  # Show countdown before the game continues

    if random.choice([True, False]):
        ball.x = paddle1.right + 5
        ball_speed_x = initial_ball_speed
    else:
        ball.x = paddle2.left - BALL_SIZE - 5
        ball_speed_x = -initial_ball_speed

    ball.y = HEIGHT // 2
    ball_speed_y = random.choice([-initial_ball_speed, initial_ball_speed])



# Get game mode and difficulty
while True:
    game_mode = start_screen()

    if game_mode == "accessibility":
        accessibility_screen()
        continue  # Ensures we return to start screen instead of progressing to the game
    elif game_mode == "info":
        info_screen()
        continue  # Ensures we return to start screen instead of progressing to the game

    break  # Breaks the loop only if a valid game mode is selected

computer_speed = difficulty_screen() if game_mode == "single" else None

# Paddle and ball setup
paddle1 = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - 60, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)

# Speeds
paddle_speed = 5
initial_ball_speed = 2
ball_speed_x, ball_speed_y = initial_ball_speed, initial_ball_speed

# Scores
score1, score2 = 0, 0
font = pygame.font.Font(None, 36)

# Start game loop
if game_mode == "multi":
    client = PongClient()
    result = client.connect()
    pygame.display.set_caption(result)

    player_number = client.player_number
else:
    countdown()

running = True


while running:
    pygame.time.delay(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    # Second player or CPU logic
    # Modify the section in your game loop for multiplayer
    # In your main game loop:

    keys = pygame.key.get_pressed()

    if game_mode == "multi":
        if player_number == 1 and keys[keybinds["P1 Up"]] and paddle1.top > 0:
            paddle1.y -= paddle_speed
        if player_number == 1 and keys[keybinds["P1 Down"]] and paddle1.bottom < HEIGHT:
            paddle1.y += paddle_speed

        if player_number == 2 and keys[keybinds["P1 Up"]] and paddle2.top > 0:
            paddle2.y -= paddle_speed
        if player_number == 2 and keys[keybinds["P1 Down"]] and paddle2.bottom < HEIGHT:
            paddle2.y += paddle_speed

            # Send paddle position to server
        if player_number == 1:
            client.update_paddle_y(paddle1.y)
        else:
            client.update_paddle_y(paddle2.y)

            # Get game state from server
        try:
            game_state = client.get_state()
            if "countdown" in game_state:
                display_countdown(game_state["countdown"])
            else:
                ball.x, ball.y = game_state["ball_x"], game_state["ball_y"]
                paddle1.y, paddle2.y = game_state["paddle1_y"], game_state["paddle2_y"]
                if score1 is not game_state["score"][0]:
                    pong_sound.play()
                if score2 is not game_state["score"][1]:
                    pong_sound.play()
                score1, score2 = game_state["score"]
        except Exception as e:
            print(f"Error updating game state: {e}")
            # Continue with the current state if there's an error

        # Skip the local physics calculations for multiplayer mode
    else:
        # Keep the single player logic as is
        # Ball movement

        if keys[keybinds["P1 Up"]] and paddle1.top > 0:
            paddle1.y -= paddle_speed
        if keys[keybinds["P1 Down"]] and paddle1.bottom < HEIGHT:
            paddle1.y += paddle_speed

        if ball_speed_x > 0:
            if paddle2.centery < ball.centery:
                paddle2.y += computer_speed / 2
            elif paddle2.centery > ball.centery:
                paddle2.y -= computer_speed / 2

        ball.x += ball_speed_x
        ball.y += ball_speed_y
        # Rest of the single player logic...

        # Ball collision with walls
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y *= -1

            # Ball collision with paddles
        if ball.colliderect(paddle1) or ball.colliderect(paddle2):
            ball_speed_x *= -1

            # Scoring
        if ball.left <= 0:
            score2 += 1
            reset_round()
        elif ball.right >= WIDTH:
            score1 += 1
            reset_round()

            # Drawing objects
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - 30, 20))

    pygame.display.flip()

pygame.quit()