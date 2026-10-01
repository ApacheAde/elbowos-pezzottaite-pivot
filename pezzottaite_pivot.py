#!/usr/bin/env python3
"""Pezzottaite Pivot — neon rotary colour-catch arcade for ElbowOS.

Shards fly in from the rim. Spin the eight-notch spindle so a matching
colour faces each shard as it hits the hub. A / D or arrows spin.
Space boosts spin. R restarts. Default run writes a 9:16 autoplay reel.
"""
import math
import os
import random
import subprocess
import sys

import pygame

W, H = 1080, 1920
CX, CY = 540, 980
FPS = 30
N = 8
STEP = math.tau / N
PAL = [(255, 72, 98), (72, 255, 176), (255, 196, 56), (72, 168, 255)]
INK = (8, 12, 22)
HUB = 176
OUT = os.environ.get("SPINDLE_OUT", "PezzottaitePivot_ElbowOS.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def ang_diff(a, b):
    return (a - b + math.pi) % math.tau - math.pi


class Shard:
    def __init__(self, tick):
        self.ang = random.random() * math.tau
        self.dist = random.uniform(760, 860)
        self.col = random.randrange(4)
        self.spd = random.uniform(6.4, 9.2)
        self.alive = True
        self.born = tick


class Game:
    def __init__(self, auto=False):
        self.auto = auto
        self.reset()

    def reset(self):
        self.spin = 0.0
        self.omega = 0.0
        self.shards = []
        self.sparks = []
        self.score = 0
        self.combo = 0
        self.best = 0
        self.tick = 0
        self.flash = 0
        self.miss = 0
        self.rng = random.Random(7 if self.auto else None)

    def spawn(self):
        s = Shard(self.tick)
        s.ang = self.rng.random() * math.tau
        s.col = self.rng.randrange(4)
        s.dist = self.rng.uniform(780, 880)
        s.spd = self.rng.uniform(6.2, 8.6)
        self.shards.append(s)

    def steer(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.omega -= 0.012
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.omega += 0.012
        if keys[pygame.K_SPACE]:
            self.omega *= 1.08

    def autopilot(self):
        live = [s for s in self.shards if s.alive]
        if not live:
            self.omega *= 0.92
            return
        s = min(live, key=lambda z: z.dist)
        best = None
        for i in range(N):
            if i % 4 != s.col:
                continue
            target = s.ang - i * STEP
            d = ang_diff(target, self.spin)
            if best is None or abs(d) < abs(best):
                best = d
        self.omega += max(-0.02, min(0.02, best * 0.18))

    def update(self):
        self.tick += 1
        if self.auto:
            self.autopilot()
        self.omega *= 0.90
        self.spin = (self.spin + self.omega) % math.tau
        if self.tick % 16 == 1 and len(self.shards) < 6:
            self.spawn()
        for s in self.shards:
            if not s.alive:
                continue
            s.dist -= s.spd
            if s.dist <= HUB + 8:
                self.resolve(s)
        self.shards = [s for s in self.shards if s.alive and s.dist > 40]
        nxt = []
        for p in self.sparks:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
            if p[4] > 0:
                nxt.append(p)
        self.sparks = nxt
        if self.flash:
            self.flash -= 1

    def resolve(self, s):
        s.alive = False
        nearest = min(range(N), key=lambda i: abs(ang_diff(self.spin + i * STEP, s.ang)))
        ok = nearest % 4 == s.col and abs(ang_diff(self.spin + nearest * STEP, s.ang)) < 0.42
        x = CX + math.cos(s.ang) * (HUB + 10)
        y = CY + math.sin(s.ang) * (HUB + 10)
        col = PAL[s.col] if ok else (255, 60, 80)
        for _ in range(14):
            a = s.ang + self.rng.uniform(-0.8, 0.8)
            sp = self.rng.uniform(2, 9)
            self.sparks.append([x, y, math.cos(a) * sp, math.sin(a) * sp, 16, col])
        if ok:
            self.combo += 1
            self.best = max(self.best, self.combo)
            self.score += 100 + 20 * self.combo
            self.flash = 8
        else:
            self.combo = 0
            self.miss += 1
            self.flash = -8

    def draw(self, surf, font, small, big):
        surf.fill(INK)
        pulse = 0.5 + 0.5 * math.sin(self.tick * 0.08)
        for i in range(10, 0, -1):
            shade = (12 + i * 3, 18 + i, 16 + i * 4)
            pygame.draw.circle(surf, shade, (CX, CY), 90 + i * 78, 6)
        for k in range(24):
            a = k * math.tau / 24 + self.tick * 0.004
            pygame.draw.line(surf, (28, 42, 36),
                             (CX + math.cos(a) * 240, CY + math.sin(a) * 240),
                             (CX + math.cos(a) * 860, CY + math.sin(a) * 860), 2)
        pygame.draw.circle(surf, (18, 28, 24), (CX, CY), 820, 4)
        for i in range(N):
            a = self.spin + i * STEP
            col = PAL[i % 4]
            x1 = CX + math.cos(a) * 70
            y1 = CY + math.sin(a) * 70
            x2 = CX + math.cos(a) * HUB
            y2 = CY + math.sin(a) * HUB
            pygame.draw.line(surf, col, (x1, y1), (x2, y2), 22)
            pygame.draw.circle(surf, col, (int(x2), int(y2)), 26)
            pygame.draw.circle(surf, (255, 255, 240), (int(x2), int(y2)), 8)
        hub_c = (255, 236, 170) if self.flash > 0 else (240, 220, 160)
        if self.flash < 0:
            hub_c = (255, 90, 100)
        pygame.draw.circle(surf, hub_c, (CX, CY), 62)
        pygame.draw.circle(surf, (20, 16, 10), (CX, CY), 62, 4)
        pygame.draw.circle(surf, (40, 30, 16), (CX, CY), 18)
        for s in self.shards:
            if not s.alive:
                continue
            x = CX + math.cos(s.ang) * s.dist
            y = CY + math.sin(s.ang) * s.dist
            col = PAL[s.col]
            trail = (CX + math.cos(s.ang) * (s.dist + 36), CY + math.sin(s.ang) * (s.dist + 36))
            pygame.draw.line(surf, col, trail, (x, y), 6)
            pts = []
            for k in range(4):
                aa = s.ang + k * math.pi / 2 + 0.4
                rad = 22 if k % 2 == 0 else 12
                pts.append((x + math.cos(aa) * rad, y + math.sin(aa) * rad))
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, (255, 255, 255), pts, 2)
        for p in self.sparks:
            pygame.draw.circle(surf, p[5], (int(p[0]), int(p[1])), max(1, p[4] // 4))
        banner = pygame.Surface((W, 210), pygame.SRCALPHA)
        banner.fill((6, 10, 16, 210))
        surf.blit(banner, (0, 0))
        foot = pygame.Surface((W, 160), pygame.SRCALPHA)
        foot.fill((6, 10, 16, 210))
        surf.blit(foot, (0, H - 160))
        title = big.render("PEZZOTTAITE PIVOT", True, (186, 255, 92))
        surf.blit(title, (W // 2 - title.get_width() // 2, 48))
        sub = small.render("match the notch  \u00b7  spin the hub", True, (255, 196, 120))
        surf.blit(sub, (W // 2 - sub.get_width() // 2, 132))
        sc = font.render(f"SCORE  {self.score}", True, (255, 244, 220))
        surf.blit(sc, (48, 1760))
        cb = font.render(f"COMBO  {self.combo}", True, PAL[self.tick // 8 % 4])
        surf.blit(cb, (W - cb.get_width() - 48, 1760))
        tag = small.render("x.com/ElbowOS", True, (120, 255, 210))
        surf.blit(tag, (W // 2 - tag.get_width() // 2, 1836))
        if pulse > 0.85:
            pygame.draw.circle(surf, (186, 255, 92), (CX, CY), int(HUB + 18 + pulse * 6), 2)


def fonts():
    path = FONT if os.path.exists(FONT) else None
    big = pygame.font.Font(path, 72)
    font = pygame.font.Font(path, 42)
    small = pygame.font.Font(path, 32)
    return font, small, big


def record():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    surf = pygame.Surface((W, H))
    font, small, big = fonts()
    g = Game(auto=True)
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames = FPS * 15
    try:
        for _ in range(frames):
            g.update()
            g.draw(surf, font, small, big)
            proc.stdin.write(pygame.image.tobytes(surf, "RGB"))
    finally:
        proc.stdin.close()
        code = proc.wait()
    pygame.quit()
    if code != 0:
        raise SystemExit(f"ffmpeg failed: {code}")
    print(f"wrote {OUT} score={g.score} combo={g.best}")


def play():
    pygame.init()
    screen = pygame.display.set_mode((W // 2, H // 2))
    pygame.display.set_caption("Pezzottaite Pivot — ElbowOS")
    canvas = pygame.Surface((W, H))
    font, small, big = fonts()
    g = Game(auto=False)
    clock = pygame.time.Clock()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                g.reset()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False
        keys = pygame.key.get_pressed()
        g.steer(keys)
        g.update()
        g.draw(canvas, font, small, big)
        pygame.transform.smoothscale(canvas, screen.get_size(), screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    if "--play" in sys.argv:
        play()
    else:
        record()
