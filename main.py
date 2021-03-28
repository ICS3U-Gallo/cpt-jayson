import pygame
import math
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0 ,0)
YELLOW = (255, 255, 27)
DARK_RED = (102, 25, 25)
GREY = (182, 185, 165)

def mouse_in_box(rect, mouse_x, mouse_y):
    return (mouse_x > rect[0] and mouse_x < rect[0] + rect[2] and mouse_y > rect[1] and mouse_y < rect[1] + rect[3])

def opaque_background():
    screen.blit(background, [0,0])
    s = pygame.Surface((800,600)) 
    s.set_alpha(224)               
    s.fill(BLACK)          
    screen.blit(s, (0,0))   

size = [800, 600]
screen = pygame.display.set_mode(size)

pygame.init()
pygame.display.set_caption("Dungeon Survivor")

click = pygame.mixer.Sound("assets/click.wav")
click.set_volume(0.1)

font = pygame.font.SysFont('Calibri', 14, True, False)
menu_font = pygame.font.SysFont('Calibri', 52, True, False)
title_font = pygame.font.SysFont('Times New Roman', 60, True, False)
background = pygame.image.load('assets/background.png')

def game():
   
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

    def spawn_enemy(radius, multiplier):
        if radius == 50:
            enemy = Enemy(75 * multiplier, 0.5, 0, 0, radius, RED)
        elif radius == 20:
            enemy = Enemy(10 * multiplier, 1, 0, 0, radius, RED)
        elif radius == 10:
            enemy = Enemy(1 , 3, 0, 0, radius, RED)
        enemy.x, enemy.y = random_spawn(enemy.radius, size)
        return enemy

    def draw_big_enemy(x, y, color):
        pygame.draw.circle(screen, color, (x,y), big_enemy_r)
        pygame.draw.circle(screen, DARK_RED, (x,y), big_enemy_r, 5)
        pygame.draw.circle(screen, BLACK, (x - 20, y - 20), 5)
        pygame.draw.circle(screen, BLACK, (x + 20, y - 20), 5)
        pygame.draw.circle(screen, BLACK, (x , y + 20), 5)

    def draw_medium_enemy(x, y, color):
        counter = 0
        for i in range(5):
            pygame.draw.circle(screen, color, (x, y), medium_enemy_r - counter, 2)
            counter += 4

    def draw_small_enemy(x, y, color):
        pygame.draw.circle(screen, color, (x, y), small_enemy_r)

    def draw_powerinfo(image, sec):
        screen.blit(image, [image_pos[index_image][1], image_pos[index][2]])
        text = font.render(f"time left: {sec}",True,WHITE)
        screen.blit(text, [image_pos[index_image][1], image_pos[index][2] + 80])


    class Enemy:
        def __init__(self, hp, velocity, x, y, radius, color):
            self.hp = hp
            self.velocity = velocity
            self.x = x
            self.y = y
            self.alive = True
            self.radius = radius
            self.color = color

        
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
        def __init__(self, x, y, left, up, radius, slope, attack, fire_rate, speed):
            self.x = x
            self.y = y
            self.left = left
            self.up = up
            self.radius = radius
            self.slope = slope
            self.attack = attack
            self.fire_rate = fire_rate
            self.speed = speed


    while True:
        frames_passed = 0

        speed_icon = pygame.image.load('assets/icon1.png')
        attack_icon = pygame.image.load('assets/icon2.png')
        fourway_icon = pygame.image.load('assets/icon3.png')
        mirror_icon = pygame.image.load('assets/icon4.png')
        hitsound = pygame.mixer.Sound("assets/hitsound.wav")
        hitsound2 = pygame.mixer.Sound("assets/hitsound2.wav")
        hitsound.set_volume(0.1)
        hitsound2.set_volume(0.1)

        # player variables
        alive = True
        velocity = 1.2
        user_x = 400
        user_y = 300
        user_radius = 10

        # bullet variables
        bullets = []
        attack = 1
        fire_rate = 8
        bullet_radius = 2
        bullet_speed = 10
        shooting = False
        faster_shot = False
        bigger_shot = False
        four_shot = False
        bouncing = False
        power_up = False

        # power up variables
        power_ups = [faster_shot, bigger_shot, four_shot, bouncing]
        faster_shot_timer = 0
        bigger_shot_timer = 0
        four_shot_timer = 0
        bouncing_shot_timer = 0
        faster_shot_sec = 0
        bigger_shot_sec = 0
        four_shot_sec = 0
        bouncing_shot_sec = 0
        four_shooting = False
        bounce_shooting = False
        kills_needed_for_power_up = 7


        # enemy variables
        enemies_killed = 0
        enemies = []
        big_enemy_r = 50
        medium_enemy_r = 20
        small_enemy_r = 10
        multiplier = 1
        spawn_rate_mod = 1


        new_kills = False
        new_time = False

        image_pos = [[False, 10, 10], [False, 95, 10], [False, 180, 10], [False, 265, 10]]
        index_image = 0

        last_pos = [0,0]

        time_passed = 0

        ending_screen = False
        rect1 = [200, 250, 400, 100]
        rect2 = [200, 400, 400, 100]

        done = False
        pygame.mouse.set_visible(False)
        clock = pygame.time.Clock()

        # -------- Main Program Loop -----------
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if ending_screen == False:
                        shooting = True
                    if ending_screen == True:
                        mouse_x, mouse_y = event.pos
                        if mouse_in_box(rect1, mouse_x, mouse_y):
                            click.play()
                            done = True

                        elif mouse_in_box(rect2, mouse_x, mouse_y):
                            click.play()
                            return "menu"

                elif event.type == pygame.MOUSEBUTTONUP:
                    if ending_screen == False:
                        shooting = False


            if shooting:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if frames_passed % fire_rate == 0:
                    slope = const_slope(mouse_x, mouse_y, user_x, user_y, bullet_speed)
                    left = True
                    up = True
                    if user_x < mouse_x:
                        left = False
                    if user_y > mouse_y:
                        up = False

                    if four_shooting == True:
                        bullet = Projectile(user_x, user_y, left, up, bullet_radius, slope, attack, fire_rate, bullet_speed)
                        bullets.append(bullet)
                        bullet = Projectile(user_x, user_y, left, up, bullet_radius, [-slope[1], slope[0]], attack, fire_rate, bullet_speed)
                        bullets.append(bullet)
                        bullet = Projectile(user_x, user_y, left, up, bullet_radius, [slope[1], -slope[0]], attack, fire_rate, bullet_speed)
                        bullets.append(bullet)
                        bullet = Projectile(user_x, user_y, left, up, bullet_radius, [-slope[0], -slope[1]], attack, fire_rate, bullet_speed)
                        bullets.append(bullet)
                    else:
                        bullet = Projectile(user_x, user_y, left, up, bullet_radius, slope, attack, fire_rate, bullet_speed)
                        bullets.append(bullet)


            #reset enemy color
            for enemy in enemies:
                enemy.color = RED


            # movement
            if ending_screen == False:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    if user_x <= 0 + user_radius:
                        pass
                    else:
                        user_x -= velocity
                if keys[pygame.K_d]:
                    if user_x >= size[0] - user_radius:
                        pass
                    else:
                        user_x += velocity
                if keys[pygame.K_w]:
                    if user_y <= 0 + user_radius:
                        pass
                    else:
                        user_y -= velocity    
                if keys[pygame.K_s]:
                    if user_y >= size[1] - user_radius:
                        pass
                    else:
                        user_y += velocity

                    
                # bullet updates
                for bullet in bullets:
                    # bullet movement
                    if bullet.left:
                        bullet.x -= bullet.slope[0]
                    elif not bullet.left:
                        bullet.x += bullet.slope[0]
                    if bullet.up:
                        bullet.y += bullet.slope[1]
                    elif not bullet.up:
                        bullet.y -= bullet.slope[1]

                    if bounce_shooting == False:
                        if bullet.x < -10 or bullet.x > size[0]:
                            bullets.remove(bullet)
                        elif bullet.y < -10 or bullet.y > size[1]:
                            bullets.remove(bullet)
                    else:
                        if bullet.x < 0 or bullet.x > size[0]:
                            bullet.slope[0] *= -1
                        elif bullet.y < 0 or bullet.y > size[1]:
                            bullet.slope[1] *= -1

                    # bullet collisions
                    for enemy in enemies:
                        dist = dist_2_points(bullet.x, bullet.y, enemy.x, enemy.y)
                        if detect_collision(dist, bullet.radius, enemy.radius):
                            enemy.on_hit(attack)
                            enemy.color = GREY
                            i = random.randint(0,1)
                            if i == 1:
                                hitsound.play()
                            else:
                                hitsound2.play()
                            try:
                                bullets.remove(bullet)   
                            except ValueError:
                                pass
                        

                # spawning enemy 
                if frames_passed % round(300 * spawn_rate_mod) == 0:
                    enemies.append(spawn_enemy(big_enemy_r, multiplier))
                elif frames_passed % round(90 * spawn_rate_mod) == 0:
                    enemies.append(spawn_enemy(medium_enemy_r, multiplier))
                if frames_passed % round(30 * spawn_rate_mod) == 0:
                    enemies.append(spawn_enemy(small_enemy_r, multiplier))
                    

                # enemy update and collisions
                for enemy in enemies:
                    enemy.towards_player(user_x, user_y)
                    if enemy.alive == False:
                        enemies_killed += 1
                        enemies.remove(enemy)
                    dist = dist_2_points(user_x, user_y, enemy.x, enemy.y)
                    if detect_collision(dist, enemy.radius, user_radius):
                        alive = False


                # power ups
                if enemies_killed >= kills_needed_for_power_up:
                    power_up = True
                    kills_needed_for_power_up += 7

                if power_up == True:
                    index = random.randint(0, 3)
                    power_ups[index] = True
                    power_up = False

                if power_ups[0] == True:
                    faster_shot_timer += 600
                    faster_shot_sec += 10
                    power_ups[0] = False
                if faster_shot_timer > 0:
                    fire_rate = 4
                    faster_shot_timer -= 1
                else:
                    fire_rate = 8

                if power_ups[1] == True:
                    bigger_shot_timer += 600
                    bigger_shot_sec += 10
                    power_ups[1] = False
                if bigger_shot_timer > 0:
                    bullet_radius = 4
                    attack = 3
                    bigger_shot_timer -= 1
                else:
                    bullet_radius = 2
                    attack = 1

                if power_ups[2] == True:
                    four_shot_timer += 600
                    four_shot_sec += 10
                    power_ups[2] = False
                if four_shot_timer > 0:
                    four_shooting = True
                    four_shot_timer -= 1
                else:
                    four_shooting = False

                if power_ups[3] == True:
                    bouncing_shot_timer += 600
                    bouncing_shot_sec += 10
                    power_ups[3] = False
                if bouncing_shot_timer > 0:
                    bounce_shooting = True
                    bouncing_shot_timer -= 1
                else:
                    bounce_shooting = False
                

                # scaling difficulty
                if frames_passed % 60 == 0:
                    multiplier += 0.005
                
                if frames_passed % 120 == 0:
                    if time_passed > 10:
                        if spawn_rate_mod > 0.15:
                            spawn_rate_mod -= 0.05
                
                frames_passed += 1
                if frames_passed % 60 == 0:
                    time_passed += 1

            if not alive:
                ending_screen = True
                pygame.mouse.set_visible(True)

                file = open('assets/leaderboards.txt', 'r')
                lines = file.readlines()

                if int(lines[0].rstrip()) < enemies_killed:
                    lines[0] = str(enemies_killed) + "\n"
                    new_kills = True
                if int(lines[1].rstrip()) < time_passed:
                    lines[1] = str(time_passed)
                    new_time = True

                file = open('assets/leaderboards.txt', 'w')
                file.writelines(lines)
                file.close()

            

            # frame to time coverter
            if faster_shot_timer > 0:
                if faster_shot_timer % 60 == 0:
                    faster_shot_sec -= 1
            if bigger_shot_timer > 0:
                if bigger_shot_timer % 60 == 0:
                    bigger_shot_sec -= 1
            if four_shot_timer > 0:
                if four_shot_timer % 60 == 0:
                    four_shot_sec -= 1
            if bouncing_shot_timer > 0:
                if bouncing_shot_timer % 60 == 0:
                    bouncing_shot_sec -= 1



            # GRAPHICS
            screen.fill(WHITE)
            screen.blit(background, [0, 0])

            for bullet in bullets:
                pygame.draw.circle(screen, YELLOW, (bullet.x, bullet.y), bullet.radius)

            for enemy in enemies:
                if enemy.radius == 50:
                    draw_big_enemy(enemy.x, enemy.y, enemy.color)
                elif enemy.radius == 20:
                    draw_medium_enemy(enemy.x, enemy.y, enemy.color)          
                else:
                    draw_small_enemy(enemy.x, enemy.y, enemy.color)
        
            # draw custom cursor
            cursor_x, cursor_y = pygame.mouse.get_pos()
            pygame.draw.circle(screen, RED, (cursor_x, cursor_y), 6, 2)
            pygame.draw.circle(screen, WHITE, (cursor_x, cursor_y), 2, 2)

            # draw user
            pygame.draw.circle(screen, BLACK, (user_x, user_y), user_radius)
            pygame.draw.circle(screen, WHITE, (user_x, user_y), user_radius, 1)

            # draw text on power up information
            index_image = 0
            if faster_shot_timer > 0:
                draw_powerinfo(speed_icon, faster_shot_sec)
                index_image += 1
            if bigger_shot_timer > 0:
                draw_powerinfo(attack_icon,  bigger_shot_sec)
                index_image += 1
            if four_shot_timer > 0:
                draw_powerinfo(fourway_icon, four_shot_sec)
                index_image += 1
            if bouncing_shot_timer > 0:
                draw_powerinfo(mirror_icon, bouncing_shot_sec)
                index_image += 1

            if ending_screen == True:
                s = pygame.Surface((800,600)) 
                s.set_alpha(224)               
                s.fill(BLACK)          
                screen.blit(s, (0,0))    

                text = menu_font.render("You Lost", True, WHITE)
                screen.blit(text, [310, 50])
                if new_kills:
                    text = font.render(f"NEW", True, YELLOW)
                    screen.blit(text, [170, 130])
                text = menu_font.render(f"Enemies killed: {enemies_killed}", True, WHITE)
                screen.blit(text, [200, 130])

                if new_time:
                    text = font.render(f"NEW", True, YELLOW)
                    screen.blit(text, [170, 180])
                text = menu_font.render(f"Time survived: {time_passed}", True, WHITE)
                screen.blit(text, [200, 180])

                pygame.draw.rect(screen, GREY, rect1)
                pygame.draw.rect(screen, BLACK, rect1, 1)

                pygame.draw.rect(screen, GREY, rect2)
                pygame.draw.rect(screen, BLACK, rect2, 1)

                text = menu_font.render("Play again", True, BLACK)
                screen.blit(text, [rect1[0] + 95, rect1[1] + 35])

                text = menu_font.render("Back to menu", True, BLACK)
                screen.blit(text, [rect2[0] + 60, rect2[1] + 35])


            pygame.display.flip()
    

            clock.tick(60)
        
def menu():
    rect1 = [200, 250, 400, 100]
    rect2 = [200, 400, 400, 100]
    rect3 = [740, 10, 50, 50]
    rect4 = [10, 540, 100, 50]

    rects = [rect1, rect2, rect3, rect4]

    text_x = 178
    text_y = 100

    r = 255
    g = 255
    b = 255
    offset = 1

    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_in_box(rect1, mouse_x, mouse_y):
                    click.play()
                    return "game"
                elif mouse_in_box(rect2, mouse_x, mouse_y):
                    click.play()
                    return "instruction"
                elif mouse_in_box(rect3, mouse_x, mouse_y):
                    return "quit"
                elif mouse_in_box(rect4, mouse_x, mouse_y):
                    click.play()
                    return "leaderboards"


        r -= offset
        g -= offset
        b -= offset
        if r >= 128:
            offset *= -1
        if r <= 254:
            offset *= -1

  
        screen.fill(BLACK)
        opaque_background()

        text = title_font.render("Dungeon Survivor", True, (r, g, b))
        screen.blit(text, [text_x, text_y])


        for rect in rects:
            pygame.draw.rect(screen, GREY, rect)


        text = menu_font.render("Play", True, BLACK)
        screen.blit(text, [rect1[0] + 157, rect1[1] + 35])
        text = menu_font.render("Instructions", True, BLACK)
        screen.blit(text, [rect2[0] + 80, rect2[1] + 35])
        text = font.render("leaderboards", True, BLACK)
        screen.blit(text, [rect4[0] + 10, rect4[1] + 18])

        pygame.draw.line(screen, RED, (rect3[0] + 10 , rect3[1] + 40), (rect3[0] + 40, rect3[1] + 10), 10)   
        pygame.draw.line(screen, RED, (rect3[0] + 40, rect3[1] + 40), (rect3[0] + 10 , rect3[1] + 10), 10)
  
        pygame.display.flip()
        clock.tick(60)

def instruction():
    rect1 = [200, 400, 400, 100]
    instruction = pygame.image.load('assets/instructions.png')
    clock = pygame.time.Clock()
    done = False
    while not done:
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_in_box(rect1, mouse_x, mouse_y):
                    click.play()
                    return "menu"
   
        screen.fill(BLACK)
        opaque_background()


        screen.blit(instruction, [0,0])   

        pygame.draw.rect(screen, GREY, rect1)
        text = menu_font.render("Back to Menu", True, BLACK)
        screen.blit(text, [rect1[0] + 60, rect1[1] + 35])
       
        pygame.display.flip()
        clock.tick(60)

def leaderboards():
    rect1 = [200, 400, 400, 100]
    instruction = pygame.image.load('assets/instructions.png')
    file = open('assets/leaderboards.txt', 'r')
    lines = file.readlines()
    file.close()

    score1 = lines[0].rstrip()
    score2 = lines[1].rstrip()


    trophy = pygame.image.load('assets/trophy.png')
    clock = pygame.time.Clock()
    done = False
    while not done:
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_in_box(rect1, mouse_x, mouse_y):
                    click.play()
                    return "menu"
   

        screen.fill(BLACK)
        opaque_background()
       
        screen.blit(trophy, (100, 100))

        text = menu_font.render(f"Enemies killed: {score1}", True, WHITE)
        screen.blit(text, [300, 140])

        text = menu_font.render(f"Time survived: {score2}", True, WHITE)
        screen.blit(text, [300, 210])

        pygame.draw.rect(screen, GREY, rect1)
        text = menu_font.render("Back to Menu", True, BLACK)
        screen.blit(text, [rect1[0] + 60, rect1[1] + 35])
       
        pygame.display.flip()
        clock.tick(60)

def main():
    game_state = "menu"
    while True:
        if game_state == "menu":
            game_state = menu()

        elif game_state == "game":
            game_state = game()

        elif game_state == "instruction":
            game_state = instruction()

        elif game_state == "leaderboards":
            game_state = leaderboards()

        elif game_state == "quit":
            break


    pygame.quit()
 
if __name__ == "__main__":
    main()
