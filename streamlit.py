import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from collections import Counter
import plotly.graph_objects as go
import networkx as nx
from community import community_louvain

df = pd.read_csv('final_data.csv')

tab1 , tab2 = st.tabs(["Chula Scopus","Arxiv Author Network Graph"])

# Visualization 1: Keyword Frequency Distribution

with tab1:
    st.write("## Keyword Frequency Distribution")

    keywords = df['keywords'].apply(eval).explode()  # Convert strings to lists and flatten
    keyword_counts = Counter(keywords)

    # Prepare data for visualization
    top_keywords = keyword_counts.most_common(20)  # Top 20 keywords
    keywords, counts = zip(*top_keywords)

    # Create a DataFrame for Plotly
    plot_df = pd.DataFrame({"Keyword": keywords, "Frequency": counts})

    # Plot with Plotly
    fig = px.bar(
        plot_df,
        x="Frequency",
        y="Keyword",
        orientation="h",
        title="Top 20 Keywords by Frequency",
        color="Frequency",
        color_continuous_scale="Blues"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))  # Reverse order for horizontal bar

    # Display Plot
    st.plotly_chart(fig)

    # Visualization 2: Publications Over Time
    st.write("## Publications Over Time")
    publication_count = df['publication_year'].value_counts().reset_index()
    publication_count.columns = ['Year', 'Count']
    publication_count = publication_count.sort_values('Year')

    fig2 = px.line(publication_count, x='Year', y='Count', title='Number of Publications Per Year')
    st.plotly_chart(fig2)

    # Visualization 3: Keywords Trend by year
    df['keywords'] = df['keywords'].apply(eval)  # Convert strings to lists
    keywords_data = df.explode('keywords')  # Each keyword in its own row

    # Count keyword occurrences by year
    keyword_trends = keywords_data.groupby(['publication_year', 'keywords']).size().reset_index(name='count')

    # Filter top keywords for better visualization
    top_keywords = keyword_trends.groupby('keywords')['count'].sum().nlargest(10).index
    filtered_trends = keyword_trends[keyword_trends['keywords'].isin(top_keywords)]

    # Plot trends
    fig = px.area(
        filtered_trends,
        x='publication_year',
        y='count',
        color='keywords',
        title='Keyword Trends Over Time',
        labels={'count': 'Occurrences', 'publication_year': 'Year', 'keywords': 'Keyword'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Display the Plot
    st.plotly_chart(fig)

with tab2 :
    st.title("Arxiv Data")

    data = pd.read_csv('arxiv_articles.csv')

    def create_author_network_from_df(df):
        G = nx.Graph()
        for _, row in df.iterrows():
            authors = row["authors"]
            if not isinstance(authors, list):
                raise ValueError(f"Expected list of authors, got {type(authors)}: {authors}")
            
            for i, author1 in enumerate(authors):
                for author2 in authors[i + 1:]:
                    if G.has_edge(author1, author2):
                        G[author1][author2]['weight'] += 1
                    else:
                        G.add_edge(author1, author2, weight=1)
        return G

    def detect_communities(G):
        partition = community_louvain.best_partition(G)  # Detect communities
        nx.set_node_attributes(G, partition, "community")  # Set community attribute for each node
        return partition

    # Draw Graph with Plotly (including community coloring)
    def draw_graph(G, layout_algo="kamada_kawai", detect_community=True):
        layout_func = getattr(nx, layout_algo + "_layout", nx.spring_layout)
        pos = layout_func(G)

        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color="#888"), hoverinfo="none", mode="lines")

        node_x, node_y, node_color, text = [], [], [], []
        if detect_community:
            partition = nx.get_node_attributes(G, "community")  # Get community assignments
            # Color nodes based on their community
            node_color = [partition.get(node, 0) for node in G.nodes()]
        else:
            node_color = [0] * len(G.nodes())  # Default color if no community detection

        for node, data in G.nodes(data=True):
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            text.append(f"Author: {node}")
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode="markers", hoverinfo="text",
            marker=dict(size=10, color=node_color, colorscale="Viridis", showscale=True),
            text=text
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        return fig

    def create_community_table(partition):
        community_counts = {}
        for author, community in partition.items():
            community_counts[community] = community_counts.get(community, 0) + 1
        community_data = [{"Community": community, "Author Count": count} for community, count in community_counts.items()]
        return pd.DataFrame(community_data)


    # Streamlit App
    layout_algo = st.sidebar.selectbox("Select Layout Algorithm", ["kamada_kawai", "spring", "circular", "shell"])
    detect_community = st.sidebar.checkbox("Detect Communities", value=True)

    # Create Graph
    data['authors'] = data['authors'].apply(eval)
    G = create_author_network_from_df(data)

    # Detect Communities
    partition = detect_communities(G)

    # Display Graph
    st.plotly_chart(draw_graph(G, layout_algo))

    community_df = create_community_table(partition)
    if detect_community:
        partition = detect_communities(G)
        # Create and Display Community Summary Table
        community_df = create_community_table(partition)
        st.subheader("Community Summary")
        st.dataframe(community_df)



