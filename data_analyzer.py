#!/usr/bin/env python3


from collections import defaultdict
import json
import sys
import networkx as nx
import matplotlib.pyplot as plt
from sklearn import cluster

from data_collector import translate_followings_db_ids_to_names

def sort_dict_by_values(dictionary, reverse = False):
    dictionary = dict((value, key) for (key, value) in dictionary.items())
    dictionary = dict((key, dictionary[key]) for key in sorted(dictionary, reverse = reverse))
    dictionary = dict((value, key) for (key, value) in dictionary.items())
    return dictionary


def translate_keys_from_ids_to_names(dictionary, users, reverse = False):
    return dict((users[user_id], dictionary[user_id]) for user_id in sort_dict_by_values(dictionary, reverse))


def convert_dict_to_grpah(dictionary):
    graph = nx.DiGraph()
    graph.add_nodes_from(list(dictionary.keys()))
    for i in dictionary:
        for j in dictionary[i]:
            graph.add_edge(i, j)
    return graph


def draw_graph(graph, position, title = "", labels = None, partition_of_node = None):
    plt.figure()
    plt.axis("off")

    if labels == "auto":
        labels = dict((i, i) for i in graph.nodes())
    if not partition_of_node:
        partition_of_node = dict((i, 0) for i in graph.nodes())

    nodes_of_partition = defaultdict(list)

    for node in partition_of_node:
        nodes_of_partition[partition_of_node[node]].append(node)

    for partition in nodes_of_partition:
        color_array = ["00BFFF", "B22222", "FF1493", "800080", "000080", "ADFF2F", "228B22", "C0C0C0", "556B2F", "FF4500", "FFFF00"]
        if partition < len(color_array):
            color = "#" + color_array[partition]
        else:
            color_secret = partition + 2
            color = [color_secret, color_secret * color_secret, color_secret * color_secret * color_secret]
            color = "#" + "0".join([str(hex(i % 14)[-1]) for i in color]) + "0"
        nx.draw_networkx_nodes(graph, position, nodes_of_partition[partition], 100, color, alpha = 0.8)
    nx.draw_networkx_edges(graph, position, alpha = 0.5, edge_color = "#808080")
    if labels:
        nx.draw_networkx_labels(graph, position, labels, font_size = 5, font_color = [0, 0, 0])
    if title:
        plt.title(title)


def cluster_grpah(graph, kClusters = 2, methode_name = None, show_visualized = True):
    clusters = defaultdict(list)
    clusterers = {
        "Agglomerative": cluster.AgglomerativeClustering(linkage="ward", n_clusters=kClusters),
        "Spectral": cluster.SpectralClustering(n_clusters=kClusters, affinity="precomputed", n_init=200),
        "KMeans": cluster.KMeans(n_clusters=kClusters, n_init=200),
        "Affinity": cluster.affinity_propagation(S=[[graph.nodes()[j] in graph.neighbors(graph.nodes()[i]) for j in range(len(graph.nodes()))] for i in range(len(graph.nodes()))], max_iter=200, damping=0.6)
    }
    for (clusterer_name, clusterer) in clusterers.items():
        if methode_name and clusterer_name != methode_name:
            continue
        if clusterer_name == "Affinity":
            clustering_result = clusterer[1]
        else:
            clusterer.fit([[graph.nodes()[j] in graph.neighbors(graph.nodes()[i]) for j in range(len(graph.nodes()))] for i in range(len(graph.nodes()))])
            clustering_result = clusterer.labels_
        clusters[clusterer_name] = [[users[graph.nodes()[i]] for i in range(len(clustering_result)) if clustering_result[i] == j] for j in range(len(set(clustering_result)))]
        if show_visualized:
            draw_graph(graph, position, "@%s : %s" % (user_name, clusterer_name) + [" (%d)" % kClusters, ""][clusterer_name == "Affinity"], users, dict((graph.nodes()[i], clustering_result[i]) for i in range(len(graph.nodes()))))
            plt.show()
    return clusters


def extract_importanat_users(graph, users, reverse = False, methode_name = None):
    important_users_extractors = {
        "deggree": lambda g: nx.degree_centrality(g),
        "closeness": lambda g: nx.closeness_centrality(g), # indicates that the user listens to how many users' tweets immediatey
        "reverse_closeness": lambda g: nx.closeness_centrality(g.reverse(copy = True)), # indicates that how many users immediatey listen the user's tweets
        "betweenness": lambda g: nx.betweenness_centrality(g)
    }
    important_users = {}
    for important_users_extractor in important_users_extractors:
        if methode_name and important_users_extractor != methode_name:
            continue
        important_users[important_users_extractor] = translate_keys_from_ids_to_names(important_users_extractors[important_users_extractor](graph), users, reverse)
    return important_users


if __name__ == '__main__':
    (user_name, users, followings) = json.loads(input())
    users = dict((int(key), users[key]) for key in users.keys())
    followings = dict((int(key), followings[key]) for key in followings.keys())
    graph = convert_dict_to_grpah(followings)
    position = nx.spring_layout(graph)

    draw_graph(graph, position, "@" + user_name, users)
    # plt.savefig(user_name + ".png")
    plt.show()

    clusters = cluster_grpah(graph, 9, "Spectral", True)
    important_users = extract_importanat_users(graph, users, reverse = True)

    # print(json.dumps(translate_followings_db_ids_to_names(followings, users), indent = 4))
    print(json.dumps((clusters, important_users), indent = 4))
    

