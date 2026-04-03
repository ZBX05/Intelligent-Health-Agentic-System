from py2neo import Graph
import os
from dotenv import load_dotenv

load_dotenv(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/.env")

neo4j_url = os.getenv("NEO4J_BROSWER_URL")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

def correct() -> None:
    graph=Graph(
            host=neo4j_url,
            user=neo4j_username,
            password=neo4j_password
            )
    graph.run("create (n:Anatomy{name:'肾脏'})")
    graph.run("match (n:Disease{name:'糖尿病肾病'}),(m:Anatomy{name:'肾脏'}) create (m)-[rel:Anatomy_Disease]->(n)")
    graph.run("match (n:Drug{name:'D PP-4i'}) detach delete (n)")
    graph.run("match (n:Drug{name:'糖尿病'}) detach delete (n)")
    graph.run("match (n:Test{name:'＜140／80mmHg'}) detach delete (n)")
    graph.run("match (n:Department{name:'肝炎'}) detach delete (n)")
    # print('Done.')

if __name__=='__main__':
    correct()