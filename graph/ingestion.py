from neo4j import GraphDatabase
import json
import os
from loguru import logger
from dotenv import load_dotenv
import re

load_dotenv()
logger.add("log/ingestion.log")

def execute_query(query: str,
                  params: dict):
    url = os.getenv("NEO4J_URL")
    usr = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")
        
    with GraphDatabase.driver(url, auth=(usr, pwd)) as driver:
        try:
            recs, summary, keys = driver.execute_query(query, params=params)
            return recs, summary, keys
        except Exception as e :
            logger.error(e)

def persist_nodes(label: str):
    with open("graph/Nodes.json", "r", encoding="utf-8") as f:
        nodes = json.loads(f.read())

    ents = nodes.get(label)
    for ent in ents:
        ent.pop("label")
    
    params = {}
    params["props"] = ents # array of maps

    if label == "Literature":
        for ent in ents:
            try:
                ent["publication_day"] = int(ent["publication_date"])
            except:
                pass
            try:
                ent["publication_month"] = int(ent["publication_month"])
            except:
                pass
            try:
                ent["publication_year"] = int(ent["publication_year"])
            except:
                pass
            ent.pop("publication_date")


        query = f"""
        UNWIND $props AS map
        MERGE (n: {label} {{id: map.id}})
        SET n = map
        SET n.approx_publication_date = date({{year: map.publication_year, month: map.publication_month, day: map.publication_day}})
        """
    else:
        if label == "Keyword":
            for ent in ents:
                ent["id"] = ent["id"].lower()

        query = f"""
        UNWIND $props as map
        MERGE (n: {label} {{id: map.id}})
        SET n = map
        """
    return execute_query(query, params)

def persist_rels(type: str):
    with open("graph/Rels.json", "r", encoding="utf-8") as f:
        rels = json.loads(f.read())
    
    ents = rels.get(type)
    for ent in ents: 
        start = ent["start"]["label"]
        end = ent["end"]["label"]
        ent["start_id"] = ent["start"]["id"]
        ent["end_id"] = ent["end"]["id"]
        ent.pop("start")
        ent.pop("end")
    
    if type == "USED_KEYWORD":
        for ent in ents:
            ent["start_id"] = ent["start_id"].lower()
            ent["end_id"] = ent["end_id"].lower()

    params = {}
    params["rels"] = ents

    # TODO: add labels
    query = f""" 
    UNWIND $rels as rel
    MATCH (a:{start} {{id:rel.start_id}})
    MATCH (b:{end} {{id:rel.end_id}})
    MERGE (a)-[r:{type}]->(b)
    """

    execute_query(query, params)


# create embeddings
def persist_embeddings(node, prop): 
    url = os.getenv("NEO4J_URL")
    usr = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(url, auth=(usr, pwd))
    
    batch_size = 100
    batch_n = 1
    batch = []

    with driver.session() as session:
        # fetch 
        result = session.run(f'MATCH (n:{node}) WHERE n.embedding IS NULL RETURN n.{prop} AS text, n.id AS id')
        for record in result:
            id = record.get("id")
            text = record.get("text")

            if id is not None and text is not None:
                batch.append({
                    "id": id,
                    "to_encode": text
                })
            
            if len(batch) == batch_size:
                import_batch(driver, node, batch, batch_n)
                batch = []
                batch_n += 1     


def import_batch(driver, node, batch, batch_n):
    tk = os.getenv("OPENAI_API_KEY")

    recs, summary, keys = driver.execute_query(f"""
    CALL genai.vector.encodeBatch($to_encode_list, 'OpenAI', {{token: $token}}) YIELD index, vector
    MATCH (n:{node} {{id:$batch[index].id}})
    CALL db.create.setNodeVectorProperty(n, 'embedding', vector)             
    """, batch=batch, to_encode_list=[en["to_encode"] for en in batch], token=tk)
    # logger.info(f"Nodes matched: {summary.counters.properties_set}")
    logger.info(f"Batch {batch_n} processed")


# create vector index
def create_index(node, name):
    q = f"""
    CREATE VECTOR INDEX {name}
    FOR (n:{node})
    ON n.embedding
    OPTIONS {{indexConfig: {{
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
    }}}}
    """
    execute_query(q, {})

def delete_null():
    q = """
    MATCH (n:Abstract) 
    WHERE n.content IS NULL
    DETACH DELETE n;
    """
    execute_query(q, {})

# in case a Literature references another Literature in the database
def lit_ref():
    query = f"""
    MATCH (source)-[rel]->(r:Reference)
    MATCH (l:Literature {{id: r.id}})
    WITH r, l, rel, source
    CREATE (source)-[newRel:type(rel)]->(l)
    DELETE rel
    WITH r
    DETACH DELETE r
    """

    execute_query(query, {})

# create co-authorship in Thailand
def create_co_auth():
    query = """
    MATCH (:Country {name:'Thailand'})<-[]-()<-[]-(a1:Author)-[]->(:Literature)<-[]-(a2:Author)-[]->()-[]->(:Country {name:'Thailand'})
    WHERE a1.id <> a2.id
    MERGE (a1)-[r:CO_AUTHORED]->(a2)
    """

    execute_query(query, {})

# remove HAS_ABSTRACT 
def clear_abstract():
    query = """
    MATCH (l:Literature)-[:HAS_ABSTRACT]->(a:Abstract) 
    SET l.abstract = a.content
    SET l.embedding = a.embedding
    DETACH DELETE (a)
    """
    execute_query(query, {})
    clear = """
    MATCH (a:Abstract) 
    DETACH DELETE (a)
    """
    execute_query(clear, {})

