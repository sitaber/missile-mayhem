import json
from time import perf_counter
import sys

import pygame

from .player import Player
from .enemy import Enemy
from .missiles import Group
from . import settings

def check_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
class App:
    def __init__(self):
        # -- INIT
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        
        flags = pygame.RESIZABLE | pygame.SCALED
        size = (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(size, flags=flags)
        self.clock = pygame.time.Clock()

        icon = pygame.image.load(f"{settings.DIR}/assets/icon.png")
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Missile Mayhem")
        
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        self.game_layer = pygame.Surface(size).convert_alpha()
        self.game_layer_rect = self.game_layer.get_rect()
        self.game_layer.fill((0,0,0))

        self.text_layer = pygame.Surface(size).convert_alpha()
        self.text_layer.fill((0,0,0,0))
        self.text_layer_rect = self.text_layer.get_rect()

        #self.font = pygame.font.Font(None, 50)
        self.font = pygame.font.Font(f"{settings.DIR}/assets/mononoki-Regular.ttf", 25)
        
    # -- utils
    def update_score(self):
        self.game_layer.fill(self.background, (0,0,1280,50))
        
        text = self.font.render(f"Score: {self.player.score}", True, self.enemy.color)
        text_rect = text.get_rect(topleft=(30, 5))
        self.game_layer.blit(text, text_rect)

        text = self.font.render(f"Hi-Score: {self.hiscore}", True, self.enemy.color) 
        text_rect = text.get_rect(centerx=1280//2, y=5)
        self.game_layer.blit(text, text_rect)

        text = self.font.render(f"Extra Cities: {self.player.extra_city}", True, self.enemy.color)
        text_rect = text.get_rect(x=1280-text.get_width()-50, y=5)
        self.game_layer.blit(text, text_rect)
        
        self.screen.blit(self.game_layer, self.game_layer_rect)
        return

    def blit_text_layer(self, text, y, fill=False):
        text = self.font.render(text, True, self.city_background)
        text_rect = text.get_rect(center=(self.text_layer_rect.centerx, y))
        if fill:
            self.text_layer.fill((0,0,0,125), text_rect)

        self.text_layer.blit(text, text_rect)
        return

    def blit_layers(self):
        self.screen.blit(self.game_layer, self.game_layer_rect)
        self.screen.blit(self.text_layer, self.text_layer_rect)

    def _wait(self, time=4000):
        t1 = pygame.time.get_ticks()
        while pygame.time.get_ticks()-t1 < time:
            check_quit()
            pygame.display.flip()
            self.clock.tick(60)
        return

    # -- MAIN
    def run(self):
        start_menu = self.start_menu()
        wait = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.new_game()
                    self.init_level()
                    self.run_game()
                    wait = 0
            
            wait +=1       
            if wait > 300: 
                self.new_game()
                self.init_level(demo=True)
                self.run_demo()
                wait = 0

            self.screen.fill((0,0,0))
            self.screen.blits(start_menu)
            pygame.display.flip()
            self.clock.tick(60)
        return

    def start_menu(self):
        image = pygame.image.load(f"{settings.DIR}/assets/title.png").convert_alpha()
        image_rect = image.get_rect(center=(1280//2, 200))

        text = self.font.render(f"Press Space to Play", True, "white")
        text_rect = text.get_rect(center=(1280//2,720//2))

        return [[image, image_rect], [text, text_rect]]

    def new_game(self):
        with open(f"{settings.DIR}/assets/game.dat") as f:
            self.hiscore = f.read()
            
        self.hiscore = int(self.hiscore)
        
        self.level = 0
        self.wave = 1
        self.max_enemy = False

        self.icbm_group = Group()
        self.rocket_group = Group()
        self.explosion_group = Group()
        self.kill_group = Group()

        groups = {
            'enemy' : self.icbm_group,
            'rocket': self.rocket_group,
            'explosion': self.explosion_group,
            'kill': self.kill_group
        }

        self.player = Player(groups)
        self.enemy = Enemy(self.player.towers.values(), self.player.cities, groups)
        return

    def init_level(self, demo=False):
        sound = pygame.mixer.Sound(f"{settings.DIR}/assets/blip.wav")
        sound.set_volume(0.1)
        sound.play(loops=9)

        level = int(self.level)
        self.background = settings.BACKGROUND[level]
        self.city_background = settings.CITY_GROUND[level]

        for tower in self.player.towers.values():
            tower.color = settings.PLAYER_COLOR[level]
            tower.build()

        for city in self.player.cities:
            city.color = settings.CITY_COLOR[level]
            if city.alive == False and self.player.extra_city:
                city.alive = True
                self.player.extra_city -= 1

        self.enemy.color = settings.ENEMY_COLOR[level]

        if self.max_enemy:
            self.enemy.speed = settings.MISSILE_SPEEDS[-1]
            self.multipler = settings.WAVE_MULTIPLERS[-1]
        else:
            self.enemy.speed = settings.MISSILE_SPEEDS[level]
            self.multipler = settings.WAVE_MULTIPLERS[level]

        self.icbm_group.clear()
        self.rocket_group.clear()
        self.explosion_group.clear()
        self.kill_group.clear()

        self.units = [
            self.player,
            self.rocket_group,
            self.icbm_group,
            self.kill_group,
            self.explosion_group
        ]

        pygame.event.clear()
        self.enemy.t1 = pygame.time.get_ticks()
        self.level_start = pygame.time.get_ticks()
        self.wave_over = False
        self.demo = demo
        if demo==False: #self.wave <= 10 and
            self.enemy.fire_salvo()
        return

    def run_game(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.USEREVENT and event.usertype == 'scoreup':
                    self.player.score_up(25 * self.multipler)

                elif event.type == pygame.KEYDOWN and event.key != pygame.K_1:
                    self.player.input(event)

            if self.wave_over and len(self.icbm_group) == 0:
                game_is_over = self.level_end()

                if game_is_over:
                    running = False
                else:
                    self.next_wave()
                    self.init_level()
                    
            self.update_render()

        self.game_over()
        return
    
    def run_demo(self):
        "Run a demo of game play"
        self.text_layer.fill((0,0,0,0))
        self.blit_text_layer("DEMO", 200)
        self.blit_text_layer("Press Space", 250)
        
        with open(f"{settings.DIR}/assets/demo_data.json", "r") as read_file:
            data = json.load(read_file)

        event_keys = list(data.keys())
        next_event = event_keys.pop(0)
        t1 = perf_counter()
        
        while next_event:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return
                
            if float(next_event) <= perf_counter() - t1:
                event_data = data[next_event]
                next_event = event_keys.pop(0) if event_keys else None
                
                if event_data['usertype'] == 'enemy':
                    self.enemy.replay(event_data)       
                
                elif event_data['usertype'] == 'player':
                    self.player.replay(event_data)
                               
            self.update_render() 
        
    def update_render(self):
        # --- Upadate and Render
        self.game_layer.fill(self.background, (0, 0, 1280, 620))
        self.game_layer.fill(self.city_background, (0, 620, 1280, 100))
        
        time_elapsed = (pygame.time.get_ticks() - self.level_start) / 1000
        if time_elapsed > 30 and not self.demo:
            self.wave_over = True
        
        elif not self.demo:
            self.enemy.update()

        for unit in self.units:
            unit.update()

        for unit in self.units:
            unit.draw(self.game_layer)

        self.screen.blit(self.game_layer, self.game_layer_rect)
        
        if self.demo:
            self.screen.blit(self.text_layer, self.text_layer_rect)
        else:
            self.update_score()
   
        pygame.display.flip()
        self.clock.tick(60)
 
    def level_end(self):
        # Clear screen and reset groups/timers etc
        if self.level < 9.5:
            self.level += 0.5
        else:
            self.level = 0
            self.max_enemy = True

        self.wave +=1
        game_over = self.calc_score()
        return game_over

    def calc_score(self):
        surving_cities = 0
        for city in self.player.cities:
            surving_cities += city.alive

        if surving_cities == 0 and self.player.extra_city == 0:
            return True

        self.player.score_up(surving_cities * 100 * self.multipler)

        self.text_layer.fill((0,0,0,125))
        self.blit_text_layer(f"Wave Complete", 150)

        val = 0
        sound = pygame.mixer.Sound(f"{settings.DIR}/assets/count.wav")
        sound.set_volume(0.15)
        while val <= surving_cities:
            if val > 0:
                sound.play()
            self.blit_text_layer(f"Cities Remaining: {int(val)}", 200, fill=True)
            self.blit_text_layer(f"Bonus Points: {int(val*100*self.multipler)}", 250, fill=True)
            self.blit_layers()
            val += 1
            self._wait(150)
        self._wait(1500)

        self.update_score()
        return False

    def game_over(self):
        new_hi = False
        if self.player.score > self.hiscore:
            new_hi = True
            with open(f"{settings.DIR}/assets/game.dat", 'w') as f:
                f.write(str(self.player.score))

        self.text_layer.fill((0,0,0,125))
        image = pygame.image.load(f"{settings.DIR}/assets/gameover.png").convert_alpha()
        image_rect = image.get_rect(center=(1280//2, 720//2-50))
        self.text_layer.blit(image, image_rect)
        self.blit_layers()

        end_sound = pygame.mixer.Sound(f"{settings.DIR}/assets/explosion.wav")
        end_sound.set_volume(0.25)
        end_sound.play(loops=100)
        end_sound.fadeout(5000)
        self._wait(5000)

        if new_hi:
            self.text_layer.fill((0,0,0,125))
            self.blit_text_layer(f"New Hi-Score!", 150)
            self.blit_text_layer(f"{self.player.score}", 200)
            self.blit_layers()
            self._wait(3500)

    def next_wave(self):
        countdown = 5
        self.text_layer.fill((0,0,0,125))
        self.blit_text_layer(f"Wave {self.wave}", 150)

        while countdown > 0:
            self.blit_text_layer(f"Starts in {int(countdown)}", 200, fill=True)
            self.blit_layers()
            self._wait(1000)
            countdown -= 1

        return

     
if __name__ == "__main__":
    from pathlib import Path
    import sys 

    sys.path.insert(0, f'{Path( __file__).parent}')
    app = App()
    app.run()





#
