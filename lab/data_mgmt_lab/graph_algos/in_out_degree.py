# from pprint import pprint as pp

example_adjacency_list = [
    [1, 2],
    [2, 3],
    [],
    [0],
]


def in_degree(graph, node_id):
    id = 0
    for node, in_list in enumerate(graph):
        print(f"{node + 1}d{len(in_list)}")
        id = len(in_list) if len(in_list) > id else id
    return id


print(f"graph max degree={in_degree(example_adjacency_list, 0)}")


def out_degree(graph, node_id):
    pass
