import pandas as pd
import streamlit as st
import plotly.express as px

journalc = pd.read_csv("csv/journal_class.csv").groupby(["Classification", "Journal"], 
                                                        as_index=False).size()
fundc = pd.read_csv("csv/funding_class.csv").groupby(["Classification", "FundingAgency"],
                                                     as_index=False).size()
pubc = pd.read_csv("csv/publisher_class.csv").groupby(["Classification", "Publisher"]
                                                      , as_index=False).size()
nodes = pd.read_csv("csv/nodes.csv").set_index("Entities")

st.header("Journal, Funding Agency, and Publisher")
left, mid, right = st.columns([2,2,2])
with left:
    with st.container(border=True):
        st.metric(value=nodes.loc["Source"],
                  label="Journal")
with mid:
       with st.container(border=True):
        st.metric(value=nodes.loc["FundingAgency"],
                  label="Funding Agency")
with right:
    with st.container(border=True):
        st.metric(value=nodes.loc["Publisher"],
                  label="Publisher")



with st.container(border=True):
  
    ent = st.selectbox(
        "Choose an entity to create a tree map",
        ("Journal", "Funding Agency", "Publisher")
    )
    st.header(f"{ent} Distribution by Classification")
    
    if ent == "Journal":
        fig = px.treemap(
            journalc,
            path=["Classification", "Journal"],
            values="size"
        )
    elif ent == "Funding Agency":
        fig = px.treemap(
            fundc,
            path=["Classification", "FundingAgency"],
            values="size"
        )
    elif ent == "Publisher":
        fig = px.treemap(
            pubc,
            path=["Classification", "Publisher"],
            values="size"
        )


    st.plotly_chart(fig)
