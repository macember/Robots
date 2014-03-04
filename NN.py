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
    def __init__(self, Name):
        self.name = Name        #name of node (used for indexing)
        self.layer = 0
        self.threshold = 0   #usually between .25-1
        self.upConnections = {}     #TOWARD OUTPUT, node name : connection weights
        self.downConnections = {}   #TOWARD INPUT, node name : connection weights
        ###stuff to reset with each run
        self.output = 0
        self.totalInput = 0
        self.error = 0

    def reset(self):
        self.output = 0
        self.totalInput = 0
        self.error = 0

    def printNodeCnxn(self):
        print("Theta:            ", self.threshold)
        print("Up connections:   ", self.upConnections)
        print("Down connections: ", self.downConnections)

    def printNode(self):
        print("Printing Node:", self.name)
        print("\tlayer is:", self.layer)
        print("\tthreshold is:", self.threshold)
        print("\tUp connections are given by:", self.upConnections)
        print("\tDown connections are given by:", self.downConnections)        
        print("\tand our output is:", self.output)


def runScript():
    N = NN()
    N.randNN([2,2])
    activation = {'a':.5, 'b':-.2}
    return N.feedForward(activation)

def testFeedForward():
    N = NN()
    N.randNN([1,1,1,1])
    print("Alpha value: ",N.alpha)
    activation = {'a':.5}
    for x in range(0,1):
        N.feedForward(activation)
    return N


class NN:
    def __init__(self, dna=""):
        self.nodes = {}       #key=node name, value = node object
        self.alpha = .2
        self.sigmoidA = 1 
        self.DNA = dna       #encoded __dict__ of class
        random.seed()        #seed random number generator
        self.layersSize = [] #size of each layer, e.g. [4,3,2] has 4 input, 3 middle, 2 output
        self.layers = []    #List-of-lists. Each node object in each layer. e.g. [ ['a','b','c'] , ['d','e'], ['f'] ]
        self.nodeNames = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

    def printNNCnxn(self):
        for nodey in self.nodes.values():
            print(nodey.name)
            nodey.printNodeCnxn()

    def updateWeight(self, A, B, newWeight): #input: two nodes and a new weight
        nameA = A.name
        nameB = B.name
        if nameB in A.upConnections:
            A.upConnections[nameB] = newWeight
            B.downConnections[nameA] = newWeight
            return True
        elif nameB in A.downConnections:
            A.downConnections[nameB] = newWeight
            B.upConnections[nameA] = newWeight
            return True
        else:
            print("updateWeight ERROR; Could not find given connection!")
            return False
            

    def getDesiredOutput(self):
        ret = {}
        x = True
        for outputNode in self.layers[len(self.layers)-1]:
            if x:
                x = False
                ret.update({outputNode.name:1})
            else:
                ret.update({outputNode.name:0})
        return ret
    
    def feedForward(self, activation):
        ###input- ACTIVATION, a dictionary with each input node and its activation weight
        for key, activ in activation.items():
            self.nodes[key].output = activ #set the activation for the input nodes given parameter


        #for each layer but the last, send activation down
        for layerIndex in range(0,len(self.layers)-1):  #for each non-output layer
            for node in self.layers[layerIndex]:        #for each node in that layer
                node.output = sigmoid(self.sigmoidA, node.totalInput + node.threshold)  #set the output for the node based on totalInput
                print("Node ", node.name, "output: ", node.output)
                print("Node connections: ",node.upConnections.items())
                
                for up, weight in node.upConnections.items(): #for each upConnection
                    upNode = self.nodes[up]     #the node we're connecting to
                    upNode.totalInput += node.output * weight
                    print("Sent up activation from node ", node.name, " to node ", up)
                    print(upNode.name,"total input: ",upNode.totalInput)
                    print("------------------------")

        #now run the output through sigmoid function
        outDictionary = {} #output dictionary that gives outputnode:outputStrength
        for node in self.layers[len(self.layers)-1]:
            node.output = sigmoid(self.sigmoidA, node.totalInput)
            outDictionary.update({node.name:node.output})
        print(outDictionary.items())

        desiredOutput = self.getDesiredOutput()
        print('\ncalling back propogation with output: ', desiredOutput)
        self.backPropogation(outDictionary, desiredOutput)
        return outDictionary

    

    def backPropogation(self, actualOutput, expectedOutput):
        #step1- take in desiredOutput for output layer, put in function to find error value

        #error = z(1-z)(y-z), z=output, y=desiredOutput
        for nodeName, z in actualOutput.items():
            y = expectedOutput[nodeName]
            error = z*(1-z) * (y-z)
            self.nodes[nodeName].error = error
        #FORMULA FOR OUTPUT NODES:
        #change in threshold = alpha * error
        #change in connection weights = change in threshold * x(i), where x(i) = input to this output node
        print("\n~~~~~ OUTPUT LAYER BACKPROP ~~~~~~ ")
        for outNode in self.layers[len(self.layers)-1]:
            deltaThreshold = outNode.error * self.alpha
            outNode.threshold += deltaThreshold

            print("NODE: ", outNode.name)
            print("Change in threshold is: ", deltaThreshold)
            print("\tThreshold is: ", outNode.threshold) 
            for downC, weight in outNode.downConnections.items(): #for downCnnection, weight
                deltaWeight = deltaThreshold * self.nodes[downC].output
                newWeight = weight = deltaWeight
                self.updateWeight(outNode, self.nodes[downC], newWeight)
                print("At connection between ", outNode.name, " and ", \
                      self.nodes[downC].name, ", change in weight is ", deltaWeight)
        
        #FORMULA FOR MIDDLE NODES
        # errorValue = z(1-z) * SUM(m(i) * p(i)),
        # z = output of node, m(i) = connection to node i toward output, pi = error values for connected node

        #for each middle layer
        print("\n~~~~~ MIDDLE LAYER BACKPROP ~~~~~")
        for i in range(len(self.layers)-2,0,-1): #for each middle layer
            print("\nEntering layer: ", self.layers[i][0].layer)
            for middleNode in self.layers[i]: #for each middle node
                print("NODE: ", middleNode.name)
                ###calculate error value for middle node
                output = middleNode.output
                #calculate sum of connection to output node and error value for output node
                MiPiSum = 0
                for nodeName, weight in middleNode.upConnections.items():
                    upNode = self.nodes[nodeName]
                    MiPiSum += weight * upNode.error
                #print("Done calculating MiPiSum for node ", middleNode.name, ", it is: ", MiPiSum)
                middleNode.error = output * (1- output) * MiPiSum
                print("Error: ", middleNode.error)
                ####Calculate deltaThreshold for middle node then deltaWeight for each downNode
                deltaThreshold = middleNode.error * self.alpha
                for downC, weight in middleNode.downConnections.items():
                    deltaWeight = deltaThreshold * self.nodes[downC].output
                    newWeight += deltaWeight
                    weight += deltaWeight
                    self.updateWeight(middleNode, self.nodes[downC], newWeight)
                    print("At connection between ", middleNode.name, " and ", \
                          self.nodes[downC].name, ", change in weight is ", deltaWeight)
                
        #now, reset all values for nodes
        for node in self.nodes.values():
            node.reset()

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
        if self.layersSize == []:
            print("ERROR! Trying to call fillLayers given empty layersSize array!")
        else:
            currentNode = 0
            for layer in range(0, len(self.layersSize)):
                self.layers.append([]) #create empy list for each layer
            for node in self.nodes.values():
                l = node.layer
                self.layers[l].append(node)
            

    def randNN(self, layers):
        self.layersSize = layers
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
                n.threshold = round(random.uniform(.25,1), 3)
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
                    self.nodes[nodeName].upConnections.update({targetNode:connectionWeight}) #node name/weight
                    self.nodes[targetNode].downConnections.update( {self.nodeNames[nodeIndex]: connectionWeight} )
                nodeIndex+=1
        #after nodes are created, fill layers
        self.fillLayers()

    def printNN(self):
        for nodey in self.nodes.values():
            nodey.printNode()
            print("\t\n")
                        
def writeToFile(filename, toWrite):
    f = open(filename, 'w')
    f.write(toWrite)
    f.close()

def readFromFile(filename):
    f = open(filename, 'r')
    string = f.read()
    f.close()
    return string
