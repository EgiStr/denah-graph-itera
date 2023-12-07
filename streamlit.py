
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import math
import pandas as pd


def calculate_distance_between_lat_lon(G, node1, node2):
    # get the lat lon of the nodes
    lat1 = G.nodes[node1]["lat"]
    lon1 = G.nodes[node1]["lon"]
    lat2 = G.nodes[node2]["lat"]
    lon2 = G.nodes[node2]["lon"]
    # calculate the distance
    distance = distance_lat_lon(lat1, lon1, lat2, lon2)
    return distance


def distance_lat_lon(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km with the haversine formula

    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    R = 6373.0
    # convert to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    # change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    # haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    # c is the central angle
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # distance is the radius times the central angle
    distance = R * c
    # get .f2
    distance = float("{:.4f}".format(distance))

    return distance

# cahce function
@st.cache_data()
def load_data():
    # create graph object that contain vertex and value lat lon
    G = nx.Graph()

    # read the data from csv file

    df = pd.read_excel("./data/datavertex.xlsx")
    # get lat lon from data cordinate
    df["lat"] = df["cordinate"].apply(lambda x: x.split(",")[0])
    df["lon"] = df["cordinate"].apply(lambda x: x.split(",")[1])
    # # add node to graph
    for i in range(len(df)):
        G.add_node(df["node"][i], lat=df["lat"][i], lon=df["lon"][i])

    # read the data from csv file
    df = pd.read_excel("./data/edges.xlsx")
    # add edge to graph
    for i in range(len(df)):
        G.add_edge(
            df["vertek"][i],
            df["to"][i],
            weight=calculate_distance_between_lat_lon(
                G, df["vertek"][i], df["to"][i]
            ),
        )

    return G


def visualize_graph(G):
    # get the edges with the highest weight
    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
    # get the edges with the lowest weight
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]
    # create figure
    fig = plt.figure(figsize=(20, 20))
    # create layout
    pos = nx.spring_layout(G, seed=0,scale=3, threshold=0.001,iterations=3000, k=0.14, weight=1.)
    # draw nodes
    color_map = []
    # with gredy coloring

    gredy_coloring = nx.greedy_color(G, strategy="largest_first")
    for node in G:
        color_map.append(gredy_coloring[node])

    # draw nodes with color_map
    nx.draw_networkx_nodes(G, pos, node_size=180, node_color=color_map)
    # draw edges
    # node labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif",font_color="black")
    # draw edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=1)
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=1, alpha=0.5, edge_color="b", style="dashed"
    )

    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels,verticalalignment="bottom",horizontalalignment="center",font_size=6,font_color="black")
    # create figure
    fig = plt.figure(figsize=(20, 20))
    # input the graph data to figure and set the figure size
    nx.draw(G,pos=pos, with_labels=True, node_size=180, node_color=color_map)
    # set the axis off
    plt.axis("off")
    # show the graph
    st.pyplot()



def find_shortest_path(G, source_node, target_node):
    # find the shortest path from Gerbang Utama to Gerbang Barat
    path = nx.dijkstra_path(G, source=source_node, target=target_node)
    # get weight of the path and sum it
    sum_weight = 0
    for i in range(len(path) - 1):
        sum_weight += G[path[i]][path[i + 1]]["weight"]

    return path, sum_weight

def visualize_shortest_path(G,path):
    pos = nx.spring_layout(G, seed=0,scale=3, threshold=0.001,iterations=3000, k=0.14, weight=1.)
    # draw nodes
    color_map = []
    # with gredy coloring

    gredy_coloring = nx.greedy_color(G, strategy="largest_first")
    for node in G:
        color_map.append(gredy_coloring[node])

    # get the edges with the highest weight
    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
    # get the edges with the lowest weight
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]

    # draw nodes with color_map
    nx.draw_networkx_nodes(G, pos, node_size=180, node_color=color_map)

    # labels weight of edges (distance) 
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=1)
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=1
    )

    # node labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)



    # find the shortest path from Gerbang Utama to Gerbang Barat
    

    # draw the shortest path from Gerbang Utama to Gerbang Barat with red color
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color="r", node_size=100)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="r", width=2)

    # set the axis off
    plt.axis("off")
    # show the graph
    st.pyplot()
    

# cache function
def main():
    # setting app
    st.set_page_config(layout="wide", page_title="Jalur Terpendek Itera", page_icon="📊",)
    st.set_option('deprecation.showPyplotGlobalUse', False)
    # load the data
    # title of the app
    st.title("Denah Kampus ITERA")
    # load images of iteras
    st.image("./images/denahitera.png")
    # write description
    st.write(
        """
        Aplikasi ini digunakan untuk mencari jalur terpendek dari suatu titik ke titik lain di kampus ITERA.
        """
    )
    # berikan tanda berubah dari denah ke graf
    st.write("Berikut adalah graf dari denah kampus ITERA")
    # load the data
    # cache function
    
    G = load_data()
    # create sidebar
    st.sidebar.title("Jalur Terpendek Itera")
    # create dropdown for source node
    source_node = st.sidebar.selectbox(
        "Pilih node asal", list(G.nodes()), index=0
    )
    # create dropdown for target node
    target_node = st.sidebar.selectbox(
        "Pilih node tujuan", list(G.nodes()), index=1
    )
    # create button to find the shortest path

    if st.sidebar.button("Cari Jalur Terpendek"):
        # find the shortest path
        path, sum_weight = find_shortest_path(G, source_node, target_node)

        # if path is empty then there is no path
        if len(path) == 0:
            st.sidebar.write("Tidak ada jalur yang tersedia")
        else:  
            # visualize the shortest path
            visualize_shortest_path(G, path)
            # show the shortest path
            for i in range(len(path)):
                if i == len(path) - 1:
                    st.sidebar.write(path[i])
                else:
                    st.sidebar.write(f"{path[i]} -> ")
                    
            st.sidebar.write("Jarak Terpendek: ", sum_weight, "km")

    else:
        visualize_graph(G)
    
    
main()