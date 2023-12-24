#import libraries - import thu vien
import pygame
import math
import random
import os
from enemies import Enemy
import button

#initialise pygame - khoi tao pygame
pygame.init()

#game window - man hinh game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

#create game window - tao cua so game
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Luận Văn Protectors')
icon = pygame.image.load('assets/bullet.png')
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60

#define game variables
level = 1
high_score = 0
level_difficulty = 0
target_difficulty = 1000
DIFFICULTY_MULTIPLIER = 1.1
game_over = False
next_level = False
MAX_ENEMIES = 10
ENEMY_TIMER = 1000
last_enemy = pygame.time.get_ticks()
enemy_alive = 0

#load highest score
if os.path.exists('score.txt'):
    with open('score.txt','r') as file:
        high_score = int(file.read())


#define colours
WHITE = (255,255,255)
BLUE = (127,255,212)
DARK_BLUE = (0,128,128)


#define font
font = pygame.font.SysFont('consolas',20)
font_60 = pygame.font.SysFont('consolas',60)


#load image - tao background cho game
bg = pygame.image.load('assets/background.jpg').convert_alpha()
lose = pygame.image.load('assets/lose.jpg').convert_alpha()

#luan van
lv_img_100 = pygame.image.load('assets/luanvan.png').convert_alpha()
lv_img_50 = pygame.image.load('assets/luanvan1.png').convert_alpha()
lv_img_25 = pygame.image.load('assets/luanvan2.png').convert_alpha()


#bullet image
bullet_img = pygame.image.load('assets/bullet.png').convert_alpha()
b_w = bullet_img.get_width()
b_h = bullet_img.get_height()
bullet_img = pygame.transform.scale(bullet_img,(int(b_w*0.05),int(b_h*0.05)))

#enemies image
enemy_animations = []
enemy_types = ['MrThinh','MrThinh','MrThinh','MrThinh']
enemy_health = [75,100,125,150]

animation_types = ['walk','attack','death']
for enemy in enemy_types:
    #load animation
    animation_list = []
    for animation in animation_types:
        #reset temperorary list of images
        temp_list = []
        if animation == 'walk':
            num_of_frames = 20
        else: num_of_frames = 4
        for i in range(num_of_frames):
            img = pygame.image.load(f'assets/enemies/{enemy}/{animation}/{i}.png').convert_alpha()
            e_w = img.get_width()
            e_h = img.get_height()
            img = pygame.transform.scale(img,(int(e_w*0.5),int(e_h*0.5)))
            temp_list.append(img)
        animation_list.append(temp_list)
    enemy_animations.append(animation_list)

#button images
   #repair image
repair_img = pygame.image.load('assets/repair.png').convert_alpha()
   #armour image
armour_img = pygame.image.load('assets/armour.png').convert_alpha()


#function for outputting text onto the screen
def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

#function for displaying status
def show_info():
    draw_text('IQ:' + str(lv.money),font,BLUE,10,10)
    draw_text('Score:' + str(lv.score),font,BLUE,10,30)
    draw_text('Highest Score:' + str(high_score),font,BLUE,10,50)
    draw_text('Level:' + str(level),font,DARK_BLUE,SCREEN_WIDTH // 2 - 180,10)
    draw_text('Graduation Chance:' + str(int((lv.health*100)/lv.max_health)) + '%',font, DARK_BLUE, SCREEN_WIDTH - 400, 10)
    draw_text('Lines Done:' + str(int(lv.health)) + '/' + str(int(lv.max_health)),font, DARK_BLUE, SCREEN_WIDTH - 400, 30)
    draw_text('(500 IQ)',font,DARK_BLUE,SCREEN_WIDTH - 105,65)
    draw_text('(1000 IQ)',font,DARK_BLUE,SCREEN_WIDTH - 110,115)

#luan van class
class Lv():
    def __init__(self,image100,image50,image25,x,y,scale):
        self.health = 1000
        self.max_health = self.health
        self.fired = False
        self.money = 0
        self.score = 0


        width = image100.get_width()
        height = image100.get_height()

        self.image100 = pygame.transform.scale(lv_img_100,(int(width*scale),int(height*scale)))
        self.image50 = pygame.transform.scale(lv_img_50, (int(width*scale),int(height *scale)))
        self.image25 = pygame.transform.scale(lv_img_25, (int(width*scale),int(height *scale)))
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y

    def shoot(self):
        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - 590
        y_dist = -(pos[1] - 407)
        self.angle = math.degrees(math.atan2(y_dist, x_dist))
        #get mouseclick
        if pygame.mouse.get_pressed()[0] and self.fired == False and pos[1] > 150:
            self.fired = True
            bullet = Bullet(bullet_img,590,407,self.angle)
            bullet_group.add(bullet)
        #reset mouseclick
        if pygame.mouse.get_pressed()[0] == False:
            self.fired = False

    def draw(self):
        #check which image to use based on health
        if self.health <= 250:
            self.image = self.image25
        elif self.health <= 500:
            self.image = self.image50
        else:
            self.image = self.image100

        screen.blit(self.image,self.rect)

    def repair(self):
        if self.money >= 1000 and self.health < self.max_health:
            self.health += 500
            self.money -= 1000
            if lv.health > lv.max_health:
                lv.health = lv.max_health

        screen.blit(self.image,self.rect)

    def armour(self):
        if self.money >= 500:
            self.max_health += 250
            self.money -= 500


#bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self,image,x,y,angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = math.radians(angle)
        self.speed = 10
        #calculate the horizontal and vertical speeds based on the angle
        self.dx = math.cos(self.angle)*self.speed
        self.dy = -(math.sin(self.angle)*self.speed)

    def update(self):

        #check if bullet has gone off the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

        #move bullet
        self.rect.x += self.dx
        self.rect.y += self.dy

class Crosshair():
    def __init__(self,scale):
        image = pygame.image.load('assets/crosshair.png').convert_alpha()
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(image,(int(width*scale),int(height*scale)))
        self.rect = self.image.get_rect()

        #hide mouse
        pygame.mouse.set_visible(False)

    def draw(self):
        mx,my = pygame.mouse.get_pos()
        self.rect.center = (mx,my)
        screen.blit(self.image,self.rect)

#tao luan van
lv = Lv(lv_img_100,lv_img_50,lv_img_25,SCREEN_WIDTH - 300, SCREEN_HEIGHT - 300,0.4)

#create crosshair
crosshair = Crosshair(0.025)

#create buttons
repair_button = button.Button(SCREEN_WIDTH - 75,70,repair_img,0.1)
armour_button = button.Button(SCREEN_WIDTH - 75,10,armour_img,0.1)

#create groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

#game loop - tao vong lap game
run = True
while run:

    clock.tick(FPS)

    if game_over == False:
        screen.blit(bg,(0,0))

        #ve luan van
        lv.draw()
        lv.shoot()

        #draw enemies
        enemy_group.update(screen,lv,bullet_group)

        #show details
        show_info()

        #create buttons
        if repair_button.draw(screen):
            lv.repair()
        if armour_button.draw(screen):
            lv.armour()

        #create enemies
        #check if max number of enemies has been reached
        if level_difficulty < target_difficulty:
            if pygame.time.get_ticks() - last_enemy > ENEMY_TIMER:
                #create enemies
                e = random.randint(0,len(enemy_types) - 1)
                enemy = Enemy(enemy_health[e], enemy_animations[e], -100, SCREEN_HEIGHT - 130,level*0.8)
                enemy_group.add(enemy)
                #reset enemy timer
                last_enemy = pygame.time.get_ticks()
                #increase level difficulty by enemy health
                level_difficulty += enemy_health[e]


        #check if all the enemies have been spawned
        if level_difficulty >= target_difficulty:
            #check how many are still alive
            enemies_alive = 0
            for e in enemy_group:
                if e.alive == True:
                    enemies_alive += 1
            #if there are not alive the level is completed
            if enemies_alive == 0 and next_level == False:
                next_level = True
                level_reset_time = pygame.time.get_ticks()

        #move onto the next level
        if next_level == True:
            draw_text('LEVEL COMPLETED!!',font_60,WHITE,140,325)
            #update highest score
            if lv.score > high_score:
                high_score = lv.score
                with open('score.txt','w') as file:
                    file.write(str(high_score))

            if pygame.time.get_ticks() - level_reset_time > 1500:
                next_level = False
                level += 1
                last_enemy = pygame.time.get_ticks()
                target_difficulty *= DIFFICULTY_MULTIPLIER
                level_difficulty = 0
                enemy_group.empty()
        #ve bullets
        bullet_group.update()
        bullet_group.draw(screen)

        #draw crosshair
        crosshair.draw()

        #check game over
        if lv.health <= 0:
            game_over = True

    else:
        screen.blit(lose, (0, 0))
        draw_text('PRESS "R" TO TRY AGAIN',font, WHITE,100,400)
        pygame.mouse.set_visible(True)
        key = pygame.key.get_pressed()
        if key[pygame.K_r]:
            #reset variebles:
            game_over = False
            level = 1
            target_difficulty = 1000
            level_difficulty = 0
            last_enemy = pygame.time.get_ticks()
            enemy_group.empty()
            lv.score = 0
            lv.health = 1000
            lv.money = 0
            pygame.mouse.set_visible(False)

    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #update display window - cap nhat man hinh game
    pygame.display.update()
pygame.quit()
