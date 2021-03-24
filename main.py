'''
mimic of legend of the prarie king

currently working on:
enemy spawn and death
need to make list of enemies

alot more other stuff
'''

import pygame
import math

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


class Enemy:
    def __init__(self, hp, velocity, damage, x, y, radius):
        self.hp = hp
        self.velocity = velocity
        self.x = x
        self.y = y
        self.damage = damage
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


    attack = 1
    piercing = False
    bullets = []
    bullet_radius = 1
    bullet_speed = 10

    #chomper = Enemy(1, 2, 1, 0, 0)
    grub = Enemy(3, 1, 1, 0, 0, 10)
    #rigidy_digidy = Enemy(10, 0.5, 3, 0, 0)
    enemies = []


    done = False
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()


    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
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


        # bullet movements
        for bullet in bullets:
            if bullet.left:
                bullet.x -= bullet.slope[0]
            elif not bullet.left:
                bullet.x += bullet.slope[0]
            if bullet.up:
                bullet.y += bullet.slope[1]
            elif not bullet.up:
                bullet.y -= bullet.slope[1]
            dist = dist_2_points(bullet.x, bullet.y, grub.x, grub.y)
            if detect_collision(dist, grub.radius, grub.radius):
                grub.on_hit(attack)
                bullets.remove(bullet)   
                if grub.alive == False:
                    print("dead")

        


        

        # enemy stuff

        grub.towards_player(user_x, user_y)

               
        
        



        screen.fill(WHITE)


        # PLACEHOLDER GRAPHICS

        for bullet in bullets:
            pygame.draw.circle(screen, RED, (bullet.x, bullet.y), bullet.radius)


        pygame.draw.circle(screen, RED, (grub.x, grub.y), grub.radius)
        
        cursor_x, cursor_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, BLACK, (cursor_x, cursor_y), 2, 1)

        
        pygame.draw.circle(screen, BLACK, (user_x, user_y), 10)
        

        pygame.display.flip()
 

        frames_passed += 1

        clock.tick(60)


    pygame.quit()
 
if __name__ == "__main__":
    main()
