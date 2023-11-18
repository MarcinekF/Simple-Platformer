import math
import pygame
from os.path import join
from enum import Enum


class Enemies_list(Enum):
    big_rat = join("assets", "Enemies", "Big_Rat")

class Background(Enum):
    blue = join("assets", "Background", "Blue.png")
    brown = join("assets", "Background", "Brown.png")
    gray = join("assets", "Background", "Gray.png")
    green = join("assets", "Background", "Green.png")
    pink = join("assets", "Background", "Pink.png")
    purple = join("assets", "Background", "Purple.png")
    yellow = join("assets", "Background", "Yellow.png")


class MainCharacters(Enum):
    mask_dude = join("assets", "MainCharacters", "MaskDude")
    ninja_frog = join("assets", "MainCharacters", "NinjaFrog")
    pink_man = join("assets", "MainCharacters", "PinkMan")
    scarf_kitten = join("assets", "MainCharacters", "ScarfKitten")
    virtual_guy = join("assets", "MainCharacters", "VirtualGuy")


class Terrain(Enum):
    # (x, y, width, height)
    gray_brick = (0, 0, 48, 48)
    wood_brick = (0, 64, 48, 48)
    emerald_brick = (0, 128, 48, 48)
    default_grass = (96, 0, 48, 48)
    red_grass = (96, 64, 48, 48)
    purple_sand = (96, 128, 48, 48)
    bronze_block = (192, 0, 48, 48)
    iron_block = (192, 64, 48, 48)
    brass_block = (192, 128, 48, 48)
    brick = (272, 64, 48, 48)
    gold = (272, 128, 48, 48)


class Traps():
    pass


pygame.init()

WIDTH, HEIGHT = 600, 800

FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sample_Game")


class Player:
    speed = 3
    gravity = 1
    animation_delay = 5

    def __init__(self, x, y, width, height, skin):
        # movement
        self.rect = pygame.Rect(x, y, width, height)
        self.movement_y = 0
        self.movement_x = 0
        self.fall_count = 0
        self.stunned_time = 0
        self.hit_points = 100
        self.hit_points_digits = []
        self.hit_points_subsurfaces = []
        self.hit_points_image = pygame.image.load(join("assets", "Menu", "Text", "Text_Black.png"))

        # animation
        self.skin = skin
        self.sheet = pygame.image.load(join(self.skin.value, "idle.png"))
        self.image = self.sheet.subsurface(pygame.Rect(0, 0, 32, 32))
        self.sheet_width = None
        self.images_in_sheet = None
        self.animation = 0
        self.animation_index = 0
        self.direction = "down"
        self.flip_image = False
        self.mask = pygame.mask.from_surface(pygame.transform.scale2x(self.image))

        # jump
        self.jump_limit = 2
        self.last_block = (self.rect.x, self.rect.width)
        self.last_y = self.rect.y

    def move(self):
        self.rect.x += self.movement_x

    def stunned_effect(self):
        if self.stunned_time > 0:
            self.speed = 0
            self.stunned_time -= 1
            self.rect.x -= 10
            if self.stunned_time == 0:
                self.speed = 3
        elif self.stunned_time < 0:
            self.speed = 0
            self.stunned_time += 1
            self.rect.x += 10
            if self.stunned_time == 0:
                self.speed = 3

    def jump(self, jump_sound, double_jump_sound):
        if self.jump_limit > 0:
            jump_sound.play()
            self.direction = "up"
            if self.jump_limit == 1:
                self.direction = "double_up"
                double_jump_sound.play()
            self.jump_limit -= 1
            self.movement_y = 0
            self.fall_count = -25
            self.animation_index = 0
            self.gravity = 1

    def landed(self, block):
        self.rect.bottom = block.rect.top
        self.movement_y = 0
        self.jump_limit = 2
        self.gravity = 0
        self.last_block = [block.rect.x, block.rect.width]
        self.last_y = self.rect.y

        if isinstance(block, Spike):
            self.direction = "hit"
            self.update_hp(block.damage)
            self.fall_count = -15
            self.gravity = 1

    def update_sheet(self):

        if self.movement_x == 0 and self.movement_y == 0:
            self.direction = None
            self.sheet = pygame.image.load(join(self.skin.value, "idle.png"))
            value, value, self.sheet_width, value = self.sheet.get_rect()
            self.images_in_sheet = self.sheet_width / 32

        elif self.direction == "up":
            self.sheet = pygame.image.load(join(self.skin.value, "jump.png"))
            self.images_in_sheet = 1

        elif self.direction == "double_up":
            self.sheet = pygame.image.load(join(self.skin.value, "double_jump.png"))
            value, value, self.sheet_width, value = self.sheet.get_rect()
            self.images_in_sheet = self.sheet_width / 32

        if self.direction == "hit":
            self.sheet = pygame.image.load(join(self.skin.value, "hit.png"))
            value, value, self.sheet_width, value = self.sheet.get_rect()
            self.images_in_sheet = self.sheet_width / 32

        elif self.movement_y > 1:
            self.direction = "down"
            self.images_in_sheet = 1
            self.sheet = pygame.image.load(join(self.skin.value, "fall.png"))

        elif self.direction == "run":
            self.sheet = pygame.image.load(join(self.skin.value, "run.png"))
            value, value, self.sheet_width, value = self.sheet.get_rect()
            self.images_in_sheet = self.sheet_width / 32

        self.animation += 1
        if self.animation_index >= self.images_in_sheet:
            self.animation_index = 0

        if self.animation % self.animation_delay == 0:
            self.image = self.sheet.subsurface(self.animation_index * 32, 0, 32, 32)
            self.animation_index += 1
            self.animation = 0

    def draw(self):
        x = 10
        for hp_digit_image in self.hit_points_subsurfaces:
            screen.blit(pygame.transform.scale2x(hp_digit_image), (x, 20))
            x += 15

        if not self.flip_image:
            screen.blit(pygame.transform.scale2x(self.image), (self.rect.x, self.rect.y))
        else:
            flipped_image = pygame.transform.flip(pygame.transform.scale2x(self.image), True, False)
            screen.blit(flipped_image, (self.rect.x, self.rect.y))

    def gravity_impact(self):
        self.movement_y += min(1, (self.fall_count / FPS) * self.gravity)
        self.rect.y += self.movement_y
        self.fall_count += 1

    def update_hp(self, damage=0):
        self.hit_points_subsurfaces.clear()
        if self.hit_points > 0:
            self.hit_points -= damage
        hp_digits = [int(digit) for digit in str(self.hit_points)]
        for digit in hp_digits:
            subsurface = self.hit_points_image.subsurface(digit * 8, 30, 8, 10)
            self.hit_points_subsurfaces.append(subsurface)


class Enemy:
    def __init__(self, x, y, width, height, sheet, damage):
        self.rect = pygame.Rect(x, y, width, height)
        self.damage = damage
        self.sheet = sheet
        self.flip_image = True


class Big_Rat(Enemy):
    animation = 0
    animation_delay = 10

    def __init__(self, x, y, width, height, sheet, damage):
        super().__init__(x, y, width, height, sheet, damage)
        self.movement_x = 1
        self.image = pygame.image.load(join(self.sheet, "idle.png"))
        self.sheet_width = 5
        self.subsurface = self.image.subsurface(0, 0, 32, 32)
        self.mask = pygame.mask.from_surface(self.subsurface)
        self.animation_index = 0
        self.direction = "run"

    def update_sheet(self):
        if self.direction == "idle":
            self.image = pygame.image.load(join(self.sheet, "idle.png"))
            self.sheet_width = 5

        else:
            self.image = pygame.image.load(join(self.sheet, "run.png"))
            self.sheet_width = 7

        self.animation += 1
        if self.animation % self.animation_delay == 0:
            self.animation_index += 1

        if self.animation_index == self.sheet_width:
            self.animation_index = 0

        if self.animation < 150:
            self.direction = "run"
            self.move()

        elif self.animation == 150:
            self.animation_index = 0
            self.direction = "idle"

        if self.animation == 200:
            self.flip_image = not self.flip_image
            self.movement_x = self.movement_x * (-1)
            self.animation = 0
            self.animation_index = 0

        self.subsurface = self.image.subsurface(self.animation_index * 32, 0, 32, 32)

    def draw(self):
        self.subsurface = pygame.transform.scale2x(self.subsurface)
        self.mask = pygame.mask.from_surface(self.subsurface)
        if self.flip_image:
            self.subsurface = pygame.transform.flip(self.subsurface, True, False)
            screen.blit(self.subsurface, (self.rect.x, self.rect.y))
        else:
            screen.blit(self.subsurface, (self.rect.x, self.rect.y))

    def move(self):
        self.rect.x += self.movement_x


class Object:
    def __init__(self, x, y, width, height, image):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image


class Block(Object):
    def __init__(self, x, y, size, image):
        super().__init__(x, y, size, size, image)
        self.mask = pygame.mask.from_surface(image)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Spike(Object):
    def __init__(self, x, y, size, image):
        super().__init__(x, y, size, size, image)
        self.mask = pygame.mask.from_surface(image)
        self.damage = 2

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


def check_collisions(player, blocks, enemies, hit_sound):
    for enemy in enemies:
        if pygame.sprite.collide_mask(player, enemy):
            if player.rect.bottom < enemy.rect.top + 35:
                player.fall_count = -18
                player.movement_y = 0
                player.rect.bottom = enemy.rect.top
                player.direction = "double_up"
                enemies.remove(enemy)
            else:
                if player.rect.centerx < enemy.rect.centerx:
                    player.rect.right = enemy.rect.left
                    player.stunned_time = 10
                else:
                    player.rect.left = enemy.rect.right
                    player.stunned_time = -10

                hit_sound.play()
                player.update_hp(enemy.damage)
                player.direction = "hit"
                player.movement_y = 0
                player.fall_count = -20
                player.animation_index = 0
                player.gravity = 1

    for block in blocks:

        if pygame.sprite.collide_mask(player, block):

            overlap_x = player.rect.width / 2 + block.rect.width / 2 - abs(player.rect.centerx - block.rect.centerx)
            overlap_y = player.rect.height / 2 + block.rect.height / 2 - abs(player.rect.centery - block.rect.centery)

            if overlap_x > 2 and overlap_y > 0:
                if overlap_x > overlap_y:
                    if player.rect.centery < block.rect.centery:
                        player.landed(block)
                    else:
                        player.rect.top = block.rect.bottom
                        player.movement_y = 0
                else:
                    if player.rect.centerx < block.rect.centerx:
                        player.rect.right = block.rect.left + 8
                    else:
                        player.rect.left = block.rect.right - 5

        if player.last_block[0] > player.rect.x + 50 or player.last_block[0] + player.last_block[1] < player.rect.x + 15:
            player.gravity = 1


def listen_key(player):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.movement_x = -player.speed
        if player.movement_y == 0:
            player.direction = "run"
        player.flip_image = True
        player.move()

    if keys[pygame.K_RIGHT]:
        player.movement_x = player.speed
        if player.movement_y == 0:
            player.direction = "run"
        player.flip_image = False
        player.move()


def get_background(background):
    image = pygame.image.load(background.value)

    some_value, some_value, bg_width, bg_height = image.get_rect()
    bg_cords = []

    for i in range(WIDTH // bg_width + 1):
        for j in range(HEIGHT // bg_height + 1):
            bg_cords.append((i * bg_width, j * bg_height))

    return image, bg_cords


def get_floor_img(floor_type):
    floor_sheet = pygame.image.load(join("assets", "Terrain", "Terrain.png"))
    floor_img = floor_sheet.subsurface(floor_type.value)
    return pygame.transform.scale2x(floor_img)


def render_floor(player, objects, enemies, start_index, floor_img):
    if player.rect.x < -player.rect.width / 2:
        player.rect.x += player.speed

    elif player.rect.x > WIDTH - WIDTH / 4:
        player.rect.x -= player.speed

        for enemy in enemies:
            enemy.rect.x -= player.speed
            if enemy.rect.right < 0:
                enemies.pop(0)
                print(len(enemies))

        for object in objects:

            object.rect.x -= player.speed
            if object.rect.right < 0:
                objects.pop(0)
                objects[0].rect.x -= 3
                next_block, start_index = read_floor("Level1.txt", start_index, start_index + 1, objects[-1].rect.x)
                for cord in next_block:
                    if cord[0] is not None:
                        if cord[2] is None:
                            objects.append(Block(cord[0], cord[1], 96, floor_img))
                        elif cord[2] == "s":
                            spike_image = pygame.image.load(join("assets", "Traps", "Spikes", "idle.png"))
                            objects.append(Spike(cord[0], cord[1], 16, spike_image))
                        elif cord[2] == "br":
                            enemies.append(Big_Rat(cord[0], cord[1] - 28, 64, 64, Enemies_list.big_rat.value, 10))

    return start_index


def draw(bg_image, bg_cords, objects, player, enemies):
    for bg_coord in bg_cords:
        screen.blit(bg_image, bg_coord)
    i = 0

    for object in objects:
        object.draw()

    for enemy in enemies:
        enemy.update_sheet()
        enemy.draw()

    player.draw()
    pygame.display.update()


def read_floor(filename, start_index, end_index, last_block_x):
    matrix = []
    x = last_block_x + 96
    with open(filename, 'r') as file:

        for _ in range(start_index):
            next(file)

        for line in file:
            if start_index == end_index:
                break
            for i in range(int(len(line.split()))):

                row = line.strip().split()
                if row[i].isnumeric():
                    matrix.append((x, HEIGHT - int(row[i]) * 96, None))
                else:
                    y = ""
                    letter = ""
                    for char in row[i]:
                        if char.isdigit():
                            y += char
                        else:
                            letter += char
                    match letter:
                        case "-":
                            matrix.append((None, None, None))
                        case "s":
                            matrix.append((x, int(y) * 96 + 17, letter))
                        case "br":
                            matrix.append((x, int(y) * 96, letter))
            x += 96
            start_index += 1

    return matrix, start_index


def main():
    jump_sound_path = join("sound", "jump.wav")
    double_jump_sound_path = join("sound", "double_jump.ogg")
    jump_sound = pygame.mixer.Sound(jump_sound_path)
    double_jump_sound = pygame.mixer.Sound(double_jump_sound_path)
    hit_sound_path = join("sound", "hit.ogg")
    hit_sound = pygame.mixer.Sound(hit_sound_path)

    filename = "Level1.txt"
    start_index = 0
    end_index = math.ceil(WIDTH / 96) + 2

    floor_cords, start_index = read_floor(filename, start_index, end_index, -96)

    bg_image, bg_coord = get_background(Background.purple)  # change in order to change background
    floor_img = get_floor_img(Terrain.purple_sand)  # change in order to change floor
    objects = []
    enemies = []

    for cord in floor_cords:
        if cord[0] is not None:
            if cord[2] is None:
                objects.append(Block(cord[0], cord[1], 96, floor_img))
            elif cord[2] == "s":
                spike_image = pygame.image.load(join("assets", "Traps", "Spikes", "idle.png"))
                objects.append(Spike(cord[0], cord[1], 16, spike_image))
            elif cord[2] == "br":
                enemies.append(Big_Rat(cord[0], HEIGHT - cord[1] + 36, 64, 64, Enemies_list.big_rat.value, 10))

    player = Player(WIDTH / 2, HEIGHT / 4, 64, 64, MainCharacters.scarf_kitten)
    player.update_hp()

    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)

        start_index = render_floor(player, objects, enemies, start_index, floor_img)
        check_collisions(player, objects, enemies, hit_sound)
        player.gravity_impact()
        player.update_sheet()
        player.stunned_effect()
        listen_key(player)

        draw(bg_image, bg_coord, objects, player, enemies)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump(jump_sound, double_jump_sound)
            if event.type == pygame.KEYUP:
                player.movement_x = 0


if __name__ == "__main__":
    main()