import pygame, sys
from pygame.locals import *


###Map class definition
class gameMap:
    #constructor
    def __init__(self):
        Matrix = [[0 for x in range(40)] for x in range(40)] #create two dimensional array
        for x in range(0,40):
            for y in range(0,40):
                color = 0
                if x < 10 or x > 30:
                    color = 0
                elif y < 10 or y > 30:
                    color = 0
                else:
                    color = 1
                Matrix[x][y] = color
        self.matrix = Matrix
        matrix[10][10] = 2
        self.playerPos = [10,10]
        self.deathQuadrant = 0 #a number between 0 and 4, starting at bottom right, moving clockwise
        

##pygame initialization
pygame.init()
fpsClock = pygame.time.Clock()
windowSurfaceObj = pygame.display.set_mode((800,800))
pygame.display.set_caption('Monkey Robots')

###Global Variables
redColor = pygame.Color(255, 0, 0)
greenColor = pygame.Color(0,255,0)
blueColor = pygame.Color(0,0,255)
greyColor = pygame.Color(120, 120, 120)
blackColor = pygame.Color(0,0,0)
whiteColor = pygame.Color(255,255,255)
mousex, mousey = 0, 0
fontObj = pygame.font.Font('freesansbold.ttf', 32)
msg = 'Hello, World!'
clock = 0

def mapColor(col):
    if col==0:
        return blueColor
    elif col==1:
        return greyColor
    elif col==2:
        return redColor
    else:
        return blackColor


def moveAgent(keyname):
    if keyname == "up":
        PlayerPos[1]-=1
    elif keyname == "down":
        PlayerPos[1]+=1
    elif keyname == "left":
        PlayerPos[0]-=1
    elif keyname == "right":
        PlayerPos[0]+=1
    if Matrix[PlayerPos[0]][PlayerPos[1]] ==0:
        print("You just died")
    return
                    
###Create Quadrants in 


windowSurfaceObj.fill(greyColor)
while True:
 
    for x in range(0, 40):
        for y in range(0, 40):
            if [x,y]==PlayerPos:
                pygame.draw.circle(windowSurfaceObj, redColor, (x*20 + 10, y*20 + 10), 10)
            else:
                pygame.draw.polygon(windowSurfaceObj, mapColor(Matrix[x][y]), ( (x*20, y*20), ((x*20)+20, y*20),((x*20)+20, (y*20)+20), (x*20, (y*20)+20)) )
            
     ##Process Game Events
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == KEYDOWN:
            print('test', pygame.key.name(event.key))
            keyname = pygame.key.name(event.key)
            moveAgent(keyname)

    pygame.display.update()
    clock+=1
    fpsClock.tick(30)
