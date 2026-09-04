import math 
import random 
from pygame import Rect 
import pygame 

pygame.mixer.init() # .wav dosyalarýný calabilmek icin
#oyun penceresinin genisligi, yüksekligi
WIDTH = 900 
HEIGHT = 600 


GRAVITY = 0.5 
SPEED = 5 # yatay hiz
JUMP_FORCE = -11 # ziplama kuvveti
game_state = "menu" # oyunun durumu
sound_enabled = True # ses durum bayragi

platforms = [ # zemin ve duvarin konumunu tutan liste
    Rect(0, 540,900, 60), 
    Rect(180,440, 180,25), 
    Rect(450,350,180,25), 
    Rect(700, 450,140,25), 
    Rect(630,280,20,260) 
] 
goal_rect = Rect(820, 370, 6, 80) # bitiþ noktasýný hedef eden sarý renkli bayrak

def check_collision(a,b):  # nesnelerin carpisma fonksiyonu
    return ( 
        a.x < b.x + b.width and 
        a.x + a.width > b.x and 
        a.y < b.y + b.height and 
        a.y + a.height > b.y 
    ) 

class Player: 
    def __init__(self): 
        self.x = 60 # baslangic koordinati
        self.y = 522 # baslangic koordinati
        self.width = 18 # boyut
        self.height=18 #boyut
        self.vy=0 
        self.is_grounded=False # zeminde mi ? 
        self.health=3 # can sayisi
        self.anim_timer=0 
        self.is_moving=False 

    def update(self): 
        self.is_moving = False 
        
        dx = 0 
        if keyboard.left: 
            dx -= SPEED 
            self.is_moving = True 
        if keyboard.right: 
            dx += SPEED 
            self.is_moving = True 
        self.x += dx 
        p_rect = Rect(self.x, self.y, self.width, self.height) 
        for plat in platforms: 
            if check_collision(p_rect, plat): 
                if dx > 0: 
                    self.x = plat.left - self.width 
                elif dx < 0: 
                    self.x = plat.right 
                p_rect.x = self.x 
        self.anim_timer+=0.15 
        self.vy+=GRAVITY # yer cekimi dikey hiza eklenir
        self.y+=self.vy  
        self.is_grounded = False 
        p_rect = Rect(self.x,self.y, self.width,self.height) 

        for plat in platforms: 
            if self.vy >= 0 and p_rect.right > plat.left and p_rect.left < plat.right and p_rect.bottom >= plat.top and p_rect.bottom <= plat.bottom + 10: 
                self.y = plat.top - self.height 
                self.vy = 0 
                self.is_grounded = True 
        self.x = max(0, min(self.x,WIDTH-self.width)) 

        if self.y > HEIGHT: 
            self.health = 0 
    def jump(self): # karakter yalnizca zemindeyse zipla
        if self.is_grounded: 
            self.vy = JUMP_FORCE 
    def draw(self): # hareket ediyorsa yürüme görseli etmiyorsa bekleme görseli
        frames = ["hero_idle1", "hero_walk1"] if self.is_moving else ["hero_idle1"] 
        img = frames[int(self.anim_timer) % len(frames)] 
        screen.blit(img, (self.x,self.y)) 
class Enemy: # düsman sinifi
    def __init__(self,x,y,left,right,e_type): # yatay sinirlarda saða sola gidip gelir
        self.x =x 
        self.base_y =y 
        self.y =y 
        self.width=18 
        self.height=18 
        self.left =left 
        self.right =right 
        self.e_type =e_type 
        self.dir = 1 
        self.v_dir = 1 
        self.anim_timer = 0 

    def update(self): 
        self.x += self.dir*2 
        self.anim_timer+=0.15 
        if self.e_type=="bat": 
            self.y+=self.v_dir * 2.5 
            if self.y>=390: 
                self.v_dir=-1 
            elif self.y<=210: 
                self.v_dir=1 

        if self.x <= self.left: 
            self.dir=1 
        if self.x + self.width >= self.right: 
            self.dir=-1 
    def draw(self): 
        frames = ["slime_idle1", "slime_walk1"] if self.e_type == "slime" else ["bat_fly1", "bat_fly2"] 
        img = frames[int(self.anim_timer) % len(frames)] 
        screen.blit(img, (self.x, self.y)) 
player = Player() 
enemies = [ 
    Enemy(200, 422, 180, 360,"slime"), 
    Enemy(470, 220, 450, 630,"bat") 
] 
def play_sfx(name): 
    if sound_enabled: 
        try: 
            s = pygame.mixer.Sound("sounds/" + name + ".wav") 
            s.play() 
        except Exception: 
            pass 
def start_bgm(): 
    if sound_enabled: 
        try: 
            pygame.mixer.music.load("sounds/bgm.wav") 
            pygame.mixer.music.play(-1) 
        except Exception: 
            pass 
def stop_bgm(): 
    try: 
        pygame.mixer.music.stop() 
    except Exception: 
        pass 
def reset_game(): 
    global player, game_state 
    player = Player() 
    game_state = "playing" 
    stop_bgm() 
    start_bgm() 
def update(): # oyuncu düsman konumlari güncellenir
    global game_state 
    if game_state != "playing": 
        return 
    player.update() 
    for enemy in enemies: 
        enemy.update() 
    p_rect = Rect(player.x, player.y, player.width, player.height) 
    for enemy in enemies: 
        e_rect = Rect(enemy.x, enemy.y, enemy.width, enemy.height) 
        if check_collision(p_rect, e_rect): 
            play_sfx("hit") 
            player.health -= 1 
            player.x = 60 
            player.y = 522 
            player.vy = 0 
    if check_collision(p_rect, goal_rect): 
        stop_bgm() 
        play_sfx("win") 
        game_state = "win" 
    if player.health <= 0: 
        stop_bgm() 
        play_sfx("hit") 
        game_state = "lose" 
def draw_btn(rect, text): 
    screen.draw.filled_rect(Rect(rect.x + 4, rect.y + 4, rect.width, rect.height), "gray") 
    screen.draw.filled_rect(rect, "blue") 
    screen.draw.text(text, center=rect.center, fontsize=26, color="white") 
def draw(): 
    screen.fill((135, 206, 235)) 
    if game_state == "menu": 
        screen.fill("orange") 
        screen.draw.text("PLATFORM ADVENTURE", center=(450, 120), fontsize=48, color="white") 
        draw_btn(Rect(300,220,300,50), "START GAME") 
        draw_btn(Rect(300, 290, 300, 50), "AUDIO: ON" if sound_enabled else "AUDIO: OFF") 
        draw_btn(Rect(300, 360, 300, 50), "EXIT") 

    elif game_state == "playing": 
        for plat in platforms: 
            screen.draw.filled_rect(plat, (34, 139, 34)) 
        screen.draw.filled_rect(goal_rect, "gold") 
        for enemy in enemies: 
            enemy.draw() 
        player.draw() 
        screen.draw.text("HEALTH: " + str(player.health), (20, 20), fontsize=28, color="black") 

    elif game_state in ("win", "lose"): 
        screen.fill("orange") 
        title = "YOU WIN!" if game_state == "win" else "GAME OVER" 
        msg = "You reached the goal!" if game_state == "win" else "You ran out of lives." 
        screen.draw.text(title, center=(450, 180), fontsize=56, color="white") 
        screen.draw.text(msg, center=(450, 250), fontsize=26, color="white") 
        draw_btn(Rect(300, 330, 300, 50), "PLAY AGAIN") 
        draw_btn(Rect(300, 400, 300, 50), "MENU") 

def on_key_down(key):# space tusuna basildiginda zipla 
    if game_state == "playing" and key == keys.SPACE: 
        player.jump() 

def on_mouse_down(pos): # buton koordinatlarina göre oyunu baslat
    global game_state, sound_enabled 

    if game_state == "menu": 
        if Rect(300,220,300,50).collidepoint(pos): 
            reset_game() 
        elif Rect(300, 290, 300, 50).collidepoint(pos): 
            sound_enabled = not sound_enabled 
            if not sound_enabled: 
                stop_bgm() 
        elif Rect(300, 360, 300, 50).collidepoint(pos): 
            quit() 

    elif game_state in ("win", "lose"): 
        if Rect(300, 330,300, 50).collidepoint(pos): 
            reset_game() 
        elif Rect(300, 400, 300,50).collidepoint(pos): 
            stop_bgm() 
            game_state = "menu"