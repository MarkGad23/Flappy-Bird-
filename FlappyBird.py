import pygame
from pygame.locals import *
import random

pygame.init()

# Frame control
clock = pygame.time.Clock()
fps = 60

# Set up dimensions
screen_width = 864
screen_height = 936


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Wings')

# create game font
font = pygame.font.SysFont('Bauhaus 93', 60)

# make character colors
color_white = (255, 255, 255)

# Define game variables
ground_shift = 0
shift_speed = 4
in_air = False
game_over_flag = False
gap_between_pipes = 150
pipe_gen_interval = 1500  # milliseconds
last_pipe_generated = pygame.time.get_ticks() - pipe_gen_interval
current_score = 0
pipe_passed = False

# Load images
background_img = pygame.image.load('img/bg.png')
ground_image = pygame.image.load('img/ground.png')
restart_button_img = pygame.image.load('img/restart.png')


def display_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def reset_game_state():
    pipe_group.empty()
    bird_instance.rect.x = 100
    bird_instance.rect.y = int(screen_height / 2)
    current_score = 0
    return current_score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.animation_counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.is_clicked = False

    def update(self):
        if in_air:
            # Apply gravity
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.velocity)

        if not game_over_flag:
            # Jumping logic for bird
            if pygame.mouse.get_pressed()[0] == 1 and not self.is_clicked:
                self.is_clicked = True
                self.velocity = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.is_clicked = False

            # Handle bird flapping animation
            self.animation_counter += 1
            flap_interval = 5

            if self.animation_counter > flap_interval:
                self.animation_counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate the bird during fall
            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, pipe_position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        # pipe_position 1 is from the top, -1 is from the bottom
        if pipe_position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(gap_between_pipes / 2)]
        if pipe_position == -1:
            self.rect.topleft = [x, y + int(gap_between_pipes / 2)]

    def update(self):
        self.rect.x -= shift_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Check if the mouse is over the button
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


# Create sprite groups for bird and pipes
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

# Initialize the bird instance
bird_instance = Bird(100, int(screen_height / 2))
bird_group.add(bird_instance)

# Create an instance for the restart button
restart_button = Button(screen_width // 2 - 50, screen_height // 2 - 100, restart_button_img)

# Main game loop
running = True
while running:

    clock.tick(fps)

    # Draw background
    screen.blit(background_img, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # Draw the ground
    screen.blit(ground_image, (ground_shift, 768))

    # Check the score of game
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and not pipe_passed:
            pipe_passed = True
        if pipe_passed:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                current_score += 1
                pipe_passed = False

    display_text(str(current_score), font, color_white, int(screen_width / 2), 20)

    # Search for bird hitting pipe
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or bird_instance.rect.top < 0:
        game_over_flag = True

    # Searching for the bird hitting ground
    if bird_instance.rect.bottom >= 768:
        game_over_flag = True
        in_air = False

    if not game_over_flag and in_air:
        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe_generated > pipe_gen_interval:
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe_generated = time_now

        # Draw and scroll the ground
        ground_shift -= shift_speed
        if abs(ground_shift) > 35:
            ground_shift = 0

        pipe_group.update()

    # Check for game over and restart
    if game_over_flag:
        if restart_button.draw():
            game_over_flag = False
            current_score = reset_game_state()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not in_air and not game_over_flag:
            in_air = True

    pygame.display.update()

pygame.quit()
