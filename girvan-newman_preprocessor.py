#!/usr/bin/env python3


import json
import sys


weight = 1


if __name__ == '__main__':
    (raw_file_addr, edges_file_addr, map_file_addr) = tuple(input().split(" "))

    with open(raw_file_addr) as f:
        _, _, adjacency_list = json.loads(f.read())

    map_dict = {}
    with open(edges_file_addr, "w") as f:
        for (u, l) in adjacency_list.items():
            u = int(u)
            if u not in map_dict.keys():
                map_dict[u] = len(map_dict)
            for v in l:
                v = int(v)
                if v not in map_dict.keys():
                    map_dict[v] = len(map_dict)
                if map_dict[v] > map_dict[u]:
                    print("%d, %d, %d" % (map_dict[u], map_dict[v], weight), file = f)

    with open(map_file_addr, "w") as f:
        f.write(json.dumps(map_dict, indent = 4))

