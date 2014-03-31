from NN import *
import random

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
    def __init__(self, nnSize):
        # AGENTS: a dictionary of NNs stored as NUMBER:NN
        self.agents = {}
        # NNSIZE: 
        self.nnSize = nnSize
        # LIFETIME: how many trials each NN gets before breeding
        self.lifetime = 2000
        # BREEDINGPAIRS: a list of tuples, each containing the name of
        # two NNs that should be bred (as established by the selection function)
        self.breedingPairs = []

    # RANDPOP
    # -----------------
    # Creates a population containing NUMAGENTS agents,
    # each with AGENTLAYERS layer sizes
    def randPop(self, numAgents):
        for agentIndex in range(0,numAgents):
            N = NN()
            agent = N.randNN(self.nnSize)
            self.agents.update({agentIndex:agent})

    def printPop(self):
        for agentIndex in range(0,len(self.agents)):
            print('Agent ', agentIndex, ' checking in!')
    
    # TRAINGENERATION
    # ------------------
    # Trains each NN in population, for the amount of time specified
    # by the LIFETIME value
    def trainGeneration(self):
        # for each agent in the dictionary...
        for agentIndex in range(0,len(self.agents)):
            # train that agent LIFETIME times
            self.agents[agentIndex].trainNN(self.lifetime)
    
    # SORTBYFITNESS
    # --------------------
    # Creates a list of agent names (numerals) in order of
    # the agents' fitness scores
    def sortByFitness(self):
        sortedAgents = []
        # walk through each agent in population
        for agentName in range(0,len(self.agents)):
            # set current agent
            curAgent = self.agents[agentName]
            # if list is empty, insert agentName
            if len(sortedAgents) == 0:
                sortedAgents.insert(0, agentName)
                print('Inserting first agent into list')
            else:
                # walk through each item in the sorted list
                for listPos in range(0,len(sortedAgents)):
                    # select the agent we're comparing fitness to
                    compareAgent = self.agents[sortedAgents[listPos]]
                    # if the current agent has greater fitness than agent
                    # at current position in list ...
                    if curAgent.fitnessScore > compareAgent.fitnessScore:
                        # insert the agent's name into the list and break
                        sortedAgents.insert(listPos, agentName)
                        break
                # if current agent doesn't have better fitness than ANY
                # sorted agent, insert it at end of list
                else:
                    sortedAgents.insert(len(sortedAgents), agentName)
        return sortedAgents
    
    # CREATENEWGENERATION
    # --------------------
    # [Assumes old generation is already trained.]
    # Takes in a selection function (for creating breeding pairs)
    # and a breeding function (for breeding two pairs of NNs together)
    # and creates a new population by using the breeding func on the
    # generated pairs
    def createNewGeneration(self, selectionFunc, breedingFunc):

        # Sort old generation by fitness
        sortedOldGen = self.sortByFitness()
        
        # Use selection func to create list of pairs to breed
        breedingPairs = selectionFunc(sortedOldGen)
        
        # Use breeding func to move through list of breeding pairs,
        # and set the newly-created dictionary of agents as the new population
        newGen = breedingFunc(breedingPairs, self.agents, self.nnSize)
    
# ============================
# SELECTION FUNCTIONS
# ============================
# INPUT: a list of agent names (numerals) already ordered by fitness
# OUTPUT: a list of tuples, each of which contains two agent names and
# represents all the agent pairs that should be bred

def selFuncA(sortedOldGen):
    breedingPairs = []
    for agentPos in range(0, len(sortedOldGen)/3):
        agent0 = sortedOldGen[agentPos]
        agent1 = sortedOldGen[agentPos + 1]
        agent2 = sortedOldGen[agentPos + 2]
        agent3 = sortedOldGen[agentPos + 3]
        breedingPairs.append((agent0, agent1))
        breedingPairs.append((agent0, agent2))
        breedingPairs.append((agent0, agent3))
    return breedingPairs

# ============================
# BREEDING FUNCTIONS
# ============================
# INPUT: a list of tuples representing the names of agents to be bred in pairs;
# a dictionary of agents which the names refer too;
# the current NN-size
# OUTPUT: a new dictionary containing the children agents

def breedingFuncA(breedingPairs, agentDictionary, nnSize):
    for pairIndex in range(0,len(breedingPairs)):
        newAgent = NN()
        newAgent.layersSize = nnSize
        cumLayers = cumulativeLayers(nnSize)
        totalNodes = sum(layers)
        parents = breedingPairs[pairIndex]
        
        # Instantiate all nodes
        for layerIndex in range(0,len(nnSize)):
            for nodeIndex in range(0,layers[layerIndex]):
                n = Node(self.nodeNames[nodeIndex])
                n.layer = layerIndex
                # METHOD FOR CHOOSING THRESHOLD?
                # n.threshold = ???
                self.nodes.update({self.nodeNames[nodeIndex]:n})

        for layerIndex in range(0,len(layers)-1):
            for nodeIndex in range(0,layers[layerIndex]):
                nodeName = self.nodeNames[nodeIndex]
                for i in range(0,layers[layerIndex+1]):
                    selectedParent = parents[random.randint(0,1)]
                    connectionWeight = selectedParent.nodes[nodeName]
                    #MORE COMING SOON!
                
### IDEA: We should probably have a more abstracted thing going where
# we create a NN using a given rule for establishing connection weights, so we
# don't have to keep copying this same code from randNN() over and over.
