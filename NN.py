import random

class Node:
    def __init__(self, Name, Layer=0, Delta=0, Connections={}):
        self.name = Name
        self.layer = Layer
        self.delta = Delta
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

    def randNN(self, layers):
        #input: layers is an array defining the size of each layer
        # e.g. [4,5,3] means 4 input layers, 5 middle, 3 output
        totalNodes = sum(layers)
        if(totalNodes>26 or totalNodes<1):
            print('You aint got enough nodes, muthafucka. You got ', totalNodes, " nodes")
            return        
        nodeNames = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'

        ###the number of random connections we will need to generate is layers[0]*layers[1] + layers[1]*layers[2]...layers[n-1]layers[n]
        allConnections = [] 
        for i in range(1,len(layers))
            for j in range(0, layers[i]*layers[i+1]):
            #    allConnections.append(    

        nodeIndex = 1
        layerNumber = 0
        for layer in layers:
            layerNumber+=1
            for i in range(1, layer+1):
                     nodexIndex+=1
                     n = node(nodeNames[nodeIndex], layerNumber)
                     n.connections = 
                     
                     
        

    def readInput(self, datafile):
        f = open(datafile, 'r')
        DNAstring = f.read()
        f.close()
        #first, parse each node
        allNodes = DNAstring.split(";")
        for nodey in allNodes:
            #print("nodey is: ",nodey)
            #creating an individual node
            n = nodey.partition(":")
           # print("n is: ", n)
            name = n[0]
            data = n[2].split(",") #each data element is separated by a comma
            layer = data[0]
            delta = data[1]
            connections = {}
            connectionList = data[2].split("#")
            print("connectionList is: ", connectionList)
            for c in connectionList:
                x = c.partition("-")
                name = x[0]
                weight = x[2]
                connections.update({name:weight})
                print("updating connection with ", name, weight)
            #now we have all the data for a node, create a node object
            print("Done with node ", name, " Connections are ", connections)
            n = Node(name, layer, delta, connections)
            self.nodes.update({name:n})
            
    def printNN(self):
        for nodey in self.nodes.values():
            print("Printing node ", nodey.name)
            nodey.printNode()
                


#TODO- 1. write parser for NN DNA
    #  2. write way to generate random NN 
    #  3. write way to mutate NN 
    #  4. simulate NN running
    #
    #
    #
    #
