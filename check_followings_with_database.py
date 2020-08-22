#!/usr/bin/env python3


import json


def print_header_row_content(kwargs):
    print("%s" % (kwargs["key"]) + ["\t", ""][len(kwargs["key"]) >= 8], end="\t")


def print_nonheader_row_content(kwargs):
    number = kwargs["numbers"][kwargs["key"]]
    percentage = number / kwargs["number_all"] * 100
    print("%s%3d (%6.2f%%)\033[%sm" % (["", "\033[101;97m"][percentage > kwargs["percentage_cutoff"]], number,
                                       percentage, ["0", "30;47", "30;107"][kwargs["row_color_code"]]), end="\t")


def print_row(keys, content_printer, row_header="", **kwargs):
    print("\033[%sm%3s" % (["0", "30;47", "30;107"][kwargs["row_color_code"]], row_header), end="\t")
    for key in keys:
        kwargs["key"] = key
        content_printer(kwargs=kwargs)
    print("\033[0;49m")


def print_result(res, db, clusters, user_name, with_respect_to_db=False, percentage_cutoff=50):
    print("\033[1m@%s\033[0m" % user_name)
    print_row(db.keys(), print_header_row_content, row_color_code=2, row_header="Cluster")
    for i in range(len(res)):
        print_row(keys=db.keys(), numbers=res[i], number_all=[len(clusters[i]), len(db[key])][with_respect_to_db],
                  row_color_code=i % 2, percentage_cutoff=percentage_cutoff, row_header=i,
                  content_printer=print_nonheader_row_content)
    print_row(keys=db.keys(), numbers=all, number_all=[all_fllowings_count, len(db[key])][with_respect_to_db],
              row_color_code=2, percentage_cutoff=percentage_cutoff, content_printer=print_nonheader_row_content,
              row_header="all")


def read_all_jsons(relations_file_name, clusers_file_name, db_file_name, cluster_name):
    with open(clusers_file_name) as f:
        clusters = json.loads(f.read())[0][cluster_name]
    with open(db_file_name) as f:
        db = json.loads(f.read())
    db = dict((key, [int(i) for i in value]) for (key, value) in db.items())
    with open(relations_file_name) as f:
        user_name, user_names = json.loads(f.read())[0:2]
    user_names = dict((int(key), value) for (key, value) in user_names.items())
    user_ids = dict((value, key) for (key, value) in user_names.items())

    return (user_names, user_ids, clusters, db, user_name)


if __name__ == '__main__':
    (user_names, user_ids, clusters, db, user_name) = read_all_jsons(*tuple(input().split(" ")))

    res = []
    all = dict((key, 0) for key in db.keys())
    all_fllowings_count = sum([len(cluster) for cluster in clusters])
    for cluster in clusters:
        res.append(dict((key, 0) for key in db.keys()))
        for user in cluster:
            for key in db.keys():
                if (user_ids[user]) in db[key]:
                    res[len(res) - 1][key] += 1
                    all[key] += 1
    print_result(res, db, clusters, user_name, with_respect_to_db=False, percentage_cutoff=25)
