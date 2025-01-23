import json
import pandas as pd
from loguru import logger
import requests
from dotenv import load_dotenv
import os
import re
from scraper import get_citation

load_dotenv()
logger.add("./log/unpacker.log")
def unpack_literature(json_obj):
    try: 
        ab_data = json_obj["abstracts-retrieval-response"]
    
        core = ab_data["coredata"] 
        id, title  = core["dc:identifier"], core["dc:title"]
        id = id.split(":")[1]

        xml, open_access = core["prism:url"], core["openaccess"]

        source = ab_data["item"]["bibrecord"]["head"]["source"]
        pubdate = source["publicationdate"]
        d, m, y = pubdate.get("day", None), pubdate.get("month", None), \
                pubdate.get("year", None)
      

        return {
            "label": "Literature",
            "id": id, 
            "title": title,
            "open_access": open_access,
            "publication_date": d,
            "publication_month": m,
            "publication_year": y
        }
    except Exception as e:
        logger.error(f"Error unpacking Literature: {e}") 

def unpack_source(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        source = ab_data["item"]["bibrecord"]["head"]["source"]
       
        return ({
            "label": "Source",
            "id": source["@srcid"],
            "name": source["sourcetitle"],

        }, {"type": "FROM", 
            "start": {
            "label": "Literature",
            "id":  ab_data["coredata"]["dc:identifier"].split(":")[1]},
            "end" : {
            "label": "Source",
            "id": source["@srcid"]
            }
        })
    except Exception as e:
        logger.error(f"Error unpacking Source: {e}") 

def unpack_abstract(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        abstract = ab_data["item"]["bibrecord"]["head"]["abstracts"]
        return ({
            "label": "Abstract",
            "id": "abstract" + ab_data["coredata"]["dc:identifier"].split(":")[1],
            "content": abstract
        }, {
            "type": "HAS_ABSTRACT",
            "start": {
                "label": "Literature",
                "id": ab_data["coredata"]["dc:identifier"].split(":")[1]
            },
            "end": {
                "label": "Abstract",
                "id": "abstract" + ab_data["coredata"]["dc:identifier"].split(":")[1]
            }
        })

    except Exception as e:
        logger.error(f"Error unpacking Abstract: {e}") 

def unpack_funding_agency(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        item = ab_data["item"]

        node_list= []
        rel_list = []

        funding_list = item.get("xocs:meta", {}).get("xocs:funding-list", {}).get("xocs:funding", [])
        if len(funding_list) == 0:
            return [], []
        elif type(funding_list) == dict:
            funding_list = [funding_list]
            
        for funder in funding_list:
            id = funder.get("xocs:funding-agency-id", None)
            id = id.split("/")[-1] if id else funder["xocs:funding-agency-matched-string"]
            id = re.sub(r"[:,&(+).\/‘¸¡–™'-]", "", id).replace(" ", "").replace("’", "")

            node_list.append({
                "label": "FundingAgency",
                "id": id,
                "name": funder.get("xocs:funding-agency-matched-string", None)
            })

            rel_list.append({
                "type": "FUNDED",
                "start" : {
                    "label": "FundingAgency",
                    "id": id,
                },
                "end" : {
                    "label": "Literature",
                    "id": ab_data["coredata"]["dc:identifier"].split(":")[1],
                }
            })
        
        return (node_list, rel_list)
            
    except Exception as e:
        logger.error(f"Error unpacking FundingAgency: {e}")

def unpack_author(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        author_list = ab_data["authors"]["author"]
        node_list = []
        rel_list = []
        for author in author_list:
            node_list.append({
                "label": "Author",
                "id": author["@auid"],
                "first_name": author["preferred-name"]["ce:given-name"],
                "last_name": author["preferred-name"]["ce:surname"]
                
            })

            rel_list.append({
                "type": "AUTHORED",
                "start": {
                    "label": "Author",
                    "id": author["@auid"]
                },
                "end": {
                    "label": "Literature",
                    "id": ab_data["coredata"]["dc:identifier"].split(":")[1]
                }
            })

            affs = author.get("affiliation", None)
            if affs:
                if type(affs) == dict:
                    affs = [affs]
                for aff in affs:
                    rel_list.append({
                        "type": "AFFILIATED_WITH",
                        "start": {
                            "label": "Author",
                            "id": author["@auid"]
                        },
                        "end": {
                            "label": "Organization",
                            "id": aff["@id"]
                        }
                    }) 

        return (node_list, rel_list)
    except Exception as e:
        logger.error(f"Error unpacking Author: {e}")


def unpack_organization(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        node_list, rel_list = [], []

        afils = ab_data["affiliation"]
        if type(afils) == dict:
            afils = [afils]

        for a in afils:
            node_list.append(
                {
                    "label": "Organization",
                    "id": a["@id"],
                    "name": a["affilname"]
                }
            )
            country = a.get("affiliation-country", None)
            if country:
                node_list.append({
                    "label": "Country",
                    "id": reformat(country),
                    "name": country
                })
                rel_list.append({
                    "type": "LOCATED_IN",
                    "start": {
                        "label": "Organization",
                        "id": a["@id"]
                    },
                    "end": {
                        "label": "Country",
                        "id": reformat(country)
                    }
                })

        return (node_list, rel_list)
    except Exception as e:
        logger.error(f"Error unpacking organization: {e}")

def unpack_keyword(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        keywords = ab_data.get("authkeywords", {})
       
        if keywords == None:
            return [], []  
        keywords = keywords.get("author-keyword", None)
        
        node_list = []
        rel_list = []
        if type(keywords) == dict:
            keywords = [keywords]
        
        for keyword in keywords:
            id = re.sub(r"[,&().\‘¸¡–™'-]", "", keyword["$"]).replace(" ", "").replace("’", "")

            node_list.append({
                "label": "Keyword",
                "id": id,
                "name": keyword["$"]
            })
            rel_list.append({
                "type": "USED_KEYWORD",
                "start": {
                    "label": "Literature",
                    "id": ab_data["coredata"]["dc:identifier"].split(":")[1]
                },
                "end": {
                    "label": "Keyword",
                    "id": id
                }
            })
        
        return (node_list, rel_list)
    except Exception as e:
        logger.error(f"Error unpacking Keyword: {e}")

def unpack_publisher(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        pub = ab_data["item"]["bibrecord"]["head"]["source"]["publisher"]
        name = pub["publishername"]
        return ({"label": "Publisher",
                 "id": name.replace(" ", ""),
                 "name": name
                 }, 
                 {
                    "type": "PUBLISHED",
                    "start" : {
                        "label": "Publisher",
                        "id": name.replace(" ", "")
                    }, "end": {
                        "label": "Literature",
                        "id": ab_data["coredata"]["dc:identifier"].split(":")[1]
                    }
                 })
    except Exception as e:
        logger.error(f"Error unpacking Publisher: {e}")


def unpack_ref(json_obj):
    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        tail = ab_data["item"]["bibrecord"]["tail"]
        if not tail:
            return [], [] 

        refs = tail["bibliography"]["reference"]
        if type(refs) == dict:
            refs = [refs]

        node_list = []
        rel_list = []
        for ref_dict in refs:
     
            ref = ref_dict["ref-info"]
            ents = ref["refd-itemidlist"]["itemid"]
            if type(ents) == dict:
                ents = [ents]

            for ent in ents:
                if ent["@idtype"] == "SGR":
                    id = ent["$"]

            node_list.append({
                "label": "Reference",
                "id": id,
                "title": ref_dict.get("ref-fulltext", None)
            })

            rel_list.append({
                "type": "REFERENCED",
                "start": {
                    "label": "Literature",
                    "id": ab_data["coredata"]["dc:identifier"].split(":")[1]
                },
                "end": {
                    "label": "Reference",
                    "id": id
                }
            })

        return (node_list, rel_list)
    except Exception as e:
        logger.error(f"Error unpacking Reference: {e}")

# NOTE: ASJC type
def unpack_class(json_obj):
    df = pd.read_csv("./addition/ASJC.csv")
    df = df.drop(columns=["CodeSystem"])

    try:
        ab_data = json_obj["abstracts-retrieval-response"]
        class_types = ab_data["item"]["bibrecord"]["head"]["enhancement"]["classificationgroup"]["classifications"]

        if type(class_types) == dict:
            class_types = [class_types]
        
        node_list = []
        rel_list = []
        for t in class_types:
            if t["@type"] == "ASJC":
                classifications = t["classification"]

                if type(classifications) == dict:
                    classifications = [classifications]

                if type(classifications) == str:
                    node_list.append({
                        "label": "Classification",
                        "id": classifications,
                        "name": df[df["Code"] == int(classifications)]["Description"].values[0]
                    })
                    rel_list.append({
                        "type": "IS_CLASSED",
                        "start": {
                            "label": "Literature",
                            "id": ab_data["coredata"]["dc:identifier"].split(":")[1]
                        },
                        "end": {
                            "label": "Classification",
                            "id": classifications
                        }
                    })
                    return (node_list, rel_list)

                for classification in classifications:
                    node_list.append({
                        "label": "Classification",
                        "id": classification["$"],
                        "name": df[df["Code"] == int(classification["$"])]["Description"].values[0]
                    })
                    rel_list.append({
                        "type": "IS_CLASSIFIED",
                        "start": {
                            "label": "Literature",
                            "id": ab_data["coredata"]["dc:identifier"].split(":")[1]
                        },
                        "end": {
                            "label": "Classification",
                            "id": classification["$"]
                        }
                    })

                break

        return (node_list, rel_list)
    except Exception as e:
        logger.error(f"Error unpacking Class: {e}")

def unpack_nodes_rels(json_obj):
    try:
        literature = unpack_literature(json_obj)
        source, rel_from = unpack_source(json_obj)
        abstract, rel_abstract = unpack_abstract(json_obj)
        node_list = [literature, source, abstract]
        rel_list = [rel_from, rel_abstract]

        funder_list, rel_funded_list = unpack_funding_agency(json_obj)
        for funder in funder_list:
            node_list.append(funder)
        for rel_funded in rel_funded_list:
            rel_list.append(rel_funded)

        author_list, rel_authored_list = unpack_author(json_obj)
        for author in author_list:
            node_list.append(author)
        for rel_authored in rel_authored_list:
            rel_list.append(rel_authored)

        org_list, rel_multiple_list = unpack_organization(json_obj)
        for org in org_list:
            node_list.append(org)
        for rel_multiple in rel_multiple_list:
            rel_list.append(rel_multiple)
        
        keyword_list, rel_keyword_list = unpack_keyword(json_obj)
        for keyword in keyword_list:
            node_list.append(keyword)
        for rel_keyword in rel_keyword_list:
            rel_list.append(rel_keyword)

        publisher, rel_published = unpack_publisher(json_obj)
        node_list.append(publisher)
        rel_list.append(rel_published)

        ref_list, rel_ref_list = unpack_ref(json_obj)
        for ref in ref_list:
            node_list.append(ref)
        for rel_ref in rel_ref_list:
            rel_list.append(rel_ref)

        class_list, rel_class_list = unpack_class(json_obj)
        for class_ in class_list:
            node_list.append(class_)
        for rel_class in rel_class_list:
            rel_list.append(rel_class)

        return (node_list, rel_list)

    except Exception as e:
        logger.error(f"Error unpacking nodes and rels: {e}")

def elsevier_api(name):
    api_url = "https://api.elsevier.com/content/search/scopus"
    params = {
        'query': f"fund-sponsor({name})",
        'apiKey': os.getenv("ELS")
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        logger.error("Server error")
        return None

def reformat(name):
    return re.sub(r"[:,&(+).\/‘¸¡–™'-]", "", name).replace(" ", "").replace("’", "")