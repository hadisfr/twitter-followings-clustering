#!/usr/bin/env python3


import json
from sys import stderr
from numpy import Infinity


if __name__ == '__main__':
    (following_count_file_address, data_analyzer_file_address, centrality_methode) = tuple(input().split(" "))
    # centrality_methode = closeness

    with open(following_count_file_address) as file:
        (user_names, followings) = json.loads(file.read())
    user_names = dict((int(key), value) for (key, value) in user_names.items())
    user_ids = dict((value, int(key)) for (key, value) in user_names.items())
    followings = dict((int(key), value) for (key, value) in followings.items())
    with open(data_analyzer_file_address) as file:
        centrality_measure = json.loads(file.read())[1][centrality_methode]
 
    normalized_centrality_measure = {}
    for user_name in centrality_measure:
        if followings[user_ids[user_name]] != 0:
            normalized_centrality_measure[user_name] = centrality_measure[user_name] / followings[user_ids[user_name]]
        else:
            normalized_centrality_measure[user_name] = 0

    normalized_centrality_measure = dict((user_name, normalized_centrality_measure[user_name]) for user_name in sorted(normalized_centrality_measure, key = normalized_centrality_measure.get, reverse = True))

    print(json.dumps(normalized_centrality_measure, indent = 4))
