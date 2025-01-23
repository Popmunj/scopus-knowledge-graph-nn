from unpacker import unpack_nodes_rels, unpack_abstract
import json
import os
from loguru import logger

logger.add("./log/writer.log")

def read_and_dump(folder):
    path = os.path.join("data", folder)
    if not os.path.isdir(path):
        logger.warning(f"Folder {folder} does not exist.")
        return

    for n, filename in enumerate(os.listdir(path)):
        if n % 50 == 0:
            logger.info(f"Processed {n + 1} files. The last file processed is {filename}.")
        try:
            with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
                json_obj = json.loads(f.read())
                new_node_list, new_rel_list = unpack_nodes_rels(json_obj)
        
            dump_nodes(new_node_list)
            dump_rels(new_rel_list)

        except Exception as e:
            logger.error(f"Error reading and dumping from {filename}: {e}")
            continue

# NOTE: NoneType dict is handled here
def dump_nodes(new_node_list):
    with open("./graph/Nodes.json", "r") as f:
        try:
            d = json.loads(f.read())
        except json.JSONDecodeError:
            d = {}

    with open("./graph/Nodes.json", "w", encoding="utf-8") as f: 
        for new_dict in new_node_list:
            try: # NoneType new_dict
                ent = new_dict["label"]
                if ent in d.keys():
                    existing = [e for e in d[ent]]
                    if new_dict not in existing:
                        d[ent].append(new_dict)
                else:
                    d[ent] = [new_dict]
            except Exception as e:
                raise Exception(f"Error associated with node {new_dict}: {e}")

        json.dump(d, f, indent=4, ensure_ascii=False)

def dump_rels(new_rel_list):
    with open("./graph/Rels.json", "r") as f:
        try:
            d = json.loads(f.read())
        except json.JSONDecodeError:
            d = {}
    
    with open("./graph/Rels.json", "w", encoding="utf-8") as f:
        for new_dict in new_rel_list:
            try:
                ent = new_dict["type"]
                if ent in d.keys():
                    existing = [e for e in d[ent]] 
                    if new_dict not in existing:
                        d[ent].append(new_dict)
                else:
                    d[ent] = [new_dict]
            except Exception as e:
                raise Exception(f"Error associated with relationship {new_dict}: {e}")
        json.dump(d, f, indent=4, ensure_ascii=False)


# read_and_dump("2018A")
# read_and_dump("2018B")
# read_and_dump("2019A")
# read_and_dump("2019B")
# read_and_dump("2020A")
# read_and_dump("2020B")
# read_and_dump("2021A")
# read_and_dump("2021B")    
# read_and_dump("2022A")    
# read_and_dump("2022B") 
# read_and_dump("2023A") 
# read_and_dump("2023B")
