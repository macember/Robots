import pygame, sys, random
from pygame.locals import *

visualMode = True
quadrantShiftTime = 100
foodClusterGenerationTime = 100


###Game Variables
redColor = pygame.Color(255, 0, 0)
greenColor = pygame.Color(0,255,0)
blueColor = pygame.Color(0,0,255)
greyColor = pygame.Color(120, 120, 120)
blackColor = pygame.Color(0,0,0)
whiteColor = pygame.Color(255,255,255)
mousex, mousey = 0, 0

###Map class definition
class gameMap:
    #constructor
    def __init__(self, logging=True):
        random.seed() #on creation of map, seed random number generator
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
        self.logging = logging
        self.Matrix = matrix
        self.locationsToUpdate = [] #list of locations to update visually
        self.playerPos = [10,10] #position of agent
        self.quadrant = 2 #a number between 0 and 4, starting at bottom left, moving clockwise
        self.foodCount = 0 #count of the food eaten
        self.score = 0 #overall game score
        self.log = "" #keep a log of moves
        self.clock = 0
        #defining quadrant bounds
        self.quadrantBounds = []
        
        self.quadrantBounds.append( [[20,30],[20,30]] ) ###quadrant 0 bounds
        self.quadrantBounds.append( [[10,20],[20,30]] ) ###quadrant 1 bounds
        self.quadrantBounds.append( [[10,20],[10,20]] )
        self.quadrantBounds.append( [[20,30],[10,20]] )

    def shiftQuadrant(self, desiredQuadrant=-1):
        #increment quadrant count
        oldQuadrant = self.quadrant
        if(desiredQuadrant==-1):                
            self.quadrant = (self.quadrant+1)%4
            newQuadrant = self.quadrant
        else:
            self.quadrant = newQuadrant = desiredQuadrant

        print('on shiftQuadrant, old quadrant is ', oldQuadrant, " New quadrant is ", newQuadrant)
        #map goes from x=10 to x=29 and y = 10 to y=29
        #quadrantBounds array is QuadrantBounds[quadrantNumber][x or y bound][lower/upper]
        self.fillQuadrant(newQuadrant, 0)
        self.fillQuadrant(oldQuadrant, 1)
        if self.logging:
            self.log+=str(self.clock) + ":Q" + str(newQuadrant) + ";"
        if self.Matrix[self.playerPos[0]][self.playerPos[1]] == 0: #quadrant just shifted onto player
            self.death()
        
    def moveAgent(self, keyname):
        move = ""
        self.locationsToUpdate.append([self.playerPos[0], self.playerPos[1]])
        if keyname == "up" or keyname == 'w':
            self.playerPos[1]-=1
            move = "w"
        elif keyname == "down" or keyname == 's':
            self.playerPos[1]+=1
            move = "s"
        elif keyname == "left" or keyname == 'a':
            self.playerPos[0]-=1
            move="a"
        elif keyname == "right" or keyname == 'd':
            self.playerPos[0]+=1
            move="d"
            
        playerLocation = self.Matrix[self.playerPos[0]][self.playerPos[1]]
        if playerLocation == 0: #if agent is in blue square after moving
            self.death()
        elif playerLocation == 3: #just ate food
            self.foodCount+=1
            print("Food count is: ", self.foodCount)
            self.Matrix[self.playerPos[0]][self.playerPos[1]] = 1 #just ate food, reset square to grey
            self.locationsToUpdate.append([self.playerPos[0], self.playerPos[1]])
        #write move to log
        if self.logging:
            self.log+=str(self.clock)+":"+move+";"
            

    def fillQuadrant(self,index, val):
        for x in range(self.quadrantBounds[index][0][0], self.quadrantBounds[index][0][1]):
            for y in range(self.quadrantBounds[index][1][0], self.quadrantBounds[index][1][1]):
                self.locationsToUpdate.append([x,y])
                self.Matrix[x][y] = val #MAKE OLD QUADRANT GREY        

    def generateFood(self, x=-1, y=-1): #generates center for where food will be
        #first, replace old quadrant's food with grey
        oldQuadrant = (self.quadrant-2) % 4
        self.fillQuadrant(oldQuadrant,1)
        #random food will be generated in the following configuration in a quadrant:
        #     xxx 
        #     x*x
        #     xxx   Where * is a empty and x has food
        #to do so, we must randomly generate a * location within a quandrant.
        if x==-1 and y==-1:
            desiredQuadrant = (self.quadrant-1) % 4
            xLower = self.quadrantBounds[desiredQuadrant][0][0] + 1
            xUpper = self.quadrantBounds[desiredQuadrant][0][1] - 2
            #because upper bound is thirty but grid only goes up to 29, subtract 2
            yLower = self.quadrantBounds[desiredQuadrant][1][0] + 1
            yUpper = self.quadrantBounds[desiredQuadrant][1][1] - 2
            chosenX = random.randint(xLower,xUpper)
            chosenY = random.randint(yLower,yUpper)
            if self.logging:
                self.log+=str(self.clock)+":F"+str(chosenX)+","+str(chosenY)+";"
            self.generateFoodHelper(chosenX,chosenY)
        else:
            self.generateFoodHelper(x,y)

    def generateFoodHelper(self,x,y):
        print('GENERATING FOOD AT ', x, y)
        #Given center, generates pattern
        #inputs: x,y, coordinates of randomly chosen center point
        #this function generates food in a pattern around the center point
        for xnew in range(x-1, x+2): 
            for ynew in range(y-1,y+2):
                if xnew!=x or ynew!=y: #choose every location BUT (x,y)
                    self.Matrix[xnew][ynew] = 3
                    self.locationsToUpdate.append([xnew,ynew])

    def death(self):
        print("Player just died!")

    def cleanup(self): #method to call when game ends. Does cleanup
        self.log += "***"
        self.log+="TotalScore:" + str(self.score) + ";"
        self.log+="ClockTicks:" + str(self.clock) + ";"
        self.log+="FoodCount:" + str(self.foodCount)
        
def writeLogToFile(filename, toWrite):
    f = open(filename, 'w')
    f.write(toWrite)
    f.close()
    


def mapColor(col):
    if col==0:
        return blueColor
    elif col==1:
        return greyColor
    elif col==2:
        return redColor
    elif col==3:
        return greenColor
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


#### MAIN GAME LOOP #####
def simulateGame():        
    ##pygame initialization
    pygame.init()
    board = gameMap()
    fpsClock = pygame.time.Clock()

    if visualMode:
        windowSurfaceObj = pygame.display.set_mode((800,800))
        pygame.display.set_caption('Monkey Robots')
        windowSurfaceObj.fill(greyColor) #fills the window with grey
        populateBoard(board, windowSurfaceObj) # fills the initial map

    finished = False
    while not finished:
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
                #pygame.quit()
                #sys.exit()
                finished = True
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == KEYDOWN:
                print('moving', pygame.key.name(event.key))
                keyname = pygame.key.name(event.key)
                board.moveAgent(keyname)

        if board.clock%quadrantShiftTime == 0:
            board.shiftQuadrant()
            board.generateFood()

        pygame.display.update()
        board.clock+=1
        fpsClock.tick(10)

        
    print("Out of game")
    board.cleanup()
    writeLogToFile("output.txt", board.log)
    pygame.quit()

def logToDictionary(gameString):
    #first, split string by ***
    x = gameString.split('***')
    clockEvents = x[0]
    metadata = x[1]
    eachEvent = clockEvents.split(';') #each clock event
                                        #in the format time:event
                                       #events = wasd / Q[0-3] / F[position
    d = {} #create dictionary
    for e in eachEvent:
        print(e)
        #first, get the clock time
        logEntry = e.split(':')
        #print(logEntry)
        if len(logEntry)>1: #edge case- in case there is empty event
            time = int(logEntry[0])
            print('time: ', time)
            event = logEntry[1]
            print('event: ', event)
            if time in d: #we already have an entry for the time; add to it
                entry = d[time]
                entry+=";" + event
                d.update({time:entry})
            else: #we don't have an entry for the time
                d.update({time:event})
    #process metadata
    ClockTicks = int(metadata.split('ClockTicks:')[1].split(';')[0])
    d.update({"ClockTicks":ClockTicks})
    print('dictionary is: ', d)
    return d
                          

def simulateFromLog(logFile):
    f = open(logFile, 'r')
    gameString = f.read()
    f.close()
    gameEvents = logToDictionary(gameString) #a dictionary of clock time/game events
    totalClockTicks = gameEvents["ClockTicks"]
    if(totalClockTicks<=0):
        return
    
    ##pygame initialization
    pygame.init()
    board = gameMap()
    fpsClock = pygame.time.Clock()

    if visualMode:
        windowSurfaceObj = pygame.display.set_mode((800,800))
        pygame.display.set_caption('Monkey Robots')
        windowSurfaceObj.fill(greyColor) #fills the window with grey
        populateBoard(board, windowSurfaceObj) # fills the initial map

    ###Main game Loop
    while board.clock<=totalClockTicks:
        if visualMode:
            pygame.draw.circle(windowSurfaceObj, redColor, (board.playerPos[0]*20 + 10, board.playerPos[1]*20 + 10), 10)
            for l in board.locationsToUpdate:
                x = l[0]
                y = l[1]
                pygame.draw.polygon(windowSurfaceObj, mapColor(board.Matrix[x][y]), ( (x*20, y*20), ((x*20)+20, y*20),((x*20)+20, (y*20)+20), (x*20, (y*20)+20)) )
            board.locationsToUpdate = []

        ###event manager
        for event in pygame.event.get():
            if event.type==QUIT:
                #pygame.quit()
                #sys.exit()
                finished = True
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == KEYDOWN:
                print('keyboard press!')
            
        ##Process Game Events
        if board.clock in gameEvents: #if there is an event at this clock time
            e = gameEvents[board.clock] #get value in hashtable
            print('e is: ',e)
            events = e.split(';')
            for event in events:
                print('on event ', event)
                firstChar = event[0]
                if firstChar=='w' or firstChar=='a' or firstChar=='s' or firstChar=='d':
                    board.moveAgent(firstChar)
                elif firstChar=='F':
                    #new food is being generated, get its location
                    foodxy = event[1:].split(',')
                    board.generateFood(int(foodxy[0]),int(foodxy[1]))
                elif firstChar=='Q':
                    board.shiftQuadrant(int(event[1]))
                else:
                    print('ERROR PARSING REPLAY FILE! SHOULDNT REACH HERE!')                


        #for debugging
        #if(board.clock%2==0):
        #    board.moveAgent('up')
        #else:
        #    board.moveAgent('down')

        pygame.display.update()
        board.clock+=1
        fpsClock.tick(10)

        
    print("Out of game")
    board.cleanup()
    #writeLogToFile("output.txt", board.log)
    pygame.quit()    
    
