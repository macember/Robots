import random, math


def sigmoid(alpha, x):
    return 1 / (1 + math.e**(-1*alpha * x))


def createTestNN():
    N = NN()
    return N
    

def cumulativeLayers(layers):
    retLayers = []
    for num in range(0,len(layers)):
        retLayers.append(sum(layers[:num]))
    return retLayers

class Node:
   # def __init__(self, Name, Layer=0, Delta=0, Connections={}):
    def __init__(self, Name):
        self.name = Name        #name of node (used for indexing)
        self.layer = 0
        self.delta = 0
        self.threshold = 0
        self.upConnections = {}
        self.downConnections = {}
        ###stuff to reset with each run
        self.output = 0
        self.totalInput = 0
        self.error = 0

    def reset(self):
        self.output = 0
        self.totalInput = 0
        self.error = 0

    def printNode(self):
        print("Printing Node:", self.name)
        print("\tlayer is:", self.layer)
        print("\tdelta is:", self.delta)
        print("\tUp connections are given by:", self.upConnections)
        print("\tDown connections are given by:", self.downConnections)        
        print("\tand our output is:", self.output)


def runScript():
    N = NN()
    N.randNN([2,2])
    activation = {'a':.5, 'b':-.2}
    return N.feedForward(activation)

class NN:
    def __init__(self, dna=""):
        self.nodes = {}       #key=node name, value = node object
        self.sigmoidA = 1 
        self.DNA = dna       #encoded __dict__ of class
        random.seed()        #seed random number generator
        self.layersSize = [] #size of each layer, e.g. [4,3,2] has 4 input, 3 middle, 2 output
        self.layers = []    #List-of-lists. names of each node in each layer. e.g. [ ['a','b','c'] , ['d','e'], ['f'] ]
        self.nodeNames = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

    def feedForward(self, activation):

        ###input- ACTIVATION, a dictionary with each input node and its activation weight
        for key, activ in activation.items():
            self.nodes[key].totalInput = activ #set the activation for the input nodes given parameter


        #for each layer but the last, send activation down
        for layerIndex in range(0,len(self.layers)-1):  #for each non-output layer
            for nodeName in self.layers[layerIndex]:        #for each node in that layer
                node = self.nodes[nodeName]
                for up, weight in node.upConnections.items(): #for each upConnection
                    upNode = self.nodes[up]     #the node we're connecting to
                    outty = sigmoid(self.sigmoidA, weight) #send this as output
                    upNode.totalInput += outty
                    print("sent up activation from node ", nodeName, " to node ", up)

        #now run the output through sigmoid function
        outDictionary = {} #output dictionary that gives outputnode:outputStrength
        for outputNode in self.layers[len(self.layers)-1]:
            node = self.nodes[outputNode]
            node.output = sigmoid(self.sigmoidA, node.totalInput)
            outDictionary.update({outputNode:node.output})

        return outDictionary
        

    def pickle(self): #returns a dictionary of the NN. Stores info about NN
        ret = {}
        nodesDict = {}
        for node in self.nodes.values(): #iterate through each node
            key = node.name
            val = node.__dict__
            nodesDict.update({key:val})
        ret.update({"nodes":nodesDict})
        return str(ret)

    def depickle(self, datafile):
        DNAstring = readFromFile(datafile)
        NNdict = eval(DNAstring)
        self.nodes = {}
        for n in NNdict['nodes'].values():
            name = n['name']
            layer = n['layer']
            delta = n['delta']
            connections = n['connections']
            node = Node(name,layer,delta,connections)
            self.nodes.update({name:node})

    def fillLayers(self): #given all nodes{}, fills in layers[] list
        if self.layersSize==[]:
            print("ERROR! Trying to call fillLayers given empty layersSize array!")
        else:
            currentNode = 0
            for layer in range(0, len(self.layersSize)):   #for each layer
                self.layers.append([])
                for i in range(0, self.layersSize[layer]):   #for each node in the layer
                    self.layers[layer].append(self.nodeNames[currentNode])
                    currentNode+=1

    def randNN(self, layers):
        self.layersSize = layers
        self.fillLayers()
        #input: layers is an array defining the size of each layer
        # e.g. [4,5,3] means 4 input layers, 5 middle, 3 output
        cumLayers = cumulativeLayers(layers) 
        totalNodes = sum(layers)
        if(totalNodes>26 or totalNodes<1):
            print('You aint got enough nodes, muthafucka. You got ', totalNodes, " nodes")
            return False      

        ###instantiate all nodes
        nodeIndex = 0
        for layerNum in range(0,len(layers)):  #for each layer
            for eachNode in range(0,layers[layerNum]):            
                n = Node(self.nodeNames[nodeIndex]) #create a new node
                n.layer = layerNum
                self.nodes.update({self.nodeNames[nodeIndex]:n}) #add the node to the dictionary of nodes
                nodeIndex+=1

        nodeIndex = 0                
        for layerNum in range(0,len(layers)-1):  #for each non-ouput layer
            for eachNode in range(0,layers[layerNum]):            
                nodeName = self.nodeNames[nodeIndex]
                for i in range(0, layers[layerNum+1]):         #for each node in the next layer up
                    connectionWeight = random.uniform(-1,1)
                    connectionWeight = round(connectionWeight, 3)
                    targetNode = self.nodeNames[cumLayers[layerNum+1]+i] 
                    self.nodes[nodeName].upConnections.update({targetNode:connectionWeight})
                    self.nodes[targetNode].downConnections.update( {self.nodeNames[nodeIndex]: connectionWeight} )
                nodeIndex+=1

    def printNN(self):
        for nodey in self.nodes.values():
            nodey.printNode()
            print("\t\n")
                
    #def feedForward(self):
        
def writeToFile(filename, toWrite):
    f = open(filename, 'w')
    f.write(toWrite)
    f.close()

def readFromFile(filename):
    f = open(filename, 'r')
    string = f.read()
    f.close()
    return string
    
#TODO- 1. write parser for NN DNA
    #  2. write way to generate random NN 
    #  3. write way to mutate NN 
    #  4. simulate NN running
    #
    #
    #
    #
