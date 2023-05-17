import numpy as np
import pygame as pg
import math
import random
from random import randint, gauss

pg.init()
pg.font.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SCREEN_SIZE = (800, 600)

#test 2 
def rand_color():
    return (randint(0, 255), randint(0, 255), randint(0, 255))

class GameObject:

    def move(self):
        pass
    
    def draw(self, screen):
        pass  


class Shell(GameObject):
    '''
    The ball class. Creates a ball, controls it's movement and implement it's rendering.
    '''
    # we added a sides variable to implement various types of projectiles
    # the number of sides is a random number between 0 and 4
    # 0,1,2 will draw a circle, 3 will draw a triangular shape, 4 will draw a square/rectangle

    def __init__(self, coord, vel, rad = 20, color = None, sides = 0):
        '''
        Constructor method. Initializes ball's parameters and initial values.
        '''
        self.coord = coord
        self.vel = vel
        if color == None:
            color = rand_color()
        self.color = color
        self.rad = rad
        self.sides = randint(0, 4)
        self.is_alive = True

    def check_corners(self, refl_ort = 0.8, refl_par = 0.9):
        '''
        Reflects ball's velocity when ball bumps into the screen corners. Implements inelastic rebounce.
        '''
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1-i] = int(self.vel[1-i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1-i] = int(self.vel[1-i] * refl_par)

    def move(self, time = 1, grav = 0):
        '''
        Moves the ball according to it's velocity and time step.
        Changes the ball's velocity due to gravitational force.
        '''
        self.vel[1] += grav
        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.check_corners()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
            self.is_alive = False

    def draw(self, screen):
        '''
        Draws the shell on appropriate surface.
        '''
        # checks what to draw depending on number of sides
        # 0,1,2 will draw a circle, 3 will draw a triangular shape, 4 will draw a square/rectangle

        if self.sides == 4:
            pg.draw.polygon(screen, self.color, self.get_square_points())
        elif self.sides == 3:
            pg.draw.polygon(screen, self.color, self.get_polygon_points(), self.rad)
        else:
            pg.draw.circle(screen, self.color, self.coord, self.rad)

    # here we create a function to define the points of a square/rectangle if the number of sides is 4
    # we store the coordinates in a list of tuples

    def get_square_points(self):
        """
        Helper method to calculate the points of the square.
        """
        x, y = self.coord
        points = [(x - self.rad, y - self.rad), 
                 (x + self.rad, y - self.rad), 
                 (x + self.rad, y + self.rad), 
                 (x - self.rad, y + self.rad)]
        return points

    # this is similar to the get_square_points function but it is for polygons. 
    # this will get the points to shapes with the number of sides being 3

    def get_polygon_points(self):
        '''
        Helper method to calculate the points of the polygon.
        '''

        # polygons have angles so we need to use the math library
        # depending on the number of sides, we call a loop to continue to generate coordinate points

        angle = 2 * math.pi / self.sides
        points = []
        for i in range(self.sides):
            x = int(self.rad * math.cos(i * angle))
            y = int(self.rad * math.sin(i * angle))
            points.append((self.coord[0] + x, self.coord[1] + y))
        return points

class Bomb (GameObject):
    '''
    Bomb class. Creates bombs, manages their movement and collision with the user's cannon.
    '''
    def __init__(self, coord=None, vel=None, rad=10, color=RED):
        if coord is None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad), 0]
        if vel is None:
            vel = [0, 5]
        self.coord = coord
        self.vel = vel
        self.rad = rad
        if color is None:
            color = rand_color()
        self.color = color
        self.is_alive = True

    def move(self):
        '''
        Moves the bomb according to its velocity.
        '''
        self.coord[0] += self.vel[0]
        self.coord[1] += self.vel[1]

    def check_collision(self, cannon):
        '''
        Checks if the bomb collides with the user's cannon.
        '''
        dist = sum([(self.coord[i] - cannon.coord[i])**2 for i in range(2)])**0.5
        min_dist = self.rad + cannon.rad
        return dist <= min_dist

    def draw(self, screen):
        '''
        Draws the bomb on the screen.
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad) 


class Cannon(GameObject):
    '''
    Cannon class. Manages it's renderring, movement and striking.
    '''
    def __init__(self, coord=[30, SCREEN_SIZE[1]//2], angle=0, max_pow=50, min_pow=10, color=RED):
        '''
        Constructor method. Sets coordinate, direction, minimum and maximum power and color of the gun.
        '''
        self.coord = coord
        self.angle = angle
        self.max_pow = max_pow
        self.min_pow = min_pow
        self.color = color
        self.active = False
        self.pow = min_pow
   
    def activate(self):
        '''
        Activates gun's charge.
        '''
        self.active = True

    def gain(self, inc=2):
        '''
        Increases current gun charge power.
        '''
        if self.active and self.pow < self.max_pow:
            self.pow += inc

    def strike(self):
        '''
        Creates ball, according to gun's direction and current charge power.
        '''
        vel = self.pow
        angle = self.angle
        ball = Shell(list(self.coord), [int(vel * np.cos(angle)), int(vel * np.sin(angle))])
        self.pow = self.min_pow
        self.active = False
        self.last_user_shot_time = pg.time.get_ticks()
        return ball
        
    def set_angle(self, target_pos):
        '''
        Sets gun's direction to target position.
        '''
        self.angle = np.arctan2(target_pos[1] - self.coord[1], target_pos[0] - self.coord[0])

        # created separate functions for vertical and horizontal movement of the cannon
    def verticalMove(self, inc):
        if (self.coord[1] > 30 or inc > 0) and (self.coord[1] < SCREEN_SIZE[1] - 30 or inc < 0):
            self.coord[1] += inc

    def horizontalMove(self, inc):

        if (self.coord[0] > 30 or inc > 0) and (self.coord[0] < SCREEN_SIZE[0] - 30 or inc < 0):
            self.coord[0] += inc

    def draw(self, screen):
        '''
        Draws the gun on the screen.
        '''
        
        gun_shape = []
        vec_1 = np.array([int(5*np.cos(self.angle - np.pi/2)), int(5*np.sin(self.angle - np.pi/2))])
        vec_2 = np.array([int(self.pow*np.cos(self.angle)), int(self.pow*np.sin(self.angle))])
        gun_pos = np.array(self.coord)
        gun_shape.append((gun_pos + vec_1).tolist())
        gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
        gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
        gun_shape.append((gun_pos - vec_1).tolist())
        pg.draw.polygon(screen, self.color, gun_shape)


class Target(GameObject):
    '''
    Target class. Creates target, manages it's rendering and collision with a ball event.
    '''
    def __init__(self, coord=None, color=None, rad=30, sides = 0):
        '''
        Constructor method. Sets coordinate, color and radius of the target.
        '''
        if coord == None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad), randint(rad, SCREEN_SIZE[1] - rad)]
        self.coord = coord
        self.rad = rad
        self.sides = randint(0, 4)

        if color == None:
            color = rand_color()
        self.color = color
        
    
    def check_collision(self, ball):
        '''
        Checks whether the ball bumps into target.
        '''
        dist = sum([(self.coord[i] - ball.coord[i])**2 for i in range(2)])**0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen):
        '''
        Draws the target on the screen
        '''
        # checks what to draw depending on number of sides
        # 0,1,2 will draw a circle, 3 will draw a triangular shape, 4 will draw a square/rectangle

        if self.sides == 4:
            pg.draw.polygon(screen, self.color, self.get_square_points())
        elif self.sides == 3:
            pg.draw.polygon(screen, self.color, self.get_polygon_points(), self.rad)
        else:
            pg.draw.circle(screen, self.color, self.coord, self.rad)

    # here we create a function to define the points of a square/rectangle if the number of sides is 4
    # we store the coordinates in a list of tuples

    def get_square_points(self):
        """
        Helper method to calculate the points of the square.
        """
        x, y = self.coord
        points = [(x - self.rad, y - self.rad), 
                 (x + self.rad, y - self.rad), 
                 (x + self.rad, y + self.rad), 
                 (x - self.rad, y + self.rad)]
        return points

    # this is similar to the get_square_points function but it is for polygons. 
    # this will get the points to shapes with the number of sides being 3

    def get_polygon_points(self):
        '''
        Helper method to calculate the points of the polygon.
        '''

        # polygons have angles so we need to use the math library
        # depending on the number of sides, we call a loop to continue to generate coordinate points

        angle = 2 * math.pi / self.sides
        points = []
        for i in range(self.sides):
            x = int(self.rad * math.cos(i * angle))
            y = int(self.rad * math.sin(i * angle))
            points.append((self.coord[0] + x, self.coord[1] + y))
        return points

    def move(self):
        """
        This type of target can't move at all.
        :return: None
        """
        pass

class EnemyCannon(Cannon):
    '''
    EnemyCannon class. Inherits methods from Cannon
    '''
    def __init__(self, coord=[SCREEN_SIZE[0]-30, SCREEN_SIZE[1]//2], angle=0, max_pow=50, min_pow=10, color=BLUE):
        super().__init__(coord, angle, max_pow, min_pow, color)
        self.time_to_shoot = 2 # time delay to shoot in frames
        self.shoot_time = None # time the cannon shot
        #changed power to enemy cannon to 35
        self.pow = 35

    '''
    Enemy Cannon Movement function that makes the cannon go either vertical or horizontal after every user movement
    '''
    def cannon_movement(self):
        self.verticalMove(random.randint(-30, 30))
        self.horizontalMove(random.randint(-30, 30))

    # used the same strike function in cannon parent class
    def strike(self):
        vel = self.pow
        angle = self.angle
        # adjussted the angle so it shoots towards the user cannon
        ball = Shell(list(self.coord), [int(35 * np.cos(angle + 180)), int(35 * np.sin(angle + 180))])
        self.pow = self.min_pow
        self.active = False
        self.last_user_shot_time = pg.time.get_ticks()
        return ball
    
    def shoot(self, last_user_shot_time):
        current_time = pg.time.get_ticks()
        elapsed_time = current_time - last_user_shot_time
        if elapsed_time >= 2000:  # 2000 milliseconds = 2 seconds
            ball = self.strike()
            last_user_shot_time = current_time
        
    def aim_at_user(self, user_coord):
        '''
        Adjust the angle of the enemy cannon to aim at the user cannon.
        '''
        dx = user_coord[0] - self.coord[0]
        dy = user_coord[1] - self.coord[1]
        self.angle = math.degrees(math.atan2(dy, dx))
        return self.angle


class MovingTargets(Target):
    def __init__(self, coord = None, color = None, rad = 30, sides = 0):
        super().__init__(coord, color, rad)
        self.vx = randint(-2, +2)
        self.vy = randint(-2, +2)
        self.x_offset = randint(0, 360)
        self.y_offset = randint(0, 360)
        self.ax = 0.1  # acceleration in x direction
        self.ay = 0.1  # acceleration in y direction

    # created 2 different types of movement for moving targets

    # this is the regular movement as it is static
    def linearMovement(self):
        self.coord[0] += self.vx
        self.coord[1] += self.vy

    # this movement accelerates the target making it more difficult to hit
    def accelerateMovement(self):
        self.vx += self.ax
        self.vy += self.ay
        self.coord[0] += self.vx
        self.coord[1] += self.vy

    # we generate a random integer between 0 and 1.
    # 1 = linear movement
    # 2 = accelerated movement
    def move(self):
        movement_type = randint(0, 1)
        if movement_type == 0:
            self.linearMovement()
        elif movement_type == 1:
            self.accelerateMovement()

class ScoreTable:
    '''
    Score table class.
    '''
    def __init__(self, t_destr=0, b_used=0):
        self.t_destr = t_destr
        self.b_used = b_used
        self.font = pg.font.SysFont("dejavusansmono", 25)

    def score(self):
        '''
        Score calculation method.
        '''
        return self.t_destr - self.b_used

    def draw(self, screen):
        score_surf = []
        score_surf.append(self.font.render("Destroyed: {}".format(self.t_destr), True, WHITE))
        score_surf.append(self.font.render("Balls used: {}".format(self.b_used), True, WHITE))
        score_surf.append(self.font.render("Total: {}".format(self.score()), True, RED))
        for i in range(3):
            screen.blit(score_surf[i], [10, 10 + 30*i])

class Manager:
    '''
    Class that manages events' handling, ball's motion and collision, target creation, etc.
    '''
    last_user_shot_time = 0

    def __init__(self, n_targets=1):
        self.balls = []
        self.enemy_balls = []
        self.gun = Cannon()
        self.enemy_cannon = EnemyCannon()
        self.targets = []
        self.score_t = ScoreTable()
        self.n_targets = n_targets
        self.bombs = []
        self.new_mission()
        self.user_coord = None

    def new_mission(self):
        '''
        Adds new targets.
        '''
        for i in range(self.n_targets):
            self.targets.append(MovingTargets(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
            self.targets.append(Target(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
            
        # bombs move until user shoots targets
        
        for target in self.targets:
            self.bombs.append(Bomb(coord=target.coord))

    def process(self, events, screen):
        '''
        Runs all necessary method for each iteration. Adds new targets, if previous are destroyed.
        '''
        done = self.handle_events(events)
        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)
        
        self.move()
        self.collide()
        self.draw(screen)
        if len(self.targets) == 0 and len(self.balls) == 0:
            self.new_mission()

        return done

    def handle_events(self, events):
        '''
        Handles events from keyboard, mouse, etc.
        '''
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.gun.verticalMove(-5)
                    self.enemy_cannon.cannon_movement()
                elif event.key == pg.K_DOWN:
                    self.gun.verticalMove(5)
                    self.enemy_cannon.cannon_movement()
                # implemented the horizontal movement with the left and right keys
                elif event.key == pg.K_LEFT:
                    self.gun.horizontalMove(-5)
                    self.enemy_cannon.cannon_movement()
                elif event.key == pg.K_RIGHT:
                    self.gun.horizontalMove(5)
                    self.enemy_cannon.cannon_movement()
                elif event.key == pg.K_ESCAPE:
                    done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.user_coord = pg.mouse.get_pos()
                if event.button == 1:
                    self.gun.activate()
                    self.enemy_cannon.activate()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.strike())
                    # enemy cannon shoots every time user shoots
                    self.enemy_balls.append(self.enemy_cannon.strike())
                    self.score_t.b_used += 1
        return done

    def draw(self, screen):
        '''
        Runs balls', gun's, targets' and score table's drawing method.
        '''
        for ball in self.balls:
            ball.draw(screen)
        # enemy_balls treated the same as user's balls
        for ball in self.enemy_balls:
            ball.draw(screen)
        for target in self.targets:
            target.draw(screen)
        for bomb in self.bombs:
            bomb.draw(screen)
        self.gun.draw(screen)
        self.enemy_cannon.draw(screen) 
        self.score_t.draw(screen)

    def move(self):
        '''
        Runs balls' and gun's movement method, removes dead balls.
        '''
        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move(grav=2)
            if not ball.is_alive:
                dead_balls.append(i)
        # we want the enemy  balls to move
        for i, ball in enumerate(self.enemy_balls):
            ball.move(grav=2)
            if not ball.is_alive:
                dead_balls.append(i)

        for i in reversed(dead_balls):
            self.balls.pop(i)
            self.enemy_balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move()
        self.gun.gain()

    def collide(self):
        '''
        Checks whether balls bump into targets, sets balls' alive trigger.
        '''
        # we do not have enemy balls here as we only want it to collide with the user's balls
        collisions = []
        targets_c = []
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
        targets_c.sort()
        for j in reversed(targets_c):
            self.score_t.t_destr += 1
            self.targets.pop(j)

    def enough_time_passed(self):
        current_time = pg.time.get_ticks()
        elapsed_time = current_time - self.last_user_shot_time
        return elapsed_time >= 2000
    
    def handle_bombs(self):
        '''
        Handles bomb motion, collision, and removal.
        '''
        for bomb in self.bombs:
            bomb.move()
            if bomb.check_collision(self.user_cannon):
                self.user_cannon_hit = True
            if bomb.coord[1] > SCREEN_SIZE[1]:
                self.bombs.remove(bomb)

    def draw_bombs(self, screen):
        '''
        Draws the bombs on the screen.
        '''
        for bomb in self.bombs:
            bomb.draw(screen)
    
screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("The gun of Khiryanov")

done = False
clock = pg.time.Clock()

mgr = Manager(n_targets=4)


while not done:
    
    clock.tick(15)
    screen.fill(BLACK)

    done = mgr.process(pg.event.get(), screen)

    pg.display.flip()


pg.quit()
