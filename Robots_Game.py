import pygame, sys, random
from NN import *
from pygame.locals import *

visualMode = False
nodeNames = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']    


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
    cannotDie = True
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
        self.Matrix = matrix

        #Matrix color scheme:
        # 1=land, 0=water, 3=food

        ###Switch variables                
        self.deathQuadrantOn = False #whether the game has a death quadrant
        self.logging = logging

        ###General variables
        self.quadrantShiftTime = 30
        self.locationsToUpdate = [] #list of locations to update visually
        for i in range(0,40):
            for j in range(0,40):
                self.locationsToUpdate.append([i,j])
        
        self.playerPos = [10,10] #position of agent
        self.foodPos = [-1, -1] #position of center of food cluster
        self.quadrant = 0 #a number between 0 and 4, starting at bottom left, moving clockwise
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
        
        ###Neural net variables
        
        self.moveBuffer = [0,0,0,0] #up, left, down, right
        self.timeSinceFood = 100
        NNInputNode = 1

    def timeUntilShift(self):
        return self.quadrantShiftTime - (self.clock % self.quadrantShiftTime)

    def shiftQuadrant(self, desiredQuadrant=-1): #DQ means if there IS a deathquadrant
        #increment quadrant count
        oldQuadrant = self.quadrant
        if(desiredQuadrant==-1):
            self.quadrant = (self.quadrant+1)%4
            newQuadrant = self.quadrant
        else:
            self.quadrant = newQuadrant = desiredQuadrant
        #map goes from x=10 to x=29 and y = 10 to y=29
        #quadrantBounds array is QuadrantBounds[quadrantNumber][x or y bound][lower/upper]
        if self.deathQuadrantOn:
            #if we have a death quadrant    
            self.fillQuadrant(newQuadrant, 0)
        self.fillQuadrant(oldQuadrant, 1)

        if self.logging:
            self.log+=str(self.clock) + ":Q" + str(newQuadrant) + ";"
        if self.Matrix[self.playerPos[0]][self.playerPos[1]] == 0: #quadrant just shifted onto player
            self.death()

    def moveBufferDecay(self, decayAmount=.25):  #decays move buffer by a fixed amount
        for i in range(0, len(self.moveBuffer)):
            self.moveBuffer[i] = max(0, self.moveBuffer[i]-decayAmount)

        
    def moveAgent(self, keyname):
        #print("Agent moved: ", keyname)
        ### local variables ###
        move = ""
        oldPos = list(self.playerPos)
        newPos = list(self.playerPos)
        ### append old playerPos to locationToUpdate ###
        self.locationsToUpdate.append([self.playerPos[0], self.playerPos[1]])

        #### SET THE MOVE, adjust move buffer###
        self.moveBufferDecay()
        if keyname == "up" or keyname == 'w':
            newPos[1]-=1
            move = "w"
            self.moveBuffer[0] = 1
        elif keyname == "left" or keyname == 'a':
            newPos[0]-=1
            move="a"
            self.moveBuffer[1] = 1            
        elif keyname == "down" or keyname == 's':
            newPos[1]+=1
            move = "s"
            self.moveBuffer[2] = 1
        elif keyname == "right" or keyname == 'd':
            newPos[0]+=1
            move="d"
            self.moveBuffer[3] = 1
        
        playerLocation = self.Matrix[newPos[0]][newPos[1]]
        ### Check if we cannot die; otherwise, update position ###
        if self.cannotDie and playerLocation==0: #we cannot die but we are moving into death
            pass #do nothing, DON'T update the playerPos
        else:
            self.playerPos = list(newPos)  
	### Do actions based on whether player died or ate food ###	
        if playerLocation == 0: #if agent is in blue square after moving
            self.death()
        elif playerLocation == 3: #just ate food
            self.eatFood()
            self.foodCount+=1
            #print("Food count is: ", self.foodCount)
            self.Matrix[self.playerPos[0]][self.playerPos[1]] = 1 #just ate food, reset square to grey
            self.locationsToUpdate.append([self.playerPos[0], self.playerPos[1]])
        ### write move to log ###
        if self.logging:
            self.log+=str(self.clock)+":"+move+";"
            

    def fillQuadrant(self,index, val):  #fills a quadrant number INDEX with the value VAL
        for x in range(self.quadrantBounds[index][0][0], self.quadrantBounds[index][0][1]):
            for y in range(self.quadrantBounds[index][1][0], self.quadrantBounds[index][1][1]):
                self.locationsToUpdate.append([x,y])
                self.Matrix[x][y] = val #MAKE OLD QUADRANT GREY

    def generateFood(self, x=-1, y=-1): #generates center for where food will be
        #first, replace old quadrant's food with grey
        oldQuadrant = (self.quadrant-2) % 4
        self.fillQuadrant(oldQuadrant,1)
        #random food will be generated in the following configuration in a quadrant:
        # xxx
        # x*x
        # xxx Where * is a empty and x has food
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
        ###set center of food to x,y
        self.foodPos = [x,y]
        #Given center, generates pattern
        #inputs: x,y, coordinates of randomly chosen center point
        #this function generates food in a pattern around the center point
        for xnew in range(x-1, x+2):
            for ynew in range(y-1,y+2):
                if xnew!=x or ynew!=y: #choose every location BUT (x,y)
                    self.Matrix[xnew][ynew] = 3
                    self.locationsToUpdate.append([xnew,ynew])

    def death(self):
        pass
        #print("Player just died!")

    def eatFood(self):
        self.timeSinceFood = 0

    def cleanup(self): #method to call when game ends. Does cleanup
        self.log += "***"
        self.log+="TotalScore:" + str(self.score) + ";"
        self.log+="ClockTicks:" + str(self.clock) + ";"
        self.log+="FoodCount:" + str(self.foodCount)

    def desiredOutput(self):
        #check if we can move one space toward food to get it. If so, its legitimate output
        moveToFood = self.moveToFoodOutput()
        if moveToFood!=[0,0,0,0]:
            return moveToFood
        else:
            return self.smellOfFoodOutputComplex()
        


    def moveToFoodOutput(self):
        ###checks if the agent can move one direction to get food
        ###if the agent can, then desired output should be toward that food
        ###otherwise, return [0,0,0,0]
        retMatrix = [0,0,0,0]
        if self.Matrix[self.playerPos[0]] [self.playerPos[1]-1] == 3: #food is up
            retMatrix[0] = 1
        if self.Matrix[self.playerPos[0]-1] [self.playerPos[1]] == 3: #food is left
            retMatrix[1] = 1
        if self.Matrix[self.playerPos[0]] [self.playerPos[1]+1] == 3: #food is down
            retMatrix[2] = 1
        if self.Matrix[self.playerPos[0]+1] [self.playerPos[1]] == 3: #food is right
            retMatrix[3] = 1
        return retMatrix

    ###Training functions for back prop
    def smellOfFoodOutputSimple(self):
        if self.foodPos == [-1,-1]:
            print("smellOfFoodOutputSimple Error! FoodPos at (-1,-1)!")
            return [0,0,0,0]
        #smellOfFoodOutputSimple: Returns '1' for directions toward center of food, '0' for direcitons away from it
        playerP = self.playerPos
        foodP = self.foodPos
        offset = [self.foodPos[i]-self.playerPos[i] for i in range(0,2)]
        retMatrix = [0,0,0,0] #matrix of desired output; initialize to 0 in each direction
        if offset[0]>0: #if food is to the right, we want to move right
            retMatrix[moveDict['right']] = 1
        else:
            retMatrix[moveDict['left']] = 1
        if offset[1]>0: #if food is farther down, we want to move down
            retMatrix[moveDict['down']] = 1
        else:
            retMatrix[moveDict['up']] = 1
        return retMatrix

    def smellOfFoodOutputComplex(self):
        if self.foodPos == [-1,-1]:
            print("smellOfFoodOutputComplex Error! FoodPos at (-1,-1)!")
            return [0,0,0,0]
        #smellOfFoodOutputSimple: Returns normalized desired output
            #where the direction we have to move the most in to get food is outputted as '1'
            #and the second-most direction is outputed as (seondMost/most)
            #For instance, if the food center was 5 squares up and 2 to the right, the return would be:
                #up: 1, right: 2/5, down: 0, left: 0

            
        offset = [self.foodPos[i]-self.playerPos[i] for i in range(0,2)]
        retMatrix = [0,0,0,0] #matrix of desired output; initialize to 0 in each direction
        dir1 = 'right' if offset[0]>0 else 'left'
        dir2 = 'down' if offset[1]>0 else 'up'
        if abs(offset[0]) > abs(offset[1]):
            primaryDir = dir1
            secondaryDir = dir2
            if offset[0]==0:
                secondary = 0
            else:
                secondary = offset[1]/offset[0] #secondary is the output for the non-primary direction
        else:
            primaryDir = dir2
            secondaryDir = dir1
            if offset[1]==0:
                secondary = 0
            else:
                secondary = offset[0]/offset[1] 
        retMatrix[moveDict[primaryDir]] = 1 #the offset for the primary direction toward food is 1
        retMatrix[moveDict[secondaryDir]] = secondary #the offset for the secondary direction toward food is a ratio of 
                                                        #secondaryMagnitude/primaryMagnitude
        return retMatrix                 

    def inMatrixBounds(self,pos):
        #input: POS, an array of 2 elements representing a position
        #output: boolean representing whether pos is in bounds of self.Matrix
        return pos[0]<len(self.Matrix) and pos[1]<len(self.Matrix) and pos[0]>-1 and pos[1]>-1

    def sight(self):
        #returns an array of four values, up left down right, representing whether food is seen in that direction
        ret = [0,0,0,0] #array to return
        ###up
        p = list(self.playerPos)
        sightColor = self.Matrix[p[0]][p[1]]
        while(self.inMatrixBounds(p) and sightColor==1):
            p[1]-=1  #go up 
            sightColor = self.Matrix[p[0]][p[1]]
        if sightColor==3: #if we see food
            ret[0]=1
        ###left
        p = list(self.playerPos)
        sightColor = self.Matrix[p[0]][p[1]]
        while(self.inMatrixBounds(p) and sightColor==1):
            p[0]-=1  #go left 
            sightColor = self.Matrix[p[0]][p[1]]
        if sightColor==3: #if we see food
            ret[1]=1
        ###down
        p = list(self.playerPos)
        sightColor = self.Matrix[p[0]][p[1]]
        while(self.inMatrixBounds(p) and sightColor==1):
            p[1]+=1  #go down 
            sightColor = self.Matrix[p[0]][p[1]]
        if sightColor==3: #if we see food
            ret[2]=1
        ###right
        p = list(self.playerPos)
        sightColor = self.Matrix[p[0]][p[1]]
        while(self.inMatrixBounds(p) and sightColor==1):
            p[0]+=1  #go right 
            sightColor = self.Matrix[p[0]][p[1]]
        if sightColor==3: #if we see food
            ret[3]=1

        #print("Sight is: ", ret)
        return ret
        
                    


        
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


def getSenses():
    senses = {}
    senses.update({"timeSinceFood": True})
    senses.update({"moveBuffer": True})
    senses.update({"clockInput": True})
    senses.update({"quadInput": True})
    senses.update({"lineSight": True})
    senses.update({"smell": False})
    return senses

def getSensesNodeCount():
    sensesSizeDict = { "timeSinceFood":1, "moveBuffer":4, 'clockInput':1, \
                      'quadInput':2, 'lineSight':4, 'smell':0}
    senses = getSenses()
    count = 0
    for key, b in senses.items():
        if b==True: #if the sense is turned on
            count+=sensesSizeDict[key]
    return count
            

def getNNInput(board, senses):
    inputList = []
    #BOARD is a gameMap object
    #SENSES is a dictionary that says which sensory information to give the NN

####  Time since food  ####
#### Resets to 1 when you eat food, and degrades by a constant (.1) each clock tick without food
    if "timeSinceFood" in senses:
        if senses["timeSinceFood"]==True:
            timeSinceFoodInput = max(1 - (.1 * board.timeSinceFood), 0)
            inputList.append(timeSinceFoodInput)

####  moveBuffer  ####
###Four numbers representing each direction. Degrades by ~.2 each clock tick, 
#resets to 1 when you move in that direction
    if "moveBuffer" in senses:
        if senses["moveBuffer"]==True:
            inputList.append(board.moveBuffer[0])
            inputList.append(board.moveBuffer[1])
            inputList.append(board.moveBuffer[2])
            inputList.append(board.moveBuffer[3])
            #print("In getNNInput, moveBuffer is: ", board.moveBuffer)

#### clockInput  ####
### A number from 0 to 1, representing how soon until the food shifts
    if "clockInput" in senses:
        if senses["clockInput"]==True:
            #normalize timeUntilShift as clockInput
            clockInput = ( board.quadrantShiftTime - board.timeUntilShift() ) / board.quadrantShiftTime
            inputList.append(clockInput)
                                    
#### quadInput  ####
###Represents the current quadrant that food is in. Two inputs for binary representation
    if "quadInput" in senses:
        if senses["quadInput"]==True:
            quad = board.quadrant
            quadInput0 = board.quadrant//2
            if quad==3 or quad==0:
                quadInput1 = 1
            else:
                quadInput1 = 0
            inputList.append(quadInput0)
            inputList.append(quadInput1)

### lineSight ###
### four element matrix representing directions, 0 if we see water, 1 if we see food
    if "lineSight" in senses:
        if senses["lineSight"]==True:
            sight = board.sight()
            for s in sight:
                inputList.append(s)
            


#####TODO: ADD MORE SENSES #####---------------------------------
    
    NNInput = {}
    for i, val in enumerate(inputList):
        NNInput.update({nodeNames[i]:val})
    return NNInput


#### MAIN GAME LOOP #####
def simulateGame(net=None, NNClockCycles=50, logFile = ""):
    clockShiftCount = 0
   ### Determine Mode ###
    fromNN = net!=None
    fromLog = logFile!=""
    fromUser = not(fromNN) and not(fromLog)

    ### pygame, board, clock initialization ###
    board = gameMap()

    ###  Populate Board ###
    if visualMode:
        fpsClock = pygame.time.Clock()
        pygame.init()
        windowSurfaceObj = pygame.display.set_mode((800,800))
        pygame.display.set_caption('Monkey Robots')
        windowSurfaceObj.fill(greyColor) #fills the window with grey
        populateBoard(board, windowSurfaceObj) # fills the initial map


###### USER CONTROL MODE-------------------------------------------------------------------------
    if fromUser:
        if not visualMode:
            print("ERROR: Trying to simulate game out of visual mode!")
            return False
        
        finished = False
        while not finished:
            senses = getSenses()
            NNInput = getNNInput(board,senses)            ##Process Game Events
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

            if visualMode:
                for l in board.locationsToUpdate:
                    x = l[0]
                    y = l[1]
                    pygame.draw.polygon(windowSurfaceObj, mapColor(board.Matrix[x][y]), ( (x*20, y*20), ((x*20)+20, y*20),((x*20)+20, (y*20)+20), (x*20, (y*20)+20)) )
                pygame.draw.circle(windowSurfaceObj, redColor, (board.playerPos[0]*20 + 10, board.playerPos[1]*20 + 10), 10)
                board.locationsToUpdate = []

    
            if board.clock % board.quadrantShiftTime == 0:
                board.shiftQuadrant()
                board.generateFood()
            print("agent location is: ", board.playerPos)
    
            pygame.display.update()
            board.clock+=1
            fpsClock.tick(1)
#######END USER MODE-------------------------------------------------------------------------


####### NEURAL NET MODE ##### ---------------------------------------------------------------
    elif fromNN:
        randNNInput = False   #flag for if NN is given random input or input from the game. For testing purposes. 
        backPropOn = net.backPropOn   #flag for if we should do backprop
        #backPropFunction = smellOfFoodOutputComplex  #which function we use for desired output in backpropogation
        
        finished = False
        endGameClock = NNClockCycles*board.quadrantShiftTime
        ###Main game loop
        NNInput = {}
        while board.clock < endGameClock and not(finished):
            #first, get all the inputs

          #####OTHER GAME STUFF ######              
            if board.clock%board.quadrantShiftTime == 0:
                clockShiftCount+=1
             #   if clockShiftCount%100==0:
             #       print(clockShiftCount)
                board.shiftQuadrant()
                board.generateFood()
            senses = getSenses()

            NNInput = getNNInput(board,senses)          


            actualOutput = None
            if randNNInput == False:
                activ = NNInput
            else:
                activ = net.randActivation()

            outty = net.feedForward(activ)
            actualOutput = outty
            if backPropOn:
                outputMatrix = board.desiredOutput()
                #outputMatrix = board.smellOfFoodOutputComplex()
                desiredOutput = net.moveListToOutputDict(outputMatrix)
                net.backPropogation(actualOutput, desiredOutput)
                
           # print("\tinput/output/activation: ", NNInput, "     ", outty, "      ", activ)
            move = decideMoveFromNNOutput(outty, net)
            #print("MOVE IS: ", move)
            if move!=None:
                board.moveAgent(move)
            else:
                print("Simulating from NN Error: Couldn't find a move from NN output!")
            


            if visualMode:
                for l in board.locationsToUpdate:
                    x = l[0]
                    y = l[1]
                    pygame.draw.polygon(windowSurfaceObj, mapColor(board.Matrix[x][y]), ( (x*20, y*20), ((x*20)+20, y*20),((x*20)+20, (y*20)+20), (x*20, (y*20)+20)) )
                pygame.draw.circle(windowSurfaceObj, redColor, (board.playerPos[0]*20 + 10, board.playerPos[1]*20 + 10), 10)
                board.locationsToUpdate = []


            ###event manager


            board.clock+=1    
            if visualMode:
                for event in pygame.event.get():
                    if event.type==QUIT:
                        #pygame.quit()
                        #sys.exit()
                        finished = True                
                pygame.display.update()
                fpsClock.tick(10)            


#####END NEURAL NET MODE -------------------------------------------------------------------        


###### LOG MODE -------------------------------------------------------------------------------
    ###Main game Loop
    elif fromLog:
        f = open(logFile, 'r')
        gameString = f.read()
        f.close()
        gameEvents = logToDictionary(gameString) #a dictionary of clock time/game events
        totalClockTicks = gameEvents["ClockTicks"]
        if(totalClockTicks<=0):
            return
        
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

            pygame.display.update()
            board.clock+=1
            fpsClock.tick(10)


   ####END LOG MODE --------------------------------------------------------------------------- 
    else:
        print("Warning! fromUser, fromNN, and fromLog all false!!!!")

        
    #### Clean up ###
    #print("Out of game")
    #print("\tScore is: ", board.foodCount)
    board.cleanup()
    if not fromLog:
        writeLogToFile("output.txt", board.log)
    if visualMode:
        pygame.quit()
    if net!=None:
        pass
        #return net.pickle()
    return board.foodCount

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
        #print(e)
        #first, get the clock time
        logEntry = e.split(':')
        #print(logEntry)
        if len(logEntry)>1: #edge case- in case there is empty event
            time = int(logEntry[0])
            #print('time: ', time)
            event = logEntry[1]
            #print('event: ', event)
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
                          

def decideMoveFromNNOutput(d, net): #d = output from net
    ####Know which move each NN node name correlates to. i.e. 'k' is up ###
    totalN = 0
    for x in range(0, len(net.layersSize)-1):
        totalN += net.layersSize[x]
    moveDict = {}
    moveDict.update({net.nodeNames[totalN]:'up'})
    moveDict.update({net.nodeNames[totalN+1]:'left'})
    moveDict.update({net.nodeNames[totalN+2]:'down'})
    moveDict.update({net.nodeNames[totalN+3]:'right'})

    ###now, iterate through the output from the net to decide a move
    maxStrength = -1
    maxNode = ''
    for node, strength in d.items():
        if strength > maxStrength:
            maxStrength = strength
            maxNode = node
    #now we have the strongest node activation from the given output
    if maxNode in moveDict:
        return moveDict[maxNode]
    else:
        print ("decideMoveFromNNOutput ERROR! Node Misalignment, coudln't determine output!!!")
        return None
                            
    
    
    
#Christina (but not actually christina) was here
# Jacob was here and Lorenz smells like old butthole. Boop.

# You'll never find my other comment.
