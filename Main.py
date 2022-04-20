# Include necessary files.
import pygame, pygame.mixer
from pygame.locals import *
from Sprite_Object import Sprite_Object
import os, random, math

# Initialize pygame
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
Window = pygame.display.set_mode((600, 400), 0, 32)

clock = pygame.time.Clock()
MENU_TIME = 10
MENU_SELECT_DELAY = 10
GAME_FRAME_RATE = 240

hitSounds = [pygame.mixer.Sound("Sounds/Hit/MetalHit0.wav"), pygame.mixer.Sound("Sounds/Hit/MetalHit1.wav"),
             pygame.mixer.Sound("Sounds/Hit/MetalHit2.wav"), pygame.mixer.Sound("Sounds/Hit/MetalHit3.wav")]
gushSound = pygame.mixer.Sound("Sounds/Wind/Gush.wav")
landNoise = pygame.mixer.Sound("Sounds/Jump/Land.wav")
jumpNoise = pygame.mixer.Sound("Sounds/Jump/Jump.wav")
boom = pygame.mixer.Sound("Sounds/Boom.wav")
hitPlayed = 0
walkChannels = 3
boxingBellSound = pygame.mixer.Sound("Sounds/66951__benboncan__boxing-bell.wav")
KOSound = pygame.mixer.Sound("Sounds/KO.wav")

# ----------Global-----------
gushSpriteF = Sprite_Object("GushF.png")
gushSpriteB = Sprite_Object("GushB.png")


# Vector class.
class Vector:
    def __init__(self):
        self._x = 0
        self._y = 0
        self._scaler = 1
        self._x2 = 0
        self._y2 = 0
        self._Mag = 0

    def magnitude(self):
        if self._x != self._x2:
            self._x -= self._x2
        else:
            self._x = 0
        if self._y != self._y2:
            self._y -= self._y2
        else:
            self._y = 0

    def Pythag(self):
        self._Mag = self._x * self._x + self._y * self._y
        if self._Mag < 0:
            self._Mag *= -1
        self._Mag = math.sqrt(self._Mag)

    def Round(self):
        round(self._x, 200)
        round(self._y, 200)

    def Round_M(self):
        round(self._Mag)

    def setDestination(self, x, y):
        self._x2 = x
        self._y2 = y

    def setBegin(self, x, y):
        self._x = x
        self._y = y

    def setSpeed(self, Speed):
        self._scaler = Speed

    def getVx(self):
        return self._x

    def getVy(self):
        return self._y

    def setVx(self, x):
        self._x = x

    def setVy(self, y):
        self._y = y

    def getSpeed(self):
        return self._scaler

    def getMag(self):
        return self._Mag

    def getdx(self):
        return self._x2

    def getdy(self):
        return self._y2

    x = property(getVx, setVx, doc="X element of the vector.")
    y = property(getVy, setVy, doc="Y element of the vector.")
    speed = property(getSpeed, setSpeed, doc="The scaler of the vector.")
    mag = property(getMag, doc="The magnitude of the vector.")
    dx = property(getdx, doc="The x destination.")
    dy = property(getdy, doc="The y destination.")


#################################

# Calculate a vector

def calculate_vector(vector, position):
    vector.magnitude()
    if position.x > vector.dx:
        if vector.x < 0:
            vector.x = vector.x * -1
    if position.y > vector.dy:
        if vector.y < 0:
            vector.y = vector.y * -1
    vector.Pythag()
    if vector.mag != 0:
        if vector.x != 0:
            vector.x = vector.x / vector.mag
        if vector.y != 0:
            vector.y = vector.y / vector.mag
    vector.x = vector.x * vector.speed
    vector.y = vector.y * vector.speed
    return vector


class XY:
    def __init__(self):
        self._x = 0
        self._y = 0

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def setX(self, value):
        self._x = value

    def setY(self, value):
        self._y = value

    x = property(getX, setX, doc="X position.")
    y = property(getY, setY, doc="Y position.")


def Move(vector, position):
    position.x = position.x + vector.x
    position.y = position.y + vector.y
    return position


# Colors.
Blue = (0, 0, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Black = (0, 0, 0)
White = (255, 255, 255)


# For collision.
class BoundingBox:
    def __init__(self):
        self.xo = 10
        self.yo = 10
        self.Position = XY()

    def setPosition(self, value):
        self.Position = value

    def getPosition(self):
        return self.Position

    def setXOffset(self, value):
        self.xo = value

    def setYOffset(self, value):
        self.yo = value

    def getXOffset(self):
        return self.xo

    def getYOffset(self):
        return self.yo

    position = property(getPosition, setPosition, doc="The position.")
    x_offset = property(getXOffset, setXOffset, doc="The x offset.")
    y_offset = property(getYOffset, setYOffset, doc="The y offset.")


class CollisionManager:
    # Calculate the reaction to a collision.
    def react(self, vector, collision_scale):
        vector.x = vector.x - vector.x * collision_scale
        vector.y = vector.y - vector.y * collision_scale
        return vector

    # Update Reactions to the collision.
    def update_physics(self, robot, other_bot):
        if robot.collision:
            robot.vector = self.react(robot.vector, robot.reaction)
            robot.collision = False
            robot.stop = False
        if robot.arm_col:
            t = robot.vector
            robot.vector = self.react(other_bot.arm_vector, robot.reaction)
            robot.vector.x = -robot.vector.x
            robot.vector.y = -robot.vector.y
            robot.position = Move(robot.vector, robot.position)
            robot.vector = t
            robot.arm_col = False
            robot.stop = True
        if robot.collision_frames < robot.collision_time:
            robot.collision_frames += 1
        else:
            robot.collision_frames = 0
            robot.vector.x = 0
            robot.vector.y = 0
            robot.stop = True
        return robot

    # Detect collisions.
    def check_collision(self, a: BoundingBox, b):
        x = a.position.x + a.x_offset > b.position.x - b.x_offset and \
            a.position.x - a.x_offset < b.position.x + b.x_offset
        y = a.position.y + a.y_offset > b.position.y - b.y_offset and \
            a.position.y - a.y_offset < b.position.y + b.y_offset
        return x == y and y


CM = CollisionManager()


# AI and player base class.
class RobotBase:
    def __init__(self, F, B, AF, AB, JF, JB):
        global walkChannels
        self._ReactM = 2
        self._Col = False
        self.ColFR = 0
        self.Box = BoundingBox()
        self._Forward = Sprite_Object(F)
        self._Back = Sprite_Object(B)
        self._ArmF = Sprite_Object(AF)
        self._ArmB = Sprite_Object(AB)
        self._JumpF = Sprite_Object(JF)
        self._JumpB = Sprite_Object(JB)
        self._Fwd = True
        self._Bkwd = False
        self._Jump = False
        self._Punch = False
        self._Vector = Vector()
        self._Position = XY()
        self._ArmPos = XY()
        self._ArmVect = Vector()
        self._ArmDis = XY()
        self._JmpF = False
        self.jc = 0
        self._coltime = 100
        self._Stop = True
        self._ReactM = 4
        self._ArmBox = BoundingBox()
        self._ArmTime = 0
        self._ArmColl = False
        self._Health = 100
        self._kicked = False
        self._kick = False
        self._kickCount = 0
        self._kickBox = BoundingBox()
        self._kickBox.x_offset = 60
        self._kickBox.y_offset = 40
        self._gushTime = 0
        self.walkSound = pygame.mixer.Sound("Sounds/Robo/Walk.wav")
        walkChannels += 1
        self.walkChannel = walkChannels

    def get_at(self):
        return self._ArmTime

    def set_at(self, value):
        self._ArmTime = value

    def get_cl(self):
        return self._coltime

    def set_cl(self, value):
        self._coltime = value

    def get_r(self):
        return self._ReactM

    def set_r(self, value):
        self._ReactM = value

    def get_collision(self):
        return self._Col

    def get_collision_frames(self):
        return self.ColFR

    def set_collision(self, value):
        self._Col = value

    def set_collision_frames(self, value):
        self.ColFR = value

    def set_bot_position(self, X, Y):
        self._Position.x = X
        self._Position.y = Y
        self._ArmPos.x = X + 10
        self._ArmPos.y = Y + 30
        self.Box.position.x = X
        self.Box.position.y = Y

    def get_box(self):
        return self.Box

    def set_box(self, value):
        self.Box = value

    def ArmCalc(self):
        self._ArmDis.x = self._Position.x - self._ArmPos.x
        self._ArmDis.y = self._Position.y - self._ArmPos.y

    def getV(self):
        return self._Vector

    def getP(self):
        return self._Position

    def setP(self, value):
        self._Position = value
        self.Box.position = value

    def setV(self, value):
        self._Vector = value

    def getAV(self):
        return self._ArmVect

    def getAP(self):
        return self._ArmPos

    def setAV(self, value):
        self._ArmVect = value

    def setAP(self, value):
        self._ArmPos = value

    def setFwd(self, value):
        if self._Bkwd and value:
            self._Bkwd = False
        else:
            self._Bkwd = True
        self._Fwd = value

    def setBkwd(self, value):
        if self._Fwd and value:
            self._Fwd = False
        else:
            self._Fwd = True
        self._Bkwd = value

    def setJump(self, value):
        self._Jump = value

    def getFwd(self):
        return self._Fwd

    def getBkwd(self):
        return self._Bkwd

    def getJump(self):
        return self._Jump

    def Draw(self):
        global gushSpriteF
        global gushSpriteB
        if self._Fwd:
            if not self._Jump:
                Window.blit(self._Forward.sprite, (self._Position.x, self._Position.y))
            else:
                Window.blit(self._JumpF.sprite, (self._Position.x, self._Position.y))
            Window.blit(self._ArmF.sprite, (self._ArmPos.x, self._ArmPos.y))
            if self._gushTime > 0:
                Window.blit(gushSpriteF.sprite, (self._Position.x, self._Position.y))
                self._gushTime -= 1
        else:
            if self._Jump:
                Window.blit(self._Back.sprite, (self._Position.x, self._Position.y))
            else:
                Window.blit(self._JumpB.sprite, (self._Position.x, self._Position.y))
            Window.blit(self._ArmB.sprite, (self._ArmPos.x, self._ArmPos.y))
            if self._gushTime > 0:
                Window.blit(gushSpriteB.sprite, (self._Position.x, self._Position.y))
                self._gushTime -= 1

    def Update_Arms(self):
        self._ArmPos.x = self._Position.x
        self._ArmPos.x -= self._ArmDis.x
        self._ArmPos.y = self._Position.y
        self._ArmPos.y -= self._ArmDis.y

    def Jump(self):
        global landNoise
        global jumpNoise
        if self._Jump:
            if self.jc == 1:
                pygame.mixer.Channel(2).play(jumpNoise)
            self.jc += 1
            if self.jc >= 100:
                self._JmpF = True
                self._Position.y += 2
                if self._Position.y > 270:
                    self.jc = 0
                    self._JmpF = False
                    self._Jump = False
                    pygame.mixer.Channel(2).play(landNoise)
            else:
                self._Position.y -= 3
        else:
            self.jc = 0

    def getStop(self):
        return self._Stop

    def setStop(self, value):
        self._Stop = value

    def getAB(self):
        return self._ArmBox

    def setAB(self, value):
        self._ArmBox = value

    def setACll(self, value):
        self._ArmColl = value

    def getACll(self):
        return self._ArmColl

    def getGushTime(self):
        return self._gushTime

    def setGushTime(self, value):
        self._gushTime = value

    def getHealth(self):
        return self._Health

    def setHealth(self, value):
        self._Health = value

    def SetFowardRaw(self, value):
        self._Fwd = value

    def SetBackwardRaw(self, value):
        self._Bkwd = value

    def Punch(self):
        if self._ArmTime >= 1:
            pass
        else:
            self._ArmVect.setBegin(self._ArmPos.x, self._ArmPos.y)
            if self._Fwd:
                self._ArmVect.setDestination(self._ArmPos.x + 10, self._ArmPos.y)
                self._ArmVect = calculate_vector(self._ArmVect, self._ArmPos)
                self._ArmTime = 1
            else:
                self._ArmVect.setDestination(self._ArmPos.x - 10, self._ArmPos.y)
                self._ArmVect = calculate_vector(self._ArmVect, self._ArmPos)
                self._ArmTime = 1

    def CheckPunch(self):
        if self._ArmTime >= 1:
            self._ArmTime += 1
            self._ArmPos = Move(self._ArmVect, self._ArmPos)
            self._ArmBox.position.x = self._ArmPos.x
            self._ArmBox.position.y = self._ArmPos.y
            self._ArmBox.x_offset = 32
            self._ArmBox.y_offset = 16
        if self._ArmTime > 20:
            self._ArmTime = 0
            self._ArmVect.x = 0
            self._ArmVect.y = 0
            self._ArmPos.x = self._Position.x + 10
            self._ArmPos.y = self._Position.y + 30

    vector = property(getV, setV, doc="The vector.")
    position = property(getP, setP, doc="The position.")
    arm_position = property(getAP, setAP, doc="The arms position.")
    arm_vector = property(getAV, setAV, doc="The arms vector.")
    foward = property(getFwd, setFwd)
    back = property(getBkwd, setBkwd)
    jump = property(getJump, setJump)
    box = property(get_box, set_box, doc="A box for bounding box collision.")
    collision = property(get_collision, set_collision, doc="A bool that tells if there is a collision or not.")
    collision_frames = property(get_collision_frames, set_collision_frames,
                                doc="Count how many frames after a collision.")
    reaction = property(get_r, set_r, doc="How much to multiply the vector from a collision by.")
    collision_time = property(get_cl, set_cl, doc="How much time the reaction for a collision should last.")
    stop = property(getStop, setStop, doc="Should the robot cease to move?")
    arm_box = property(getAB, setAB, doc="The bounding box for the arm.")
    arm_col = property(getACll, setACll, doc="Did we collide with a robots arm?")
    health = property(getHealth, setHealth, doc="The robot's health.")
    arm_time = property(get_at, set_at, doc="To tell if the robot is punching")
    gushTime = property(getGushTime, setGushTime, doc="The amount of time to display wind.")


class PlayerBase(RobotBase):
    def control(self):
        pass


# Input variables.
Up = False
Down = False
Left = False
Right = False
W = False
A = False
S = False
D = False
Z = False
X = False
RShift = False
r_control = False
R = False
H = False


# The player 1 and player 2 class will be slightly different.
class Player1(PlayerBase):
    def control(self):
        if self._Stop:
            if A:
                self._Vector.setBegin(self._Position.x, self._Position.y)
                self._Vector.setDestination(self._Position.x + 1, self._Position.y)
                self._Vector = calculate_vector(self._Vector, self._Position)
                self._Fwd = True
                self._Bkwd = False
            if D:
                self._Vector.setBegin(self._Position.x, self._Position.y)
                self._Vector.setDestination(self._Position.x - 1, self._Position.y)
                self._Vector = calculate_vector(self._Vector, self._Position)
                self._Fwd = False
                self._Bkwd = True
            if W:
                self._Jump = True


# The player 2 and player 1 classes are slightly different.
class Player2(PlayerBase):
    def control(self):
        if self._Stop:
            if Left:
                self._Vector.setBegin(self._Position.x, self._Position.y)
                self._Vector.setDestination(self._Position.x + 1, self._Position.y)
                self._Vector = calculate_vector(self._Vector, self._Position)
                self._Fwd = True
                self._Bkwd = False
            if Right:
                self._Vector.setBegin(self._Position.x, self._Position.y)
                self._Vector.setDestination(self._Position.x - 1, self._Position.y)
                self._Vector = calculate_vector(self._Vector, self._Position)
                self._Fwd = False
                self._Bkwd = True
            if Up:
                self._Jump = True


def combat(robot: RobotBase, punch: bool):
    if punch:
        robot.Punch()
    robot.CheckPunch()
    return robot


# Makes sure the robot does not exit the level.
def keep_in_level(robot: RobotBase):
    if robot.position.x > 600:
        robot.vector.x = -1
        robot.vector.y = 0
        t = robot.vector
        while robot.position.x > 560:
            robot.position = Move(robot.vector, robot.position)
        robot.vector = t
    if robot.position.x < 0:
        robot.vector.x = 1
        robot.vector.y = 0
        t = robot.vector
        while robot.position.x < 40:
            robot.position = Move(robot.vector, robot.position)
        robot.vector = t
    return robot


# If the robot gets "punched" its health will be decremented."
def Hurt(Robot, OtherBot):
    global hitSounds
    global hitPlayed
    if Robot.arm_col and OtherBot.arm_time >= 1:
        Robot.health = Robot.health - 1
        if hitPlayed < 16:
            pygame.mixer.Channel(0).play(hitSounds[random.randint(0, 2)])
            hitPlayed += 1
        else:
            pygame.mixer.Channel(0).play(hitSounds[3])
            hitPlayed = 0
        if OtherBot.position.y < 250:
            pygame.mixer.Channel(1).play(gushSound)
            Robot.gushTime = 20
    return Robot


# Manages all the collisions.
def ManageCollision(Robot, OtherBot):
    Robot.collision = CM.check_collision(Robot.box, OtherBot.box)
    Robot.arm_col = CM.check_collision(OtherBot.arm_box, Robot.box)
    Robot = Hurt(Robot, OtherBot)
    return Robot


def RobotWalkSound(robot):
    robot.vector.Pythag()
    if robot.vector.mag > .4 and robot.position.y >= 270:
        if pygame.mixer.Channel(robot.walkChannel).get_busy():
            pygame.mixer.Channel(robot.walkChannel).play(robot.walkSound)
    else:
        pygame.mixer.Channel(robot.walkChannel).stop()


# Refreshes the players.
def Refresh_Bot(Robot, OtherBot, Punch):
    Robot.control()
    Robot.position = Move(Robot.vector, Robot.position)
    RobotWalkSound(Robot)
    Robot.Update_Arms()
    Robot = combat(Robot, Punch)
    Robot.Draw()
    Robot = ManageCollision(Robot, OtherBot)
    Robot = CM.update_physics(Robot, OtherBot)
    if Robot.jump:
        Robot.Jump()
    Robot = keep_in_level(Robot)
    return Robot


# Gets events
def getEvents():
    for event in pygame.event.get():
        global H
        global W
        global A
        global S
        global D
        global Left
        global Right
        global Up
        global R
        global Down
        global Z
        global X
        global RShift
        global r_control
        if event.type == QUIT:
            pygame.quit()
        if event.type == KEYDOWN:
            if event.key == K_h:
                H = True
            if event.key == K_r:
                R = True
            if event.key == K_w:
                W = True
            if event.key == K_a:
                A = True
            if event.key == K_s:
                S = True
            if event.key == K_d:
                D = True
            if event.key == K_UP:
                Up = True
            if event.key == K_DOWN:
                Down = True
            if event.key == K_LEFT:
                Left = True
            if event.key == K_RIGHT:
                Right = True
            if event.key == K_z:
                Z = True
            if event.key == K_x:
                X = True
            if event.key == K_RSHIFT:
                RShift = True
            if event.key == K_RCTRL:
                r_control = True
        if event.type == KEYUP:
            if event.key == K_h:
                H = False
            if event.key == K_r:
                R = False
            if event.key == K_w:
                W = False
            if event.key == K_a:
                A = False
            if event.key == K_s:
                S = False
            if event.key == K_d:
                D = False
            if event.key == K_UP:
                Up = False
            if event.key == K_DOWN:
                Down = False
            if event.key == K_LEFT:
                Left = False
            if event.key == K_RIGHT:
                Right = False
            if event.key == K_z:
                Z = False
            if event.key == K_x:
                X = False
            if event.key == K_RSHIFT:
                RShift = False
            if event.key == K_RCTRL:
                r_control = False


class GameThread:
    def __init__(self, KO, kop, back):
        self.threadClock = pygame.time.Clock()
        self.bg = Sprite_Object(back)
        self.ko = Sprite_Object(KO)
        self.KOP = kop

    def MainGameThreadBegin(self):
        Window.blit(self.bg.sprite, (0, 0))
        getEvents()

    def MainGameThreadEnd(self):
        global GAME_FRAME_RATE
        self.threadClock.tick(GAME_FRAME_RATE)
        pygame.display.update()

    def getKO(self):
        return self.ko

    def setKO(self, value):
        self.ko = value

    def getKOP(self):
        return self.KOP

    def setKOP(self, value):
        self.KOP = value

    koP = property(getKOP, setKOP)
    kO = property(getKO, setKO, doc="Knock out sprite.")


class Exploader:
    def __init__(self, x, y):
        self.booms = []
        self.all_coords = []
        self.X = x
        self.Y = y
        self.random = 0
        self.size = 0
        self.currentChannel = 1
        self.currentExplosion = 0

    def Randomize_R(self):
        self.random = random.randint(0, 100)

    def Create(self):
        global boom
        if 10 <= self.random <= 15:
            if self.size >= 10:
                i = 9
                while i >= 0:
                    del self.booms[i]

                    del self.all_coords[i]
                    i -= 1
                self.size = 0
            self.size += 1
            self.booms.append(Sprite_Object("Explosion.png"))
            self.all_coords.append(XY())
            self.all_coords[self.size - 1].x = random.uniform(self.X, self.X + 32)
            self.all_coords[self.size - 1].y = random.uniform(self.Y, self.Y + 128)
            if self.currentExplosion % 3 == 0:
                if self.currentChannel >= 8:
                    currentChannel = 1
                pygame.mixer.Channel(self.currentChannel).play(boom)
            self.currentExplosion += 1

    def Refresh(self):
        self.Randomize_R()
        self.Create()
        i = 0
        while i < self.size:
            Window.blit(self.booms[i].sprite, (self.all_coords[i].x, self.all_coords[i].y))
            i += 1

    def setX(self, value):
        self.X = value

    def setY(self, value):
        self.Y = value


# AI behavor base class.
class Behavor:
    def __init__(self):
        self._position = XY()
        self._behavorDeterminBox = BoundingBox()
        self._punchBox = BoundingBox()
        self._foward = False
        self._back = True
        self._otherFront = True
        self._otherBack = False
        self._otherFace = True
        self._bbbCollided = False
        self._pbbCollided = False
        self._vector = Vector()
        self._targate = Player1("Blue Bot/Robot_StandF.jpg", "Blue Bot/Robot_StandB.jpg", "Blue Bot/Robot_ArmF.png",
                                "Blue Bot/Robot_ArmB.png", "Blue Bot/Robot_JumpingF.jpg", "Blue Bot/Robot_JumpingB.jpg")
        self._otherJumping = False
        self._speed = .01
        self._combat = False
        self._jump = False
        self._jt = 0

    def UpdateParams(self, AI, Other):
        self._position = AI.position
        self._foward = AI.foward
        self._back = AI.back
        self._targate = Other
        self._behavorDeterminBox.x_offset = 200
        self._behavorDeterminBox.y_offset = 200
        self._punchBox.x_offset = 10
        self._punchBox.y_offset = 70
        self._behavorDeterminBox.position.x = self._position.x
        self._behavorDeterminBox.position.y = self._position.y
        self._punchBox.position.x = self._position.x
        self._punchBox.position.y = self._position.y

    def IsFacing(self, Other):
        if Other.foward == self._foward or Other.back == self._back:
            self._otherFace = False
        else:
            self._otherFace = True

    def Which_Side(self, Other):
        if Other.position.x > self._position.x:
            self._otherFront = False
            self._otherBack = True
        else:
            self._otherFront = True
            self._otherBack = False
        if Other.position.y < self._position.y - 5:
            self._otherJumping = True
        else:
            self._otherJumping = False

    def Manage_Collision(self, boundingBox):
        self._bbbCollided = CM.check_collision(self._behavorDeterminBox, boundingBox)
        self._pbbCollided = CM.check_collision(self._punchBox, boundingBox)
        if self._bbbCollided and self._pbbCollided:
            self._bbbCollided = False

    def FowardAlt(self):
        pass

    def BackAlt(self):
        pass

    def FowardDecision(self):
        pass

    def BackDecision(self):
        pass

    def Default(self):
        pass

    def DefaultAll(self):
        pass

    def Decision(self):
        self.IsFacing(self._targate)
        self.Which_Side(self._targate)
        self.Manage_Collision(self._targate.box)
        if self._bbbCollided:
            if self._otherFront:
                self.FowardDecision()
            else:
                self.BackDecision()
        if self._pbbCollided:
            if self._otherFront:
                self.FowardAlt()
            else:
                self.BackAlt()
        else:
            self.Default()
        self.DefaultAll()

    def Refresh(self):
        pass

    def Notify(self, AI):
        AI.position = self._position
        AI.SetFowardRaw(self._foward)
        AI.SetBackwardRaw(self._back)
        AI.vector = self._vector
        AI.jump = self._jump
        AI.Jump()
        AI = combat(AI, self._combat)
        return AI


class Agressive(Behavor):
    def Default(self):
        t = Vector()
        t.setBegin(self._position.x, self._position.y)
        self._combat = False
        if self._otherFront:
            t.setDestination(self._position.x + self._speed, self._position.y)
            self._back = False
            self._foward = True
        else:
            t.setDestination(self._position.x - self._speed, self._position.y)
            self._back = True
            self._foward = False
        t = calculate_vector(t, self._position)
        self._vector.x = t.x
        self._position = Move(self._vector, self._position)

    def FowardAlt(self):
        self._vector.x = 0
        self._vector.y = 0
        self._back = False
        self._foward = True
        self._combat = True

    def BackAlt(self):
        self._vector.x = 0
        self._vector.y = 0
        self._back = True
        self._foward = False
        self._combat = True

    def FowardDecision(self):
        self._vector.setBegin(self._position.x, self._position.y)
        self._vector.setDestination(self._position.x + .05, self._position.y)
        self._back = False
        self._foward = True
        self._combat = False
        self._vector = calculate_vector(self._vector, self._position)
        self._position = Move(self._vector, self._position)

    def BackDecision(self):
        self._vector.setBegin(self._position.x, self._position.y)
        self._vector.setDestination(self._position.x - .05, self._position.y)
        self._back = True
        self._foward = False
        self._combat = False
        self._vector = calculate_vector(self._vector, self._position)
        self._position = Move(self._vector, self._position)

    def DefaultAll(self):
        if self._otherJumping:
            if self._jt >= 25:
                self._jump = True
            else:
                self._jt += 1
        else:
            self._jt -= 1
            self._jump = False
            if self._position.y <= 270:
                self._position.y += 3


class Passive(Behavor):
    def Default(self):
        t = Vector()
        t.setBegin(self._position.x, self._position.y)
        self._combat = True
        # print( "DEFAULT" )
        if self._otherFront:
            t.setDestination(self._position.x, self._position.y)
            self._back = False
            self._foward = True
            if self._otherJumping and self._position.y >= 270 and not (
                    self._position.x < 64 or self._position.x > 536):
                t.setDestination(self._position.x - self._speed, self._position.y)
                self._back = True
                self._foward = False
            elif not self._bbbCollided and not self._pbbCollided:
                t.setDestination(self._position.x + self._speed, self._position.y)
        else:
            t.setDestination(self._position.x, self._position.y)
            self._back = True
            self._foward = False
            if self._otherJumping and self._position.y >= 270 and not (
                    self._position.x < 64 or self._position.x > 536):
                t.setDestination(self._position.x + self._speed, self._position.y)
                self._back = False
                self._foward = True
            elif not self._bbbCollided and not self._pbbCollided:
                t.setDestination(self._position.x - self._speed, self._position.y)
        t = calculate_vector(t, self._position)
        self._vector.x = t.x
        self._position = Move(self._vector, self._position)

    def FowardAlt(self):
        self._vector.x = 0
        self._vector.y = 0
        self._back = False
        self._foward = True
        self._combat = True

    def BackAlt(self):
        self._vector.x = 0
        self._vector.y = 0
        self._back = True
        self._foward = False
        self._combat = True

    def FowardDecision(self):
        self._combat = True

    def BackDecision(self):
        self._combat = True

    def DefaultAll(self):
        if self._otherJumping:  # and self._pbbCollided == True:
            if self._jt >= 25:
                self._jump = True
            else:
                self._jt += 1
        else:
            self._jt -= 1
            self._jump = False
            if self._position.y <= 270:
                self._position.y += 3


class ArtificalIntelegence(RobotBase):
    def BehavorDecide(self):
        if self._Health < 50:
            return "pass"
        else:
            return "agress"


# Makes it so there is no long constructor for a robot.
class RobotFactory:
    def __init__(self, F, B, AF, AB, JF, JB):
        self._sds = [F, B, AF, AB, JF, JB]

    def GetSpriteDirectories(self):
        return self._sds

    def CreatePlayer1(self):
        player1 = Player1(self._sds[0], self._sds[1], self._sds[2], self._sds[3], self._sds[4], self._sds[5])
        player1.set_bot_position(100, 270)
        player1.ArmCalc()
        player1.box.x_offset = 32
        player1.box.y_offset = 30
        return player1

    def CreatePlayer2(self):
        player2 = Player2(self._sds[0], self._sds[1], self._sds[2], self._sds[3], self._sds[4], self._sds[5])
        player2.set_bot_position(100, 270)
        player2.ArmCalc()
        player2.box.x_offset = 32
        player2.box.y_offset = 30
        return player2

    def CreateAI(self):
        AI = ArtificalIntelegence(self._sds[0], self._sds[1], self._sds[2], self._sds[3], self._sds[4], self._sds[5])
        AI.set_bot_position(300, 273)
        AI.ArmCalc()
        AI.box.x_offset = 8
        AI.box.y_offset = 20
        return AI

    spriteDirectories = property(GetSpriteDirectories, doc="All the sprite directories.")


class AIControler:
    def __init__(self, AI, targate):
        self._targate = targate
        self._ai = AI
        self._current = "agress"
        self._availibleBehaviors = ["agress", Agressive(), "pass", Passive()]
        self._ag = self._availibleBehaviors[1]

    def UpdateParamiters(self, AI, targate):
        self._targate = targate
        self._ai = AI

    def Refresh(self):
        ManageCollision(self._ai, self._targate)
        self._ai = CM.update_physics(self._ai, self._targate)
        dec = self._ai.BehavorDecide()
        if dec != self._current:
            i = 0
            while i < len(self._availibleBehaviors):
                if self._availibleBehaviors[i] == dec:
                    self._ag = self._availibleBehaviors[i + 1]
                    self._current = self._availibleBehaviors[i]
                    break
                i += 2
        self._ag.UpdateParams(self._ai, self._targate)
        self._ag.Decision()
        self._ai = self._ag.Notify(self._ai)
        self._ai = keep_in_level(self._ai)
        #####################
        self._ai.Draw()
        self._ai.Update_Arms()
        RobotWalkSound(self._ai)
        return self._ai


def Wait():
    w = 0
    while w < 10000:
        w += 1


# More will be implemented.
class GamePackage:
    def __init__(self, levelDir, ko_object):
        self._thread = GameThread(ko_object, XY(), levelDir + "/Back.png")
        self._foreground = Sprite_Object(levelDir + "/Foreground.png")
        self._cloudDir = levelDir + "/Cloud.png"
        self._thread.koP.x = 200
        self._thread.koP.y = 400
        self._clouds = self.InitClouds()
        self._frontClouds = self.InitClouds()
        self._cloudVects = self.InitVectors()
        self._fowardCloudVects = self.InitVectors()
        self._foregroundPos = XY()
        self._foregroundPos.x = -25
        self._foregroundPos.y = 330
        self._cloudPoses = self.InitVectors()
        self._fowardCloudPoses = self.InitVectors()

    def InitClouds(self):
        t = Sprite_Object(self._cloudDir)
        clouds = [t]
        del clouds[0]
        return clouds

    def InitVectors(self):
        t = XY()
        vects = [t]
        del vects[0]
        return vects

    def RandomCloudGenirator(self):
        R = random.randrange(0, 5000)
        if 200 <= R < 201:
            t = Sprite_Object(self._cloudDir)
            self._clouds.append(t)
            t2 = XY()
            t2.x = 0
            t2.y = random.randrange(30, 160)
            t3 = Vector()
            t3.setBegin(0, t2.y)
            t3.setDestination(-.003, t2.y)
            t3.y = t2.y
            t3 = calculate_vector(t3, t2)
            self._cloudVects.append(t3)
            self._cloudPoses.append(t2)
        if 100 <= R < 101:
            t = Sprite_Object(self._cloudDir)
            self._frontClouds.append(t)
            t2 = XY()
            t2.x = 0
            t2.y = random.randrange(0, 150)
            t3 = Vector()
            t3.setBegin(0, t2.y)
            t3.setDestination(-.003, t2.y)
            t3.y = t2.y
            t3 = calculate_vector(t3, t2)
            self._fowardCloudVects.append(t3)
            self._fowardCloudPoses.append(t2)

    def getThread(self):
        return self._thread

    def BeginThread(self):
        self._thread.MainGameThreadBegin()
        iret = 0
        for i in self._frontClouds:
            self._fowardCloudPoses[iret] = Move(self._fowardCloudVects[iret], self._fowardCloudPoses[iret])
            Window.blit(i.sprite, (self._fowardCloudPoses[iret].x, self._fowardCloudPoses[iret].y))
            iret += 1

    def EndThread(self):
        self.RandomCloudGenirator()
        iret = 0
        for i in self._clouds:
            self._cloudPoses[iret] = Move(self._cloudVects[iret], self._cloudPoses[iret])
            Window.blit(i.sprite, (self._cloudPoses[iret].x, self._cloudPoses[iret].y))
            iret += 1
        Window.blit(self._foreground.sprite, (self._foregroundPos.x, self._foregroundPos.y))
        self._thread.MainGameThreadEnd()

    def setKOposition(self):
        if self._thread.koP.y > 80:
            self._thread.koP.y -= 1

    def GetForground(self):
        return self, self._foreground

    def SetForeground(self, value):
        self._foreground = value

    def GetForegroundPosition(self):
        return self._foregroundPos

    def SetForegroundPosition(self, value):
        self._foregroundPos = value

    thread = property(getThread, doc="Main game thread.")
    foreground = property(GetForground, SetForeground, doc="Foreground makes it look good.")
    foregroundPos = property(GetForegroundPosition, SetForegroundPosition, doc="The position of the foreground.")


# Base class for a level, so its not so messy.
class Level:
    def __init__(self, Package, Obj1, Obj2, AI):
        self._playerHealth = Sprite_Object("Battary.png")
        self._robotHealth = Sprite_Object("Battary.png")
        self._pHBars = [Sprite_Object("Bar.png"), Sprite_Object("Bar.png"), Sprite_Object("Bar.png"),
                        Sprite_Object("Bar.png"), Sprite_Object("Bar.png"), Sprite_Object("Bar.png"),
                        Sprite_Object("Bar.png"), Sprite_Object("Bar.png"), Sprite_Object("Bar.png"),
                        Sprite_Object("Bar.png")]
        self._rHBars = self._pHBars
        self._player = Obj1
        self._robot = Obj2
        self._package = Package
        self._exploader = Exploader(100.1, 100.1)
        self._gameOver = False
        self._end = False
        self.sound = 0
        if AI:
            self._controller = AIControler(Obj2, Obj1)
        self.Initilize()

    def Draw(self):
        pass

    def EndGame(self):
        global walkChannels
        self._player.Draw()
        self._robot.Draw()
        if self._player.health <= 0:
            self._exploader.setX(self._player.position.x)
            self._exploader.setY(self._player.position.y)
        if self._robot.health <= 0:
            self._exploader.setX(self._robot.position.x)
            self._exploader.setY(self._robot.position.y)
        self._exploader.Refresh()
        self._package.setKOposition()
        Window.blit(self._package.thread.kO.sprite, (self._package.thread.koP.x, self._package.thread.koP.y))
        if W:
            self._gameOver = False
            self._robot.health = 100
            self._player.health = 100
            self.sound = 0
            self._package.thread.koP.y = 400
            self.Initilize()
        if R:
            self._end = True
            walkChannels = 3

    def DrawHealth(self):
        inc = 0
        i = 0
        Window.blit(self._playerHealth.sprite, (0, 0))
        Window.blit(self._robotHealth.sprite, (500, 0))
        while inc < 101:
            if self._player.health > inc:
                Window.blit(self._pHBars[i].sprite, (inc, 2))
            inc += 10
            i += 1
        inc = 0
        i = 0
        while inc < 101:
            if self._robot.health > inc:
                Window.blit(self._rHBars[i].sprite, (500 + inc, 2))
            inc += 10
            i += 1

    def RunLevel(self):
        pass

    def Initilize(self):
        self.sound = 0

    def CleanUp(self):
        del self._player
        del self._robot
        del self._package
        del self._gameOver
        del self._exploader

    def ForegroundUpdate(self):
        if self._player.position.x < 300 and self._package.foregroundPos.x > -56:
            self._package.foregroundPos.x -= .25
        if self._player.position.x > 300 and self._package.foregroundPos.x < 3:
            self._package.foregroundPos.x += .25
        if self._player.position.y < 270 and self._package.foregroundPos.y < 350:
            self._package.foregroundPos.y += .25
        elif self._package.foregroundPos.y > 330:
            self._package.foregroundPos.y -= .25

    def Logic(self):
        global boxingBellSound
        global KOSound
        if self._gameOver and self._package.thread.koP.y < 80:
            pass
        else:
            getEvents()
        self._package.BeginThread()
        self.DrawHealth()
        if self._gameOver:
            self.RunLevel()
        else:
            if pygame.mixer.Channel(0).get_busy():
                if self.sound == 0:
                    pygame.mixer.Channel(0).play(boxingBellSound, loops=0, maxtime=1700)
                    self.sound += 1
                elif self.sound == 1:
                    pygame.mixer.Channel(0).play(KOSound, loops=0)
                    self.sound += 1
            self.EndGame()
        self.Draw()
        self.ForegroundUpdate()
        self._package.EndThread()

    def getKO(self):
        return self._package.kO

    def Notify(self):
        return self._end

    KO = property(getKO)


class TwoPlayerLevel(Level):
    def Initilize(self):
        self._player.set_bot_position(100, 270)
        self._player.ArmCalc()
        self._player.box.x_offset = 12  # 32
        self._player.box.y_offset = 30
        self._robot.set_bot_position(200, 270)
        self._robot.ArmCalc()
        self._robot.box.x_offset = 12
        self._robot.box.y_offset = 30  # 20

    def RunLevel(self):
        self._player = Refresh_Bot(self._player, self._robot, Z)
        self._robot = Refresh_Bot(self._robot, self._player, RShift)
        self._robot.Update_Arms()
        self._player.Update_Arms()
        if self._robot.health <= 0 or self._player.health <= 0:
            self._gameOver = True

    def Draw(self):
        self._package.EndThread()


class OnePlayerLevel(Level):
    def Initilize(self):
        self._player.set_bot_position(100, 270)
        self._player.ArmCalc()
        self._player.box.x_offset = 32
        self._player.box.y_offset = 30
        self._robot.set_bot_position(200, 270)
        self._robot.ArmCalc()
        self._robot.box.x_offset = 8
        self._robot.box.y_offset = 20

    def RunLevel(self):
        self._player = Refresh_Bot(self._player, self._robot, Z)
        self._controller.UpdateParamiters(self._robot, self._player)
        self._robot = self._controller.Refresh()
        self._player.Update_Arms()
        self._robot.Update_Arms()
        if self._robot.health <= 0 or self._player.health <= 0:
            self._gameOver = True

    def Draw(self):
        self._package.EndThread()


class ButtonAction:
    def __init__(self):
        self.Initilize()

    def Implement(self):
        pass

    def Initilize(self):
        pass


class Button:
    def __init__(self, Highlighted, NotSelected, x, y):
        self._selected = False
        self._activate = False
        self._highlighted = Sprite_Object(Highlighted)
        self._notSelected = Sprite_Object(NotSelected)
        self._position = XY()
        self._position.x = x
        self._position.y = y
        self._action = ButtonAction()
        self._action.Initilize()

    def Animate(self):
        if self._selected:
            Window.blit(self._highlighted.sprite, (self._position.x, self._position.y))
        else:
            Window.blit(self._notSelected.sprite, (self._position.x, self._position.y))

    def Run(self):
        if self._activate:
            return self._action.Implement()
        else:
            return -1

    def GetSelected(self):
        return self._selected

    def SetSelected(self, value):
        self._selected = value

    def GetActivate(self):
        return self._activate

    def SetActivate(self, value):
        self._activate = value

    def sprite(self):
        if self._selected:
            return self._highlighted
        else:
            return self._notSelected

    def GetAction(self):
        return self._action

    def SetAction(self, value):
        self._action = value

    selected = property(GetSelected, SetSelected, doc="Is the cursor hovering over this option?")
    activate = property(GetActivate, SetActivate, doc="Did we press the button?")
    action = property(GetAction, SetAction)


class BotChoice(ButtonAction):
    def __init__(self, bot):
        super().__init__()
        self._bot = bot

    def Implement(self):
        return self._bot


class GameType(ButtonAction):
    def __init__(self, value):
        super().__init__()
        self._gt = value

    def Implement(self):
        return self._gt


class Menu:
    def __init__(self, numberOfButtons, Button_Images, x, startingY, Cursor, increment, ButtonAlts, optionSound,
                 selectSound):
        self._middle = len(Button_Images) / 2
        self._buttons = self.InitButtons()
        self._currentButton = numberOfButtons - 1
        self._cursor = Sprite_Object(Cursor)
        self._cursorPosition = XY()
        self._cursorPosition.x = x - 64
        self._cursorPosition.y = startingY - 64
        self._buttonOffset = increment
        self._startY = startingY
        self._x = x
        self._lastY = 0.0
        self._lastPosition = self._cursorPosition.y
        self._optionSound = optionSound
        self._selectSound = selectSound
        i = 0
        self._itemCoords = self.InitCoords()
        while i < numberOfButtons:
            self._buttons.append(Button(Button_Images[i], ButtonAlts[i], x, startingY))
            temp = XY()
            temp.x = self._x
            temp.y = startingY
            self._itemCoords.append(temp)
            startingY += increment
            i += 1
        self._lastY = startingY - increment

    def InitButtons(self):
        t = Button("Default.jpg", "Default.jpg", 0, 0)
        temp = [t]
        del temp[0]
        return temp

    def InitCoords(self):
        t = XY()
        temp = [t]
        del temp[0]
        return temp

    def GetButtons(self):
        return self._buttons

    def SetButtons(self, value):
        self._buttons = value

    def Select(self):
        t = 0
        self._buttons[self._currentButton].selected = False
        if Down:
            pygame.mixer.Channel(0).play(self._optionSound)
            self._currentButton -= 1
            if self._currentButton < 0:
                self._currentButton = len(self._buttons) - 1
        if Up:
            self._optionSound.play()
            self._currentButton += 1
            if self._currentButton > len(self._buttons) - 1:
                self._currentButton = 0
        self._cursorPosition.y = self._itemCoords[self._currentButton].y + 64
        if Right:
            self._selectSound.play()
            self._buttons[self._currentButton].activate = True
        while t < 50:
            Wait()
            t += 1
        self._buttons[self._currentButton].selected = True

    def Draw(self):
        temp = self._startY
        for i in self._buttons:
            temp += self._buttonOffset
            t = i.sprite()
            Window.blit(t.sprite, (self._x, temp))
        Window.blit(self._cursor.sprite, (self._cursorPosition.x, self._cursorPosition.y))

    buttons = property(GetButtons, SetButtons)


def PygameUpdate(time):
    global clock
    clock.tick(time)
    pygame.display.update()


def main():
    global clock
    global MENU_TIME
    global MENU_SELECT_DELAY
    os.system("COLOR 9")
    print("Giant Robot Super Battles: \n\n \t Created by Christopher Greeley: \n\n\t" +
          "Programed With:\n\n\t Python Version 3.22, and Pygame Version 1.92.")

    levels = [GamePackage("City", "KO.png"), GamePackage("Radioactive", "KO.png"), GamePackage("Moutain", "KO.png")]
    level_choices = ["CityC.png", "RadC.png", "MountC.png"]
    level_choice_alts = ["AltC.png", "AltR.png", "AltM.png"]
    blue_bot = RobotFactory("Blue Bot/Robot_StandF.jpg", "Blue Bot/Robot_StandB.jpg", "Blue Bot/Robot_ArmF.png",
                            "Blue Bot/Robot_ArmB.png", "Blue Bot/Robot_JumpingF.jpg", "Blue Bot/Robot_JumpingB.jpg")
    red_bot = RobotFactory("Red Bot/Robot_StandF.png", "Red Bot/Robot_StandB.png", "Red Bot/Robot_ArmF.png",
                           "Red Bot/Robot_ArmB.png", "Red Bot/Robot_JumpingF.png", "Red Bot/Robot_JumpingB.png")
    yellow_bot = RobotFactory("Yellow Bot/Robot_StandF.png", "Yellow Bot/Robot_StandB.png",
                              "Yellow Bot/Robot_ArmF.png", "Yellow Bot/Robot_ArmB.png",
                              "Yellow Bot/Robot_JumpingF.png", "Yellow Bot/Robot_JumpingB.png")
    green_bot = RobotFactory("Green Bot/Robot_StandF.png", "Green Bot/Robot_StandB.png", "Green Bot/Robot_ArmF.png",
                             "Green Bot/Robot_ArmB.png", "Green Bot/Robot_JumpingF.png",
                             "Green Bot/Robot_JumpingB.png")
    bots = [blue_bot, red_bot, yellow_bot, green_bot]
    choices = ["Blue Bot Icon.png", "Red Bot Icon.png", "Green Bot Icon.png", "Yellow Bot Icon.png"]
    alts = ["Default.png", "Default.png", "Default.png", "Default.png"]
    menu = Menu(4, choices, 300.0, 60.0, "Cursor.png", 64.0, alts, pygame.mixer.Sound("Sounds/Menu/Option2.wav"),
                pygame.mixer.Sound("Sounds/Menu/Select.wav"))
    gt = ["1Player.png", "2Player.png", "Online.png"]
    gtalts = ["1Palt.png", "2Palt.png", "OnlineAlt.png"]
    # 230.0
    start_menu = Menu(3, gt, 240, 166.0, "Cursor.png", 64.0, gtalts, pygame.mixer.Sound("Sounds/Menu/Option.wav"),
                      pygame.mixer.Sound("Sounds/Menu/Select.wav"))
    start_menu.buttons[0].action = GameType(0)
    start_menu.buttons[1].action = GameType(1)
    menu.buttons[0].action = BotChoice(0)
    menu.buttons[1].action = BotChoice(1)
    menu.buttons[2].action = BotChoice(3)
    menu.buttons[3].action = BotChoice(2)
    level_menu = Menu(3, level_choices, 300.0, 60.0, "Cursor.png", 80.0, level_choice_alts,
                      pygame.mixer.Sound("Sounds/Menu/Option.wav"), pygame.mixer.Sound("Sounds/Menu/Select.wav"))
    level_menu.buttons[0].action = BotChoice(0)
    level_menu.buttons[1].action = BotChoice(1)
    level_menu.buttons[2].action = BotChoice(2)
    gui_back = Sprite_Object("GuiScreen.png")
    choose_bot = Sprite_Object("Choose Your Robot.png")
    choose_stage = Sprite_Object("Choose Stage.png")
    help_file = Sprite_Object("Press H For Help.png")
    start_screen = True
    in_game = False
    p1 = -1
    p2 = -1
    game_type = -1
    which_level = -1
    pygame.display.set_caption("Giant Robot Super Battles")
    while True:
        while start_screen:
            Window.blit(gui_back.sprite, (0, 0))
            Window.blit(help_file.sprite, (60, 360))
            getEvents()
            start_menu.Select()
            start_menu.Draw()
            for i in start_menu.buttons:
                if i.Run() != -1:
                    game_type = i.Run()
                    i.activate = False
                    start_screen = False
                    clock.tick(MENU_SELECT_DELAY)
                    break
            if H:
                os.system("ReadMe.txt")
                os.system("EXIT")
            PygameUpdate(MENU_TIME)
        while which_level == -1:
            Window.blit(gui_back.sprite, (0, 0))
            Window.blit(choose_stage.sprite, (200, 40))
            getEvents()
            level_menu.Select()
            level_menu.Draw()
            for i in level_menu.buttons:
                if i.Run() != -1:
                    which_level = i.Run()
                    clock.tick(MENU_SELECT_DELAY)
                    i.activate = False
                    break
            PygameUpdate(MENU_TIME)
        while not in_game and not start_screen:
            if game_type == 1:
                Window.blit(gui_back.sprite, (0, 0))
                Window.blit(choose_bot.sprite, (200, 40))
                getEvents()
                menu.Select()
                menu.Draw()
                if p1 == -1:
                    Window.blit(Sprite_Object(gt[0]).sprite, (200, 20))
                    for i in menu.buttons:
                        if i.Run() != -1:
                            p1 = i.Run()
                            i.activate = False
                            clock.tick(MENU_SELECT_DELAY)
                            break
                if p2 == -1 and p1 != -1:
                    Window.blit(Sprite_Object(gt[1]).sprite, (200, 20))
                    for i in menu.buttons:
                        if i.Run() != -1:
                            p2 = i.Run()
                            i.activate = False
                            in_game = True
                            clock.tick(MENU_SELECT_DELAY)
                            break
            else:
                while p1 == -1:
                    Window.blit(gui_back.sprite, (0, 0))
                    Window.blit(choose_bot.sprite, (200, 40))
                    getEvents()
                    menu.Select()
                    menu.Draw()
                    for i in menu.buttons:
                        if i.Run() != -1:
                            p1 = i.Run()
                            i.activate = False
                            in_game = True
                            break
                    PygameUpdate(MENU_TIME)
            PygameUpdate(MENU_TIME)
        while in_game:
            if game_type == 0:
                level = OnePlayerLevel(levels[which_level], bots[p1].CreatePlayer1(), bots[0].CreateAI(), True)
                while not level.Notify():
                    level.Logic()
                in_game = False
                p1 = -1
                p2 = -1
                start_screen = True
                game_type = -1
                which_level = -1
            else:
                level = TwoPlayerLevel(levels[which_level], bots[p1].CreatePlayer1(), bots[p2].CreatePlayer2(), False)
                while not level.Notify():
                    level.Logic()
                in_game = False
                p1 = -1
                start_screen = True
                game_type = -1
                which_level = -1


if __name__ == "__main__":
    main()
