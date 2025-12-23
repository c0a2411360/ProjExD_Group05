import pygame as pg
import sys
import os
import random


# 指定条件
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# =====================
# 定数
# =====================
WIDTH, HEIGHT = 800, 450
FPS = 60
GROUND_Y = 360
GRAVITY = 1
JUMP_POWER = -18
MAX_JUMP = 3


# =====================
# 初期化
# =====================
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("こうかとん、講義に遅刻する")
clock = pg.time.Clock()
font = pg.font.SysFont(None, 32)


# =====================
# 主人公
# =====================
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("C:/Users/Admin/Documents/ProjExD/ex4/fig/2.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect(midbottom=(150, GROUND_Y))
        self.vel_y = 0
        self.jump_count = 0

    def update(self, grounds):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        landed = False
        for g in grounds:
            if (
                self.rect.colliderect(g)
                and self.vel_y >= 0
                and self.rect.bottom - self.vel_y <= g.top
            ):
                self.rect.bottom = g.top
                self.vel_y = 0
                self.jump_count = 0
                landed = True

        # 画面下に落ちたら穴落下
        if not landed and self.rect.top > HEIGHT:
            return "fall"
        return None

    def jump(self):
        if self.jump_count < MAX_JUMP:
            self.vel_y = JUMP_POWER
            self.jump_count += 1


# =====================
# 段差
# =====================
class Step:
    def __init__(self, x):
        h = random.choice([40, 80])
        w = random.randint(80, 140)
        self.rect = pg.Rect(x, GROUND_Y - h, w, h)

    def update(self, speed):
        self.rect.x -= speed


# =====================
# 穴
# =====================
class Hole:
    def __init__(self, x):
        w = random.randint(100, 160)
        self.rect = pg.Rect(x, GROUND_Y, w, HEIGHT)

    def update(self, speed):
        self.rect.x -= speed


# =====================
# ゴール旗
# =====================
class GoalFlag:
    def __init__(self, x):
        self.pole = pg.Rect(x, GROUND_Y - 120, 10, 120)
        self.flag = pg.Rect(x + 10, GROUND_Y - 120, 50, 30)

    def update(self, speed):
        self.pole.x -= speed
        self.flag.x -= speed

    def draw(self):
        pg.draw.rect(screen, (200, 200, 200), self.pole)
        pg.draw.rect(screen, (255, 0, 0), self.flag)
    

# =====================
# 赤い先生
# =====================
def make_teacher_image():  # 赤い先生を作成
    surf = pg.Surface((40, 60), pg.SRCALPHA)  # 透過あり
    surf.fill((0, 0, 0, 0))  # 完全透明

    # 体
    pg.draw.rect(surf, (200, 50, 50), (5, 10, 30, 45), border_radius=8)

    # 頭
    pg.draw.circle(surf, (230, 80, 80), (20, 12), 10)

    # 目
    pg.draw.circle(surf, (0, 0, 0), (16, 10), 2)
    pg.draw.circle(surf, (0, 0, 0), (24, 10), 2)

    return surf


class Teacher:
    def __init__(self, x):
        self.image = make_teacher_image()
        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))

        self.vel_y = 0
        self.speed = 8
        self.on_ground = False
        self.jump_timer = 0

    def update(self, grounds):
        # 前進
        self.rect.x += self.speed
        if self.rect.right > WIDTH - 80:
            self.rect.right = WIDTH - 80

        # 一定周期ジャンプ
        self.jump_timer += 1
        if self.jump_timer >= 90 and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
            self.jump_timer = 0

        # 重力
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # 着地
        self.on_ground = False
        for g in grounds:
            if (
                self.rect.colliderect(g)
                and self.vel_y >= 0
                and self.rect.bottom - self.vel_y <= g.top
            ):
                self.rect.bottom = g.top
                self.vel_y = 0
                self.on_ground = True
                break

    def draw(self):
        screen.blit(self.image, self.rect)


# =====================
# メイン
# =====================
def main():
    stage = 1
    speed = 6
    goal_distance = 2500

    while True:
        player = Player()
        steps = []
        holes = []
        teachers = []  # 先生リスト
        teacher_appeared = False
        goal = GoalFlag(goal_distance)
        frame = 0
        state = "play"
        next_stage = False

        while True:
            # ---------- イベント ----------
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE and state == "play":
                        player.jump()

                    if state == "clear":
                        if event.key == pg.K_y:
                            stage += 1
                            speed += 1
                            goal_distance += 1500
                            next_stage = True
                        if event.key == pg.K_n:
                            pg.quit()
                            sys.exit()

                    if state == "gameover" and event.key == pg.K_r:
                        next_stage = True

            # ---------- ゲーム処理 ----------
            if state == "play":
                frame += 1

                if frame % 80 == 0:
                    x = WIDTH + 50
                    if random.random() < 0.5:
                        steps.append(Step(x))
                    else:
                        holes.append(Hole(x))

                for s in steps:
                    s.update(speed)
                for h in holes:
                    h.update(speed)
                
                goal.update(speed)

                # ===== 地面生成（穴を除外） =====
                base_grounds = [pg.Rect(0, GROUND_Y, WIDTH, HEIGHT)]
                teacher_grounds = [pg.Rect(0, GROUND_Y, WIDTH, HEIGHT)]

                for h in holes:
                    new_grounds = []
                    for g in base_grounds:
                        if not g.colliderect(h.rect):
                            new_grounds.append(g)
                        else:
                            if g.left < h.rect.left:
                                new_grounds.append(
                                    pg.Rect(g.left, g.top, h.rect.left - g.left, g.height)
                                )
                            if h.rect.right < g.right:
                                new_grounds.append(
                                    pg.Rect(h.rect.right, g.top, g.right - h.rect.right, g.height)
                                )
                    base_grounds = new_grounds

                grounds = base_grounds + [s.rect for s in steps]

                for t in teachers:
                    t.update(teacher_grounds)

                if player.update(grounds) == "fall":
                    state = "gameover"

                # 段差の横衝突
                for s in steps:
                    if player.rect.colliderect(s.rect):
                        if not (player.rect.bottom <= s.rect.top + 5 and player.vel_y >= 0):
                            state = "gameover"

                # ゴール
                if player.rect.colliderect(goal.pole):
                    state = "clear"

                # 低確率で先生を出現
                if (
                    not teacher_appeared
                    and frame % 120 == 0
                    and random.random() < 0.5
                ):
                    teachers.append(Teacher(player.rect.left - 80))
                    teacher_appeared = True

            # ---------- 描画 ----------
            screen.fill((135, 206, 235))
            pg.draw.rect(screen, (50, 200, 50), (0, GROUND_Y, WIDTH, HEIGHT))

            for h in holes:
                pg.draw.rect(screen, (0, 0, 0), h.rect)
            for s in steps:
                pg.draw.rect(screen, (50, 200, 50), s.rect)
            for t in teachers:  # 先生の描画
                t.draw()

            goal.draw()
            screen.blit(player.image, player.rect)

            screen.blit(font.render(f"STAGE {stage}", True, (0, 0, 0)), (10, 10))

            if state == "gameover":
                screen.blit(font.render("GAME OVER (R)", True, (255, 0, 0)),
                            (WIDTH//2 - 100, HEIGHT//2))

            if state == "clear":
                if teacher_appeared:
                    msg = "Class cancellation！"
                else:
                    msg = "NEXT STAGE? Y / N"
                screen.blit(font.render(msg, True, (0, 0, 255)),
                            (WIDTH//2 - 120, HEIGHT//2))

            pg.display.update()
            clock.tick(FPS)

            if next_stage:
                break


# =====================
if __name__ == "__main__":
    main()
