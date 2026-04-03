from py2neo import Graph
import random

def get_graph(graph:list|Graph) -> Graph:
    if(isinstance(graph,Graph)):
        return graph
    elif(isinstance(graph,list)):
        return graph[random.randint(0,len(graph)-1)]
    else:
        raise TypeError