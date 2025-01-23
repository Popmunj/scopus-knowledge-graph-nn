import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pydeck as pdk


st.set_page_config(layout="wide")
aff = pd.read_csv("csv/aff.csv").set_index("id")
loc = pd.read_csv("csv/loc.csv").set_index("id").drop(columns=["Organization"])
auth_count = pd.read_csv("csv/aff_org.csv").set_index("id").drop(columns=["Organization"])
aff = aff.merge(loc, left_on="id", right_on="id").sort_values(by="Literature", ascending=False)
aff = aff.merge(auth_count, left_on="id", right_on="id")

top = aff.iloc[0:10,:]
top_aff = aff[aff["Organization"].isin(top["Organization"].values)]
melted = top_aff.melt(id_vars='Organization', value_vars=['Literature', 'Author'],
                                                   var_name='Metric', value_name='Count')
coor = pd.read_csv("csv/coor.csv")
aff = aff.merge(coor, left_on="Country", right_on="Country")
orgclass = pd.read_csv("csv/org_class.csv")
orgclass = orgclass.drop_duplicates(subset=["lit_id"])
coauth = pd.read_csv("csv/co_auth.csv").drop_duplicates(subset=["AuthorA", "AuthorB"])


st.header("Affiliation and Author")

    

      
left, right = st.columns([3,7])
with left:
    with st.container(border=True, height=650):
        st.header("Top 10 Affiliated Organizations")
        st.write("This scopus is provided by the CU Office of Academic Resources and thus skewed to Chulalongkorn University")

        fig = px.bar(melted.sort_values(by="Count"), x="Count", y="Organization", barmode="group", color="Metric")
        st.plotly_chart(fig, use_container_width=True)
with right:
    with st.container(border=True, height=650): 
        st.header("Organization Distribution by ASJC Classification")
        st.write("""Top classifications are dominated by Chulalongkorn University, except for **Nuclear and High Energy Physics** which
                  is dominanted by Yerevan Physics Institute
                 """)
        agg = orgclass.groupby(["Organization", "Classification"], as_index=False).size()
        fig = px.treemap(agg, 
                        path=["Classification", "Organization"],
                        values="size",
        
                        )
        st.plotly_chart(fig, use_container_width=True)





with st.container(border=True):
        st.header("Affiliated Organization Map by Literature Count")
        view = pdk.ViewState(
            latitude=15.8700,
            longitude=100.9925,
            zoom=1,
            pitch=0,
        )


        layer = pdk.Layer(
            "ScatterplotLayer",
            data=aff,
            get_position=["Longitude", "Latitude"],
            get_radius=["Literature"],
            get_fill_color=[255, 140, 0, 140],
            radius_scale=1000,
            pickable=True)
        
        r = pdk.Deck(layers=[layer], 
                     initial_view_state=view,
                     tooltip={"text": "{Organization}: {Literature} affiliations"},
                     height=300)
        st.pydeck_chart(r)

with st.container(border=True):
    st.header("Co-authorship Network in Thailand")
    left, right = st.columns([7,3])
    with left:
        st.image("assets/co_auth.png", caption="Network Snapshot (Blue Node as Author and Red Node as Organization)")
    with right:
        st.metric(value=coauth["AuthorA"].unique().shape[0], label="Authors")
        st.metric(value=int(coauth.shape[0] / 2), label="Edges")
        st.metric(value=str(round(coauth.shape[0] / (2 *7309576), 5)*100) + "%", label="Connectedness")
        


    
    

        
