'''
todo:

power ups
graphics
menu screens
timer and score

'''

import pygame
import math
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0 ,0)
GREEN = (0, 255, 0)

def dist_2_points(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def detect_collision(distance, circle_r1, circle_r2):
    return distance < circle_r1 + circle_r2
    
def const_slope(x1, y1, x2, y2, velocity):
    y = abs(y2 - y1)
    x = abs(x2 - x1)
    ratio = (x + y) / velocity
    return [x/ratio, y/ratio]

def random_spawn(radius, size):
    x = 0
    y = 0
    counter = random.randint(0, 1)
    if counter == 0:
        x = random.randint(-radius, size[0] + radius)
        counter = random.randint(0, 1)
        if counter == 0:
            y = -radius
        else:
            y = radius + size[1]
    else:
        y = random.randint(-radius, size[1] + radius)
        counter = random.randint(0, 1)
        if counter == 0:
            x = -radius
        else:
            x = radius + size[0]

    return [x, y]



class Enemy:
    def __init__(self, hp, velocity, x, y, radius):
        self.hp = hp
        self.velocity = velocity
        self.x = x
        self.y = y
        self.alive = True
        self.radius = radius

    
    def towards_player(self, player_x, player_y):
        if self.x < player_x:
            self.x += self.velocity
        if self.x > player_x:
            self.x -= self.velocity
        if self.y < player_y:
            self.y += self.velocity
        if self.y > player_y:
            self.y -= self.velocity
        

    def on_hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False



class Projectile:
    def __init__(self, x, y, left, up, radius, slope):
        self.x = x
        self.y = y
        self.left = left
        self.up = up
        self.radius = radius
        self.slope = slope



def main():
    pygame.init()
 
    size = [700, 500]
    screen = pygame.display.set_mode(size)
 
    pygame.display.set_caption("My Game")


    game_state = "menu"
    frames_passed = 0

    # player variables
    alive = True
    velocity = 1.2
    user_x = 350
    user_y = 250
    user_radius = 10

    attack = 1
    piercing = False
    bullets = []
    bullet_radius = 1
    bullet_speed = 10

    enemies_killed = 0

    enemies = []
    big_enemy_r = 50
    medium_enemy_r = 20
    small_enemy_r = 10

    score = 0
    time_passed = 0

    done = False
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()


    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # shooting
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                slope = const_slope(mouse_x, mouse_y, user_x, user_y, bullet_speed)
                left = True
                up = True
                if user_x < mouse_x:
                    left = False
                if user_y > mouse_y:
                    up = False
                bullet = Projectile(user_x, user_y, left, up, bullet_radius, slope)
                bullets.append(bullet)


        # movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            user_x -= velocity
        if keys[pygame.K_d]:
            user_x += velocity
        if keys[pygame.K_w]:
            user_y -= velocity    
        if keys[pygame.K_s]:
            user_y += velocity


        # bullet update

        # bullet movement
        for bullet in bullets:
            if bullet.left:
                bullet.x -= bullet.slope[0]
            elif not bullet.left:
                bullet.x += bullet.slope[0]
            if bullet.up:
                bullet.y += bullet.slope[1]
            elif not bullet.up:
                bullet.y -= bullet.slope[1]
            
        # collision detection
        for bullet in bullets:
            for enemy in enemies:
                dist = dist_2_points(bullet.x, bullet.y, enemy.x, enemy.y)
                if detect_collision(dist, bullet.radius, enemy.radius):
                    enemy.on_hit(attack)
                    try:
                        bullets.remove(bullet)   
                    except ValueError:
                        pass
                    if not enemy.alive:
                        enemies.remove(enemy)
                        enemies_killed += 1
                


        

        # spawning enemy 

        if frames_passed % 300 == 0:
            enemy_x, enemy_y = random_spawn(big_enemy_r, size)
            big_enemy = Enemy(10, 0.5, enemy_x, enemy_y, big_enemy_r)
            enemies.append(big_enemy)
        elif frames_passed % 180 == 0:
            enemy_x, enemy_y = random_spawn(medium_enemy_r, size)
            medium_enemy = Enemy(3, 1, enemy_x, enemy_y, medium_enemy_r)
            enemies.append(medium_enemy)
        elif frames_passed % 60 == 0:
            enemy_x, enemy_y = random_spawn(small_enemy_r, size) 
            small_enemy = Enemy(1, 3, enemy_x, enemy_y, small_enemy_r)
            enemies.append(small_enemy)



        # moving enemies

        if len(enemies) >= 1:
            for enemy in enemies:
                enemy.towards_player(user_x, user_y)
            
        # enemy collsion
        for enemy in enemies:
            dist = dist_2_points(user_x, user_y, enemy.x, enemy.y)
            if detect_collision(dist, enemy.radius, user_radius):
                alive = False


        if not alive:
            done = True




        screen.fill(WHITE)


        # PLACEHOLDER GRAPHICS

        for bullet in bullets:
            pygame.draw.circle(screen, RED, (bullet.x, bullet.y), bullet.radius)
        
        
        if len(enemies) >= 1:
            for enemy in enemies:
                pygame.draw.circle(screen, RED, (enemy.x, enemy.y), enemy.radius)
        

        cursor_x, cursor_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, BLACK, (cursor_x, cursor_y), 2, 1)

        
        pygame.draw.circle(screen, BLACK, (user_x, user_y), user_radius)
        
        frames_passed += 1
        if frames_passed % 60 == 0:
            time_passed += 1

        pygame.display.flip()
 



        clock.tick(60)


    pygame.quit()
 
if __name__ == "__main__":
    main()
