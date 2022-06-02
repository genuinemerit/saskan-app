# is every node connected to every other node?

example_adjacency_list_complete = [
    [1, 2, 3],
    [0, 2, 3],
    [0, 1, 3],
    [0, 1, 2],
]


def is_complete(graph):
    # need to also check if all nodes are connected
    for node, edges in enumerate(graph):
        if node in edges:
            return False
    return True


print(f"Graph is complete: {str(is_complete(example_adjacency_list_complete))}")
