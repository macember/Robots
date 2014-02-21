import random, json

def createTestNN():
    N = NN()
    N.readInputOld('neuralNetDNA.txt')
    return N
    

class Node:
    def __init__(self, Name, Layer=0, Delta=0, Connections={}):
        self.name = Name
        self.layer = int(Layer)
        self.delta = float(Delta)
        self.connections = Connections
        self.output = 0

    def printNode(self):
        print("name is:", self.name)
        print("layer is:", self.layer)
        print("delta is:", self.delta)
        print("connections are given by:", self.connections)
        print("and our output is:", self.output)


class NN:
    def __init__(self, dna=""):
        self.nodes = {}
        self.DNA = dna
        random.seed()

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
            
                

    def randNN(self, layers):
        #input: layers is an array defining the size of each layer
        # e.g. [4,5,3] means 4 input layers, 5 middle, 3 output
        totalNodes = sum(layers)
        if(totalNodes>26 or totalNodes<1):
            print('You aint got enough nodes, muthafucka. You got ', totalNodes, " nodes")
            return        
        nodeNames = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

        ###the number of random connections we will need to generate is layers[0]*layers[1] + layers[1]*layers[2]...layers[n-1]layers[n]
        allConnections = [] 
        for i in range(1,len(layers)):
            for j in range(0, layers[i]*layers[i+1]):
                print('test')
            #    allConnections.append(

        nodeIndex = 1
        layerNumber = 0
        for layer in layers:
            layerNumber+=1
            for i in range(1, layer+1):
                     nodexIndex+=1
                     n = node(nodeNames[nodeIndex], layerNumber)
                     #n.connections = 
                     
            
    def printNN(self):
        for nodey in self.nodes.values():
            print("Printing node ", nodey.name)
            nodey.printNode()
                
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
