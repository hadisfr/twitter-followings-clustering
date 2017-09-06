#!/usr/bin/env python3


import json
from sys import stderr


def print_result(res, db, clusters, with_respect_to_db = False):
    print("\033[30;107mCluster", end = "\t")
    for key in db.keys():
        print("%s" % (key) + ["\t", ""][len(key) >= 8], end = "\t")
    print("\033[0;49m")
    for i in range(len(res)):
        print("\033[%sm%3d" % (["0", "30;47"][i % 2], i), end = "\t")
        for key in db.keys():
            number = res[i][key]
            number_all = [len(clusters[i]), len(db[key])][with_respect_to_db]
            percentage = number / number_all * 100
            print("%s%3d (%6.2f%%)\033[%sm" % (["", "\033[101;97m"][percentage > 50], number, percentage, ["0", "30;47"][i % 2]), end = "\t")
        print("\033[0;49m")
    print("\033[30;107m", end = "\t")
    for key in db.keys():
        number = all[key]
        number_all = [all_fllowings_count, len(db[key])][with_respect_to_db] 
        percentage = number / number_all * 100
        print("%s%3d (%6.2f%%)\033[30;107m" % (["", "\033[101;97m"][percentage > 50], number, percentage), end = "\t")
    print("\033[0;49m")


if __name__ == '__main__':
    (relations_file_name, clusers_file_name, db_file_name, cluster_name) = tuple(input().split(" "))

    with open(clusers_file_name) as f:
        clusters = json.loads(f.read())[0][cluster_name]
    with open(db_file_name) as f:
        db = json.loads(f.read())
    with open(relations_file_name) as f:
        user_names = json.loads(f.read())[1]
    user_ids = dict((value, key) for (key, value) in user_names.items())

    res = []
    all = dict((key, 0) for key in db.keys())
    all_fllowings_count = sum([len(cluster) for cluster in clusters])
    for cluster in clusters:
        res.append(dict((key, 0) for key in db.keys()))
        for user in cluster:
            for key in db.keys():
                if user_ids[user] in db[key]:
                    res[len(res) - 1][key] += 1
                    all[key] += 1
    
    print_result(res, db, clusters)

