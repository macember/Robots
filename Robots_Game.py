import pygame, sys
from pygame.locals import *

visualMode = True
quadrantShiftTime = 100
foodClusterGenerationTime = 100

###Map class definition
class gameMap:
    #constructor
    def __init__(self):
        matrix = [[0 for x in range(40)] for x in range(40)] #create two dimensional array
        for x in range(0,40):
            for y in range(0,40):
                color = 0
                if x < 10 or x >= 30:
                    color = 0
                elif y < 10 or y >= 30:
                    color = 0
                else:
                    color = 1
                matrix[x][y] = color
        self.Matrix = matrix
        self.locationsToUpdate = []
        self.playerPos = [10,10]
        self.deathQuadrant = 0 #a number between 0 and 4, starting at bottom left, moving clockwise
        
        #defining quadrant bounds
        self.quadrantBounds = []
        self.quadrantBounds.append( [[20,30],[20,30]] ) ###quadrant 0 bounds
        self.quadrantBounds.append( [[10,20],[20,30]] ) ###quadrant 1 bounds
        self.quadrantBounds.append( [[10,20],[10,20]] )
        self.quadrantBounds.append( [[20,30],[10,20]] )

    def shiftQuadrant(self):
        #increment quadrant count
        oldQuadrant = self.deathQuadrant
        self.deathQuadrant = (self.deathQuadrant+1)%4
        newQuadrant = self.deathQuadrant
        #map goes from x=10 to x=29 and y = 10 to y=29
        #quadrantBounds array is QuadrantBounds[quadrantNumber][x or y bound][lower/upper]
        self.fillQuadrant(newQuadrant, 0)
        self.fillQuadrant(oldQuadrant, 1)

    def moveAgent(self, keyname):
        self.locationsToUpdate.append([board.playerPos[0], board.playerPos[1]])
        if keyname == "up":
            self.playerPos[1]-=1
        elif keyname == "down":
            self.playerPos[1]+=1
        elif keyname == "left":
            self.playerPos[0]-=1
        elif keyname == "right":
            self.playerPos[0]+=1
        if self.Matrix[self.playerPos[0]][self.playerPos[1]] == 0: #if agent is in blue square after moving
            print("You just died")
        return

    def fillQuadrant(self,index, val):
        for x in range(self.quadrantBounds[index][0][0], self.quadrantBounds[index][0][1]):
            for y in range(self.quadrantBounds[index][1][0], self.quadrantBounds[index][1][1]):
                self.locationsToUpdate.append([x,y])
                self.Matrix[x][y] = val #MAKE OLD QUADRANT GREY        
                    

##pygame initialization
pygame.init()
board = gameMap()
fpsClock = pygame.time.Clock()

if visualMode:
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



        

###populate board: fills the game board
def populateBoard(board, window):
    for x in range(0, 40):
        for y in range(0, 40):
            if [x,y]==board.playerPos:
                pygame.draw.circle(window, redColor, (x*20 + 10, y*20 + 10), 10)
            else:
                pygame.draw.polygon(window, mapColor(board.Matrix[x][y]), ( (x*20, y*20), ((x*20)+20, y*20),((x*20)+20, (y*20)+20), (x*20, (y*20)+20)) )


if visualMode:
    windowSurfaceObj.fill(greyColor) #fills the window with grey
    populateBoard(board, windowSurfaceObj) # fills the initial map



#### MAIN GAME LOOP #####
while True:
    if visualMode:
        pygame.draw.circle(windowSurfaceObj, redColor, (board.playerPos[0]*20 + 10, board.playerPos[1]*20 + 10), 10)
        for l in board.locationsToUpdate:
            x = l[0]
            y = l[1]
            pygame.draw.polygon(windowSurfaceObj, mapColor(board.Matrix[x][y]), ( (x*20, y*20), ((x*20)+20, y*20),((x*20)+20, (y*20)+20), (x*20, (y*20)+20)) )
        board.locationsToUpdate = []
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
            board.moveAgent(keyname)

    if clock%quadrantShiftTime == 0:
        board.shiftQuadrant()

    pygame.display.update()
    clock+=1
    fpsClock.tick(30)
