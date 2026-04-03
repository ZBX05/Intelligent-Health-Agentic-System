import os
import json
from py2neo import Graph,Node
from dotenv import load_dotenv

load_dotenv("./.env")
neo4j_url = os.getenv("NEO4J_BROSWER_URL")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

def create_node(graph:Graph,label:str,nodes:set) -> None:
    count=0
    for node_name in nodes:
        node=Node(label,name=node_name)
        graph.create(node)
        count+=1
        print(count)

def create_disease_node(graph:Graph,label:str,nodes:list) -> None:
    count=0
    for node_name in nodes:
        node=Node(label,name=node_name,reason=[]
                    ,infectivity=[],period=[])
        graph.create(node)
        count+=1
        print(count)

def create_relationship(graph:Graph,start_node:str,end_node:str,edges:list,rel_type:str,rel_name:str) -> None:
    count=0
    # 去重处理
    set_edges=[]
    for edge in edges:
        set_edges.append("###".join(edge))
    all=len(set(set_edges))
    for edge in set(set_edges):
        edge = edge.split("###")
        p=edge[0]
        q=edge[1]
        query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
            start_node, end_node, p, q, rel_type, rel_name)
        try:
            graph.run(query)
            count += 1
            print(rel_type,count,all)
        except Exception as e:
            print(e)

def addSportGraph(graph:Graph,knowledge_data_dir:str,txt_dir:str) -> bool:
    with open(knowledge_data_dir,"r",encoding="utf-8",errors="ignore") as fp:
        data=json.load(fp)
    disease=data["entity"]["disease"]
    sport=data["entity"]["sport"]
    sport_suitable_diseases=data["relation"]["Sport_Suitable_Disease"]

    if len(disease):
        create_disease_node(graph,"Disease",disease)
        f_disease=open(os.getcwd()+"/txt/disease.txt", "w+",encoding="utf-8")
        f_disease.write("\n".join(list(disease)))
        f_disease.close()
        print("Disease:",len(disease))

    if len(sport):
        create_node(graph,"Sport",sport)
        f_sport=open(os.getcwd()+"/txt/sport.txt", "w+",encoding="utf-8")
        f_sport.write("\n".join(list(sport)))
        f_sport.close()
        print("Sport:",len(sport))

    if len(sport_suitable_diseases):
        create_relationship(graph,"Sport","Disease",sport_suitable_diseases,"Sport_Suitable_Disease","疾病适合的运动")

    return True

if __name__=="__main__":
    if(addSportGraph(Graph(host=neo4j_url, user=neo4j_username, password=neo4j_password),
                     os.getcwd()+"/data/extractedData/extracted_sport.json",
                     os.getcwd()+"/txt/sport.txt")):
        print("Done.")