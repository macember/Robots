from NN import *
from Robots_Game import *
import random
import copy

Lamarck = False
initialTrainingPeriod = True
preTrainingTime = 1000
lifetime = 30
Asexual = True


# =========================
# THING I NEED IN NN CLASS
# =========================
#
# trainNN(lifetime)
# -----------------
# INPUT: lifetime, a number indicating how many trails the agent
# should be run for
# RESULT: trains NN for that number of times, sets new fitness number
#
# fitnessScore
# -----------------
# a value that's updated to contain the fitness score
#

# =================
# AGENT class
# =================
# a member of the population
class Agent:
    def __init__(self, N):
        self.fitnessScore = -1
        self.net = N
        self.generation = 0

    def trainNN(self, cycles=lifetime, initialTrainingPeriod=False):
        beforeNet = copy.deepcopy(self.net)
        #print("BEFORE NET IS: ")
        #beforeNet.printNNCompact()
        self.fitnessScore = simulateGame(self.net, cycles)
        if Lamarck==False and initialTrainingPeriod==False: #we don't want to keep the training changes
            self.net = beforeNet
            
       # print("AFTER NET IS: ")
        #self.net.printNNCompact()
        #in the process of simulating the game, the net is trained


# =================
# POPULATION class
# =================
# contains:
#   a library of NNs
#   a list marking the order of those NN by fitness
#
# can do:
#   - Create a random population
#   - Train each member of a given population X number of times
#   - Use a breeding function to create breeding pairs based on fitness
#   - Breed the breeding pairs

class Population:
    def __init__(self):
        # AGENTS: a dictionary of NNs stored as NUMBER:NN
        self.agents = {}
        self.middleNodeCount = 6
        self.nnSize = []
        self.nnSize.append(getSensesNodeCount())
        self.nnSize.append(self.middleNodeCount)
        self.nnSize.append(4)
        # NNSIZE: 
        # LIFETIME: how many trials each NN gets before breeding
        self.lifetime = lifetime
        # BREEDINGPAIRS: a list of tuples, each containing the name of
        # two NNs that should be bred (as established by the selection function)
        self.breedingPairs = []
        # AVERAGEGENFITNESS: the current generation's average fitness.
        self.averageGenFitness = 0

    # RANDPOP
    # -----------------
    # Creates a population containing NUMAGENTS agents,
    # each with AGENTLAYERS layer sizes
    def randPop(self, numAgents):
        for agentIndex in range(0,numAgents):
            N = NN()
            N.randNN(self.nnSize)
            agent = Agent(N)
            self.agents.update({agentIndex:agent})

    def printPop(self):
        for agentIndex in range(0,len(self.agents)):
            print('Agent ', agentIndex, ' checking in!')

   
    # TRAINGENERATION
    # ------------------
    # Trains each NN in population, for the amount of time specified
    # by the LIFETIME value
    def trainGeneration(self, cycles=None):
        print("Training generation for ", cycles)
        totalFitness = 0;
        # for each agent in the dictionary...
        for agentIndex in range(0,len(self.agents)):
            # train that agent LIFETIME times
            curAgent = self.agents[agentIndex]
            trainingTime = cycles if cycles!=None else self.lifetime
            curAgent.trainNN(trainingTime)
            totalFitness += curAgent.fitnessScore
        self.averageGenFitness = totalFitness / len(self.agents)        


    def trainInitialGeneration(self):
        print("Training generation for ", preTrainingTime)
        totalFitness = 0;
        # for each agent in the dictionary...
        for agentIndex in range(0,len(self.agents)):
            # train that agent LIFETIME times
            curAgent = self.agents[agentIndex]
            trainingTime = preTrainingTime
            curAgent.trainNN(trainingTime, True)
            totalFitness += curAgent.fitnessScore
        self.averageGenFitness = totalFitness / len(self.agents) 

    
    # SORTBYFITNESS
    # --------------------
    # Creates a list of agent names (numerals) in order of
    # the agents' fitness scores
    def sortByFitness(self):
        sortedAgents = []
        L = sorted(self.agents.items(), key= lambda kv : kv[1].fitnessScore, reverse=True)
        return list(map(lambda ab:ab[0], L))
    
    # CREATENEWGENERATION
    # --------------------
    # [Assumes old generation is already trained.]
    # Takes in a selection function (for creating breeding pairs)
    # and a breeding function (for breeding two pairs of NNs together)
    # and creates a new population by using the breeding func on the
    # generated pairs
    def createNewGeneration(self, selectionFunc, breedingMode):

        # Sort old generation by fitness
        sortedOldGen = self.sortByFitness()
        # Use selection func to create list of pairs to breed
        self.breedingPairs = selectionFunc(sortedOldGen)
        
        # Use breeding func to move through list of breeding pairs,
        # and set the newly-created dictionary of agents as the new population
        if not Asexual:
            self.agents = self.breedingFunc(breedingMode)
        else:
            self.agents = self.breedingFuncAsexual(breedingMode)

        # Reset average fitness
        averageGenFitness = 0


    def breedingFunc(self, mode):
        breedingPairs = self.breedingPairs
        agentDict = self.agents
        newAgentDict = {}
        agentCounter = 0
        for i,j in breedingPairs:
            parent1 = agentDict[i].net
            parent2 = agentDict[j].net
            child = mixNeuralNets(parent1,parent2,mode)
            A = Agent(child)
            newAgentDict.update({agentCounter:A})
            agentCounter+=1
        return newAgentDict
        
    def breedingFuncAsexual(self,mode=0):
        breedingPairs = self.breedingPairs
        agentDict = self.agents
        newAgentDict = {}
        agentCounter = 0
        for i in breedingPairs:
            for repetition in range(0,3): #for each net, make three children
                child = mixNeuralNetAsexual(agentDict[i].net, mode)
                A = Agent(child)
                newAgentDict.update({agentCounter:A})
                agentCounter+=1
        return newAgentDict
        


def mixNeuralNetAsexual(parent,mode=0):
    majorMutationRate = 100 #mutate on average 1/100 times
    minorMutationRate = 4
    minMultiplier = .9
    maxMultiplier = 1.1
    layers = parent.layersSize
    if mode==0:
        child = NN(layers)
        for nodey in child.nodes.values(): #for each node
            for connection in nodey.upConnections.keys(): #for each node that its connected to
                connectionWeight = parent.nodes[nodey.name].upConnections[connection]
                if random.randint(0,majorMutationRate)==0:
                    newConnectionWeight = random.uniform(-1,1)
                elif random.randint(0,minorMutationRate)==0:
                    multiplier = random.uniform(minMultiplier,maxMultiplier)
                    newConnectionWeight = connectionWeight * multiplier
                else:
                    newConnectionWeight = connectionWeight
                child.updateWeight(nodey, child.nodes[connection], newConnectionWeight)
        return child
                


### mixNeuralNets; Given two NNs and a mode (way of mixing), outputs a child NN
def mixNeuralNets(parent1, parent2, mode):
    mutationRate = 100 #mutate on average 1/100 times
    layers = parent1.layersSize
    if mode==0: ###randomly choose for each connection from one or the other parent. mutation off
        child = NN(layers)
        for nodey in child.nodes.values(): #for each node
            for connection in nodey.upConnections.keys(): # for each node that its connected to 
                randParent = parent1 if random.randint(0,1)==0 else parent2
                connectionWeight = randParent.nodes[nodey.name].upConnections[connection]
                child.updateWeight(nodey, child.nodes[connection], connectionWeight)
        return child

    elif mode==1:  #randomly choose for each connection, mutate to give random weight every 1/100 randomly
        child = NN(layers)
        for nodey in child.nodes.values(): #for each node
            for connection in nodey.upConnections.keys(): # for each node that its connected to
                if random.randint(1,mutationRate) == 1:
                    connectionWeight = random.uniform(-1,1)
                    print("rando used!")
                else:
                    randParent = parent1 if random.randint(0,1)==0 else parent2
                    connectionWeight = randParent.nodes[nodey.name].upConnections[connection]
                child.updateWeight(nodey, child.nodes[connection], connectionWeight)
        return child


def runXGenerations(gens, popSize=10):
    breedingMode = 0 #for calling breedingFunc
    P = Population()
    P.randPop(popSize)
    print("\nOn generation 0")
    if initialTrainingPeriod:
        P.trainInitialGeneration()
    else:
        P.trainGeneration()
    print("Average score for generation 0: ", P.averageGenFitness)

    if  not Asexual:
        P.createNewGeneration(selFuncA, breedingMode)
    else:
        P.createNewGeneration(selFuncAsexual, breedingMode)
        
    
    for genIndex in range(1,gens):
        print("\nOn generation ", genIndex)
        P.trainGeneration(P.lifetime)
        print("Average score for generation ", genIndex, ": ", P.averageGenFitness)
       # print("Creating new generation")
        if not Asexual:       
            P.createNewGeneration(selFuncA, breedingMode)
        else:
            P.createNewGeneration(selFuncAsexual, breedingMode)
       # print("Finished creating new generations")
    
# ============================
# SELECTION FUNCTIONS
# ============================
# INPUT: a list of agent names (numerals) already ordered by fitness
# OUTPUT: a list of tuples, each of which contains two agent names and
# represents all the agent pairs that should be bred

def selFuncA(sortedOldGen):
    print("sortedOldgen is: ", sortedOldGen, " fitness scores are: ")
    if len(sortedOldGen)<5:
        print("selFuncA error! Length shouldn't be less than 9")

    breedingPairs = []
    for agentPos in range(0, len(sortedOldGen)//3):
        agent0 = sortedOldGen[agentPos]
        agent1 = sortedOldGen[agentPos + 1]
        agent2 = sortedOldGen[agentPos + 2]
        agent3 = sortedOldGen[agentPos + 3]
        breedingPairs.append((agent0, agent1))
        breedingPairs.append((agent0, agent2))
        breedingPairs.append((agent0, agent3))
    return breedingPairs

def selFuncAsexual(sortedOldGen):
    breedingPairs = []
    for agentPos in range(0, len(sortedOldGen)//3):
        breedingPairs.append(sortedOldGen[agentPos])
    return breedingPairs


# ============================
# BREEDING FUNCTIONS
# ============================
# INPUT: breedingPairs: a list of tuples representing the names of agents to be bred in pairs;
# agentDictionary: a dictionary of agents which the names refer too;
# the current NN-size
# OUTPUT: a new dictionary containing the children agents

def breedingFuncOld(breedingPairs, agentDictionary, layers):
    
    for pairIndex in range(0,len(breedingPairs)): #for each breeding pair
        newAgent = NN() #create new NN
        newAgent.randNN(layers); 
        parents = breedingPairs[pairIndex]
        cumLayers = cumulativeLayers(layers) 
        
        # Update threshold value for each node
        for layerIndex in range(0,len(layers)):
            for nodeIndex in range(0,layers[layerIndex]):
                n = newAgent.nodes[self.nodeNames[cumLayers[layerIndex]+nodeIndex]]
                thresholdParent = parents[random.randint(0,1)]
                n.threshold = agentDictionary[thresholdParent].nodes[n.name].threshold
                
                # METHOD FOR CHOOSING THRESHOLD?
                  
                # if not in the input layer...
                if layerIndex is not 0:
                    for downC, weight in nodeIndex.downConnections.items():
                        selectedParent = parents[random.randint(0,1)]
                        # Select new connection weight
                        #agentDictionary[selectedParent].nodes[n.name].
                        newAgent.updateWeight(n, newAgent.nodes[downC], newWeight)



               

 
