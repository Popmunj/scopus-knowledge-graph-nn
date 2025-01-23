import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.preprocessing import StandardScaler
import torch
from torch import nn, optim
import numpy as np



st.set_page_config(layout="wide")
nodes = pd.read_csv("csv/nodes.csv").set_index("Entities")
lit_key = pd.read_csv("csv/lit_key.csv")
lit_class = pd.read_csv("csv/lit_class.csv")
key_group = lit_key.groupby("k_name").size()
key_group = pd.DataFrame(key_group).rename(columns={"k_name":"Keyword",
                                                                     0:"Count"})

key_group = key_group.sort_values(by="Count", ascending=False).head(20)
lit_class = pd.DataFrame(lit_class.groupby("Classification").size()).sort_values(
    by="Classification", ascending=False
).rename(columns={0:"Count"}).head(20)


class_date = pd.read_csv("csv/class_date.csv")


lit_auth_fund = pd.read_csv("csv/lit_ref_auth_fund.csv").drop(columns=["ReferenceCount"])
fund_score = lit_auth_fund.assign(FundingScore = lambda x : (x["FundingAgencyCount"]/ x["AuthorCount"])).drop(
    columns=["FundingAgencyCount", "AuthorCount"]
)
example = pd.read_csv("csv/example_ts.csv").set_index("LiteratureID")

st.header("Classification and Keyword")

left, right = st.columns([5,5])
with left:
    with st.container(border=True):
        st.metric(label=" ASJC Classification",
                  value=nodes.loc["Classification"])
        # st.write("Of 2025 literatures, 717 are classed using the ASJC code")
    with st.container(border=True):
        fig = px.bar(lit_class.sort_values(by="Count"),
                     x="Count",
                     y=lit_class.sort_values(by="Count").index,
                     )
        fig.update_layout(
            title="Top Classification Frequency",
            yaxis_title="Classification"
        
        )
        st.plotly_chart(fig, use_container_width=True)
  

       
        
with right:
    with st.container(border=True):
        st.metric(label="Keyword",
                  value=nodes.loc["Keyword"])
        # st.write("Of 2025 literatures, 1638 used keywords")
    with st.container(border=True):
        fig = px.bar(key_group.sort_values(by="Count"), x="Count", y=key_group.sort_values(by="Count").index)
        fig.update_layout(
            title="Top Keyword Frequency",
            yaxis_title="Keyword"
        )
        st.plotly_chart(fig, use_container_width=True)

    


  


        
        