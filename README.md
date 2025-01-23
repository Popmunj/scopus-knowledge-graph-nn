# Knowledge graph of Scopus of the engineering field from the CU Office of Academic Resources (2018 - 2023)
**The constructed knowledge graph has 10 node types and relationships.** This project first performs a simple EDA on the database and trains 2 models: co-authorship prediction graph neural network 
and K-means clustering.
<img width="920" alt="Screenshot 2568-01-23 at 17 03 41" src="https://github.com/user-attachments/assets/ea916610-10d0-4ba1-8bf2-398292dde9c6" />
<img width="262" alt="Screenshot 2568-01-23 at 17 02 29" src="https://github.com/user-attachments/assets/b4e9c071-3ea7-4204-aba8-ade78825639b" />
<img width="257" alt="Screenshot 2568-01-23 at 17 02 34" src="https://github.com/user-attachments/assets/cc1f352e-1ad2-4434-9722-6f9686b2ab3d" />


# Quickstart
Set up a virtual environment (for convenience) and run:
```bash
pip install -r requirements.txt
```

A single example of the raw data is in the ```data/sample``` directory. The full preprocessed data (using functions from ```preprocessing```) is in the ```graph``` directory.
To inject the data to own Neo4j instance, run ```persist_nodes``` and ```persist_rels``` in ```ingestion.py```. Run other functions if neeeded.

The environment variables should look like:
```bash
NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
AURA_INSTANCEID=
AURA_INSTANCENAME=
AURA_DS=true
OPENAI_API_KEY=
# (optional) for tracing
LANGCHAIN_TRACING_V2=
LANGCHAIN_ENDPOINT=
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=

```


# EDA
To see the dashboard, 
```bash
cd dashboard
streamlit run About.py
```

# Co-authorship (link) prediction
The model passes features through edges to obtain nodes' embeddings and performs a dot product between author nodes. The training of models can be found in the 
```train``` directory.
![Author](https://github.com/user-attachments/assets/760825ef-fcfc-48de-85a2-02e3748fcee1)


