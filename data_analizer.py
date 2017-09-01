#!/usr/bin/env python3


from collections import defaultdict
import json
import sys
import networkx as nx
import matplotlib.pyplot as plt
from sklearn import cluster

from data_collector import translate_followings_db_ids_to_names


def convert_dict_to_grpah(dictionary):
    graph = nx.DiGraph()
    graph.add_nodes_from(list(dictionary.keys()))
    for i in dictionary:
        for j in dictionary[i]:
            graph.add_edge(i, j)
    return graph


def draw_graph(graph, position, title = "", labels = None, partition_of_node = None):
    if not labels:
        labels = dict((i, i) for i in graph.nodes())
    if not partition_of_node:
        partition_of_node = dict((i, 0) for i in graph.nodes())

    nodes_of_partition = defaultdict(list)

    for node in partition_of_node:
        nodes_of_partition[partition_of_node[node]].append(node)

    for partition in nodes_of_partition:
        color_secret = partition + 2
        color = [color_secret, color_secret * color_secret, color_secret * color_secret * color_secret]
        color = "#" + "0".join([str(i % 10) for i in color]) + "0"
        nx.draw_networkx_nodes(graph, position, nodes_of_partition[partition], 2000, color, alpha = 0.8)
    nx.draw_networkx_edges(graph, position, alpha = 0.5)
    nx.draw_networkx_labels(graph, position, labels, font_size = 5, font_color = [1, 1, 1])
    if title:
        plt.title(title)


if __name__ == '__main__':
    (user_name, users, followings) = json.loads(input())
    users = dict((int(key), users[key]) for key in users.keys())
    followings = dict((int(key), followings[key]) for key in followings.keys())

    # print(translate_followings_db_ids_to_names(followings, users))

    graph = convert_dict_to_grpah(followings)

    # position = nx.spring_layout(graph)
    position = nx.circular_layout(graph)
    draw_graph(graph, position, "@" + user_name, users)
    plt.axis("off")
    # plt.savefig(user_name + ".png")
    plt.show()

    kClusters = 2
    clusterers = {
        "Agglomerative": cluster.AgglomerativeClustering(linkage="ward"),
        "Spectral": cluster.SpectralClustering(n_clusters=kClusters, affinity="precomputed", n_init=200),
        "KMeans": cluster.KMeans(n_clusters=kClusters, n_init=200),
    }
    for (clusterer_name, clusterer) in clusterers.items():
        clusterer.fit([[graph.nodes()[j] in graph.neighbors(graph.nodes()[i]) for j in range(len(graph.nodes()))] for i in range(len(graph.nodes()))])
        draw_graph(graph, position, "@" + user_name + ": " + clusterer_name, users, dict((graph.nodes()[i], clusterer.labels_[i]) for i in range(len(graph.nodes()))))
        plt.axis("off")
        plt.show()

