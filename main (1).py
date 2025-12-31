import pygame, random, math, datetime
from settings import *
from utils import load_img, draw_button
from sprites import Egg, FallingEgg
from logic import *

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 0
        self.load_assets()
        self.init_ui()
        self.game_history = []
        self.init_level(1)
        self.game_state = 0

    def load_assets(self):
        self.bg_start = load_img("batdau.png", (WIDTH, HEIGHT))
        self.bg_select = load_img("man.png", (WIDTH, HEIGHT))
        self.bg_game = load_img("background.png", (WIDTH, HEIGHT))
        self.bg_gameover = load_img("gameover.png", (WIDTH, HEIGHT))
        self.bg_help = load_img("huongdan.png", (WIDTH, HEIGHT))
        self.bubble_imgs = [load_img(f"bubble_{i+1}.gif", (BALL_RADIUS*2, BALL_RADIUS*2)) for i in range(6)]
        self.btn_start_img = load_img("start.png", height=80)
        self.btn_help_img = load_img("help.png", height=70)
        self.btn_history_img = load_img("history.png", height=70)
        self.btn_man1_img = load_img("man1.png", height=180)
        self.btn_man2_img = load_img("man2.png", height=180)
        self.btn_man3_img = load_img("man3.png", height=180)
        self.btn_home_img = load_img("home.png", height=50)
        self.btn_replay_img = load_img("choilai.png", height=50)
        self.btn_home_big = load_img("home.png", height=85)
        self.btn_replay_big = load_img("choilai.png", height=85)

    def init_ui(self):
        self.btn_start_rect = self.btn_start_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.btn_help_rect = self.btn_help_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.btn_history_rect = self.btn_history_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140))
        self.btn_replay_final_rect = self.btn_replay_big.get_rect(center=(WIDTH // 2 - 130, HEIGHT // 2 + 180))
        self.btn_home_final_rect = self.btn_home_big.get_rect(center=(WIDTH // 2 + 130, HEIGHT // 2 + 180))
        self.btn_home_ingame_rect = self.btn_home_img.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
        self.btn_replay_ingame_rect = self.btn_replay_img.get_rect(bottomright=(self.btn_home_ingame_rect.left - 20, HEIGHT - 20))
        self.btn_home_any_rect = self.btn_home_img.get_rect(topright=(WIDTH - 30, 30))
        self.btn_man1_rect = self.btn_man1_img.get_rect(center=(WIDTH // 2 - 200, HEIGHT // 2))
        self.btn_man2_rect = self.btn_man2_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.btn_man3_rect = self.btn_man3_img.get_rect(center=(WIDTH // 2 + 200, HEIGHT // 2))

    def init_level(self, level):
        self.current_level, self.score, self.grid_offset_state = level, 0, 0
        self.last_drop_time = pygame.time.get_ticks()
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.falling_bubbles, self.shooting = [], False
        for r in range(5):
            for c in range(COLS):
                gx, gy = get_pos(r, c, self.grid_offset_state)
                self.grid[r][c] = Egg(gx, gy, random.randint(0, 5), self.bubble_imgs)
        self.current_egg = Egg(WIDTH // 2, HEIGHT - 80, random.randint(0, 5), self.bubble_imgs)
        self.game_state = 1

    def add_to_history(self):
        now = datetime.datetime.now().strftime("%H:%M %d/%m")
        self.game_history.insert(0, {"time": now, "score": self.score, "level": self.current_level})

    def draw_trajectory(self, m_pos):
        dx, dy = m_pos[0] - self.current_egg.x, m_pos[1] - self.current_egg.y
        if dy >= 0: return

        dist = math.hypot(dx, dy)
        vx, vy = (dx / dist) * 20, (dy / dist) * 20
        cx, cy = self.current_egg.x, self.current_egg.y

        # THAY ĐỔI ĐỘ DÀI TẠI ĐÂY:
        if self.current_level == 1:
            steps = 70  # Màn 1: Rất dài (nhìn rõ điểm nảy tường)
        elif self.current_level == 2:
            steps = 15  # Màn 2: Rất ngắn (chỉ đủ thấy hướng bắn gần)
        else:
            steps = 0  # Màn 3: Không hiện (đã khóa trong LEVEL_CONFIG)

        for i in range(steps):
            cx += vx
            cy += vy

            # Phản xạ tường
            if cx <= X_MARGIN + BALL_RADIUS or cx >= X_MARGIN + PLAY_WIDTH - BALL_RADIUS:
                vx *= -1

            # Vẽ nét đứt
            if i % 2 == 0:
                pygame.draw.circle(self.screen, (255, 255, 255), (int(cx), int(cy)), 3)

            # Dừng nếu chạm trần
            if cy <= BALL_RADIUS:
                break
    def handle_click(self, m_pos):
        if self.game_state == 0:
            if self.btn_start_rect.collidepoint(m_pos): self.game_state = 3
            elif self.btn_help_rect.collidepoint(m_pos): self.game_state = 4
            elif self.btn_history_rect.collidepoint(m_pos): self.game_state = 5
        elif self.game_state == 3:
            if self.btn_man1_rect.collidepoint(m_pos): self.init_level(1)
            elif self.btn_man2_rect.collidepoint(m_pos): self.init_level(2)
            elif self.btn_man3_rect.collidepoint(m_pos): self.init_level(3)
        elif self.game_state == 1:
            if self.btn_home_ingame_rect.collidepoint(m_pos): self.game_state = 0
            elif self.btn_replay_ingame_rect.collidepoint(m_pos): self.init_level(self.current_level)
            elif not self.shooting:
                dx, dy = m_pos[0] - self.current_egg.x, m_pos[1] - self.current_egg.y
                if dy < 0:
                    dist = math.hypot(dx, dy)
                    self.vel_x, self.vel_y = (dx/dist)*25, (dy/dist)*25
                    self.shooting = True
        elif self.game_state in [4, 5]:
            if self.btn_home_any_rect.collidepoint(m_pos): self.game_state = 0
        elif self.game_state == 2:
            if self.btn_replay_final_rect.collidepoint(m_pos): self.init_level(self.current_level)
            elif self.btn_home_final_rect.collidepoint(m_pos): self.game_state = 0

    def update(self):
        if self.game_state == 1:
            now = pygame.time.get_ticks()
            if now - self.last_drop_time > LEVEL_CONFIG[self.current_level]["drop_time"]:
                self.grid_offset_state = shift_grid_down(self.grid, self.grid_offset_state, Egg, self.bubble_imgs, FallingEgg, self.falling_bubbles)
                self.last_drop_time = now
            if self.shooting:
                self.current_egg.x += self.vel_x; self.current_egg.y += self.vel_y
                if self.current_egg.x <= X_MARGIN + BALL_RADIUS or self.current_egg.x >= X_MARGIN + PLAY_WIDTH - BALL_RADIUS: self.vel_x *= -1
                hit = (self.current_egg.y <= BALL_RADIUS)
                if not hit:
                    for r in range(ROWS):
                        for c in range(COLS):
                            if self.grid[r][c] and math.hypot(self.current_egg.x - self.grid[r][c].x, self.current_egg.y - self.grid[r][c].y) < BALL_RADIUS * 1.5:
                                hit = True; break
                        if hit: break
                if hit:
                    self.shooting = False
                    r, c, gx, gy = snap_to_grid(self.current_egg.x, self.current_egg.y, self.grid_offset_state, self.grid)
                    self.grid[r][c] = Egg(gx, gy, self.current_egg.color_id, self.bubble_imgs)
                    group = get_same_color_group(r, c, self.grid, self.grid_offset_state)
                    if len(group) >= 3:
                        for pr, pc in group:
                            self.falling_bubbles.append(FallingEgg(self.grid[pr][pc]))
                            self.grid[pr][pc] = None; self.score += 10
                        self.score += handle_floating(self.grid, self.falling_bubbles, FallingEgg, self.grid_offset_state)
                    if r >= LOSE_LINE_ROW: self.add_to_history(); self.game_state = 2
                    self.current_egg = Egg(WIDTH // 2, HEIGHT - 80, random.randint(0, 5), self.bubble_imgs)
            for fb in self.falling_bubbles[:]:
                fb.update()
                if fb.y > HEIGHT: self.falling_bubbles.remove(fb)

    def draw(self, m_pos):
        if self.game_state == 0:
            self.screen.blit(self.bg_start, (0,0))
            draw_button(self.screen, self.btn_start_img, self.btn_start_rect, m_pos)
            draw_button(self.screen, self.btn_help_img, self.btn_help_rect, m_pos)
            draw_button(self.screen, self.btn_history_img, self.btn_history_rect, m_pos)
        elif self.game_state == 1:
            self.screen.blit(self.bg_game, (0,0))
            if LEVEL_CONFIG[self.current_level]["show_guide"] and not self.shooting: self.draw_trajectory(m_pos)
            for r in range(ROWS):
                for c in range(COLS):
                    if self.grid[r][c]: self.grid[r][c].draw(self.screen)
            for fb in self.falling_bubbles: self.screen.blit(fb.image, fb.image.get_rect(center=(int(fb.x), int(fb.y))))
            self.current_egg.draw(self.screen)
            draw_button(self.screen, self.btn_home_img, self.btn_home_ingame_rect, m_pos)
            draw_button(self.screen, self.btn_replay_img, self.btn_replay_ingame_rect, m_pos)
            self.screen.blit(SCORE_FONT.render(f"Score: {self.score}", True, (255,255,255)), (30,30))
        elif self.game_state == 2:
            self.screen.blit(self.bg_gameover, (0,0))
            draw_button(self.screen, self.btn_replay_big, self.btn_replay_final_rect, m_pos)
            draw_button(self.screen, self.btn_home_big, self.btn_home_final_rect, m_pos)
        elif self.game_state == 3:
            self.screen.blit(self.bg_select, (0,0))
            draw_button(self.screen, self.btn_man1_img, self.btn_man1_rect, m_pos)
            draw_button(self.screen, self.btn_man2_img, self.btn_man2_rect, m_pos)
            draw_button(self.screen, self.btn_man3_img, self.btn_man3_rect, m_pos)
        elif self.game_state == 4:
            self.screen.blit(self.bg_help, (0,0))
            draw_button(self.screen, self.btn_home_img, self.btn_home_any_rect, m_pos)
        elif self.game_state == 5:
            self.screen.fill((30,30,50))
            for i, e in enumerate(self.game_history):
                txt = HISTORY_FONT.render(f"{e['time']} | Lvl {e['level']} | Score: {e['score']}", True, (255,255,255))
                self.screen.blit(txt, (WIDTH//2 - 200, 150 + i*40))
            draw_button(self.screen, self.btn_home_img, self.btn_home_any_rect, m_pos)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            m_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN: self.handle_click(m_pos)
            self.update(); self.draw(m_pos); pygame.display.flip()

if __name__ == "__main__":
    Game().run()
    pygame.quit()