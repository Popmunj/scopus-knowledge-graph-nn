import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

st.set_page_config(layout="wide")
count_df = pd.read_csv("csv/lit_count_filled.csv")
count_df["Date"] = pd.to_datetime(count_df["Date"])
count_df = count_df.set_index("Date")
nodes = pd.read_csv("csv/nodes.csv")
nodes = nodes.set_index("Entities")
rels = pd.read_csv("csv/rels.csv")
rels = rels.set_index("Relationships")
lits = pd.read_csv("csv/lit_cluster.csv")
elbow = pd.read_csv("csv/elbow.csv")
pca = pd.read_csv("csv/pca.csv")

st.header("Overview")

st.markdown(
    """
    <style>
    

    .css-m9mqwd.esravye1 {
        border: 1px solid #ccc;
        padding: 15px;
        border-radius: 10px;
        background-color: #f9f9f9;
        margin-bottom: 20px;
    
    }

    </style>
    """,
    unsafe_allow_html=True,
)


with st.container():
    left, right = st.columns([2,5])
    with left:
        with st.container(border=True, height=700):
            st.header("About the Scopus")
            st.metric(label="Literature", value=nodes.loc["Literature"].Count)
            st.metric(label="Relations", value=rels["Count"].sum())
            st.write("Learn more about the database")
            with st.expander("Entities (10)"):
                st.table(nodes[~nodes.index.isin(["Abstract", "_Neodash_Dashboard"])])
            with st.expander("Relationships (10)"):
                st.table(rels[~rels.index.isin(["HAS_ABSTRACT"])])
    with right: 
        with st.container(border=True, height=700):
            count_df['Cumulative_Count'] = count_df['Count'].cumsum()
            
            st.header("Literature Count (2018 - 2023)")
            layout = go.Layout(
                    xaxis={"title": "Date"},
                    yaxis={"title": "Count"}
                
                )
            cumsum = st.checkbox("Cumulative", value=True)
            if cumsum:
                trace = go.Scatter(
                    x=count_df.index,
                    y=count_df["Cumulative_Count"],
                    mode='lines',
                    name='Cumulative Count',
                    fill="tozeroy",
                    fillcolor="rgba(173, 216, 230, 0.3)"
                )

            else:
                trace = go.Scatter(
                    x=count_df.index,
                    y=count_df["Count"],
                    mode='lines',
                    name='Count'
                )
        
            fig = go.Figure(data=[trace], layout=layout)
            fig.update_layout(
                autosize=True,  
                margin=dict(l=20, r=20, t=20, b=20),  
        )
            st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):

    left, right = st.columns([6,4])
    with left:
        fig2 = px.scatter_3d(lits, x='AuthorCount', y='ReferenceCount', z='FundingAgencyCount', color='Cluster')
        fig2.update_layout(
            autosize=True,  
            margin=dict(l=0, r=50, t=10, b=10) )
        st.plotly_chart(fig2, use_container_width=True)

        
    with right:
        st.header("Literature Scales")
        st.write("""Using the number of authors, funders, and references as a proxy for the scale of each literature,
                  the literatures can be grouped into **7 groups**
                  """)
        cluster_counts = lits.groupby('Cluster')['ReferenceCount'].count()
        counts = pd.DataFrame(cluster_counts.sort_values(ascending=False)).rename(columns={"ReferenceCount": "Literature"})
        st.write(counts)
        with st.expander("KMeans details and PCA analysis"):
            st.header("The elbow method")
            st.line_chart(elbow.drop(columns=['Unnamed: 0']))

            st.header("The Principal Component Analysis (PCA)")
            st.write("""
            The number of references catgorizes literatures in a different way than
            the numbers of funders and authors do
            """)
            pca_c = lits[["PCA1", "PCA2"]]
            fig = px.scatter(pca_c, x="PCA1", y="PCA2")
            st.plotly_chart(fig, use_container_width=True)
            st.table(pca.set_index("Unnamed: 0"))

with st.container(border=True):
    st.header("The Use of Reference")
    st.write("""
    The number of references can be normalized by the number of funders and authors
             """)
    ref = lits["ReferenceCount"] / (lits["AuthorCount"] + lits["FundingAgencyCount"])
    ref = ref.sort_values(ascending=False)
    fig = px.histogram(ref)

    fig.update_layout(
        xaxis_title="Reference Ratio",
        yaxis_title="Count",
        bargap=0.2,
        margin=dict(l=20, r=20, t=50, b=20),  
        showlegend=False,
        title_text="Reference Ratio Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

    