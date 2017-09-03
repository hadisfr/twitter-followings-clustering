#!/usr/bin/env python3

import json
import sys
from collections import defaultdict

if __name__ == '__main__':
    (followings_file_address, clusters_file_address, clustering_methode) = tuple(input().split(" "))

    with open(followings_file_address) as file:
        (user_names, followings) = json.loads(file.read())
    user_names = dict((int(key), value) for (key, value) in user_names.items())
    user_ids = dict((value, int(key)) for (key, value) in user_names.items())
    followings = dict((int(key), value) for (key, value) in followings.items())
    with open(clusters_file_address) as file:
        (clusters) = json.loads(file.read())[clustering_methode]

    sum = 0
    for (user_id, followings_number) in followings.items():
        sum += followings_number
    average_all = sum / len(followings)

    average_by_cluster = []
    for cluster in clusters:
        sum = 0
        for user_name in cluster:
            sum += followings[user_ids[user_name]]
        average_by_cluster.append(sum / len(cluster))

    cat_length = 100
    cats = defaultdict(list)
    for (user_id, followings_number) in followings.items():
        cats[int(followings_number / cat_length) * cat_length].append(user_names[user_id])

    print(json.dumps(dict({"all": average_all, "by_cluster": average_by_cluster, "by_number": dict((key, len(cats[key])) for key in sorted(cats, reverse = True))}), indent = 4))

