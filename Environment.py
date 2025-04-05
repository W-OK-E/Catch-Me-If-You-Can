import pygame
import random
import math
import time

class ChaseEnvironment:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800
        self.border_width = 10
        self.chaser_size = 20
        self.target_size = 30
        self.chaser_color = (0, 0, 255)
        self.target_color = (255, 0, 0)
        self.chaser_speed = 8
        self.target_speed = 4
        self.chaser_acceleration = 0.5
        self.max_chaser_speed = 16
        self.target_change_direction_threshold = 150
        self.chaser_positions = [[self.screen_width//2, self.screen_height//2]]
        self.reset()

    def reset(self):
        self.chaser_x = self.screen_width // 2
        self.chaser_y = self.screen_height // 2
        self.target_x = random.randint(self.border_width + 300, self.screen_width - self.border_width - self.target_size - 300)
        self.target_y = random.randint(self.border_width + 200, self.screen_height - self.border_width - self.target_size - 200)
        self.target_dx = random.choice([-1, 1]) * self.target_speed
        self.target_dy = random.choice([-1, 1]) * self.target_speed
        self.reward = 0
        self.steps = 0
        self.score = 0
        self.chaser_positions = [[self.screen_width//2, self.screen_height//2]]
        return self.get_state()

    def chaser_action(self, action):
        if action == 0:
            self.chaser_y -= self.chaser_speed
        elif action == 1:
            self.chaser_y += self.chaser_speed
        elif action == 2:
            self.chaser_x -= self.chaser_speed
        elif action == 3:
            self.chaser_x += self.chaser_speed
        elif action == 4:
            self.chaser_speed = min(self.chaser_speed + self.chaser_acceleration, self.max_chaser_speed)
        elif action == 5:
            self.chaser_speed = max(5, self.chaser_speed - self.chaser_acceleration)
        self.chaser_x = max(self.border_width, min(self.chaser_x, self.screen_width - self.border_width - self.chaser_size))
        self.chaser_y = max(self.border_width, min(self.chaser_y, self.screen_height - self.border_width - self.chaser_size))

    def target_movement(self):
        self.target_x += self.target_dx
        self.target_y += self.target_dy
        if (self.target_x <= self.border_width + 10 or
            self.target_x >= self.screen_width - self.border_width - self.target_size - 10):
            self.target_dx *= -1
            self.target_dx += random.uniform(-0.5, 0.5)
        if (self.target_y <= self.border_width + 10 or
            self.target_y >= self.screen_height - self.border_width - self.target_size - 10):
            self.target_dy *= -1
            self.target_dy += random.uniform(-0.5, 0.5)
        self.target_x = max(self.border_width, min(self.target_x, self.screen_width - self.border_width - self.target_size))
        self.target_y = max(self.border_width, min(self.target_y, self.screen_height - self.border_width - self.target_size))
        if self.steps % self.target_change_direction_threshold == 0:
            self.target_dx = random.choice([-1, 1]) * self.target_speed + random.uniform(-1, 1)
            self.target_dy = random.choice([-1, 1]) * self.target_speed + random.uniform(-1, 1)
            magnitude = math.sqrt(self.target_dx**2 + self.target_dy**2)
            self.target_dx = (self.target_dx / magnitude) * self.target_speed
            self.target_dy = (self.target_dy / magnitude) * self.target_speed
        self.steps += 1
        distance = self.get_distance()
        if distance < 200:
            dx = self.chaser_x - self.target_x
            dy = self.chaser_y - self.target_y
            mag = math.sqrt(dx**2 + dy**2)
            if mag > 0:
                dx /= mag
                dy /= mag
                self.target_dx -= dx * 0.5
                self.target_dy -= dy * 0.5
                mag = math.sqrt(self.target_dx**2 + self.target_dy**2)
                if mag > 0:
                    self.target_dx = (self.target_dx / mag) * self.target_speed
                    self.target_dy = (self.target_dy / mag) * self.target_speed

    def get_distance(self):
        return math.sqrt((self.target_x - self.chaser_x)**2 + (self.target_y - self.chaser_y)**2)

    def get_reward(self):
        current_distance = self.get_distance()
        if current_distance <= self.chaser_size + self.target_size:
            self.reward += 10
            self.score += 1
            return 10
        elif (self.chaser_x <= self.border_width or
              self.chaser_x >= self.screen_width - self.border_width - self.chaser_size or
              self.chaser_y <= self.border_width or
              self.chaser_y >= self.screen_height - self.border_width - self.chaser_size):
            self.reward -= 5
            self.chaser_x = self.screen_width//2
            self.chaser_y = self.screen_height//2
            return -5
        else:
            if len(self.chaser_positions) >= 2:
                prev_distance = math.sqrt((self.target_x - self.chaser_positions[0][0])**2 +
                                         (self.target_y - self.chaser_positions[0][1])**2)
                if current_distance < prev_distance:
                    return 0.5
                else:
                    return -0.2
            else:
                return 0

    def step(self, action):
        self.chaser_action(action)
        self.target_movement()
        self.chaser_positions.append([self.chaser_x, self.chaser_y])
        if len(self.chaser_positions) > 5:
            self.chaser_positions.pop(0)
        reward = self.get_reward()
        state = self.get_state()
        done = False
        if reward == 10:
            done = True
            self.target_x = random.randint(self.border_width + 100, self.screen_width - self.border_width - self.target_size - 100)
            self.target_y = random.randint(self.border_width + 100, self.screen_height - self.border_width - self.target_size - 100)
            self.target_dx = random.choice([-1, 1]) * self.target_speed
            self.target_dy = random.choice([-1, 1]) * self.target_speed
            self.target_speed = min(self.target_speed + 0.2, 10)
        return state, reward, done

    def get_state(self):
        distance = self.get_distance()
        return {
            'target_x': self.target_x,
            'target_y': self.target_y,
            'chaser_x': self.chaser_x,
            'chaser_y': self.chaser_y,
            'distance': distance,
            'chaser_speed': self.chaser_speed,
            'target_speed': self.target_speed,
            'target_dx': self.target_dx,
            'target_dy': self.target_dy,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height
        }

    def render(self):
        pygame.init()
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Chase Environment")
        return screen

    def update_screen(self, screen):
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, self.chaser_color, (self.chaser_x, self.chaser_y, self.chaser_size, self.chaser_size))
        pygame.draw.rect(screen, self.target_color, (self.target_x, self.target_y, self.target_size, self.target_size))
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, self.screen_width, self.screen_height), self.border_width)
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (20, 20))
        pygame.display.flip()

    def close_window(self):
        pygame.quit()

if __name__ == "__main__":
    env = ChaseEnvironment()
    screen = env.render()
    clock = pygame.time.Clock()
    state = env.reset()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        action = None
        if keys[pygame.K_UP]:
            action = 0
        elif keys[pygame.K_DOWN]:
            action = 1
        elif keys[pygame.K_LEFT]:
            action = 2
        elif keys[pygame.K_RIGHT]:
            action = 3
        elif keys[pygame.K_SPACE]:
            action = 4
        elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            action = 5
        if action is None:
            action = random.randint(0, 5)
        next_state, reward, done = env.step(action)
        env.update_screen(screen)
        print(f"Action: {action}, Reward: {reward}, Done: {done}, Speed: {env.chaser_speed:.1f}")
        clock.tick(60)
    env.close_window()
