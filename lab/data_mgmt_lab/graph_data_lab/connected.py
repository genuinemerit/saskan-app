# Debug this...

example_adjacency_list = [
    [1, 2],
    [2, 3],
    [],
    [0],
]

example_adjacency_list_connected = [
    [1, 2, 3],
    [3],
    [0],
    [0, 1],
]


def is_path_between(graph, source, target):
    visited = set()
    to_visit = []
    to_visit.append(source)
    while to_visit:
        current = to_visit.pop()
        if current in visited:
            continue
        if current == target:
            return True
        for neighbour in graph[current]:
            to_visit.append(neighbour)
    return False


assert is_path_between(example_adjacency_list, 0, 1)
assert is_path_between(example_adjacency_list_connected, 0, 5)
assert not is_path_between(example_adjacency_list_connected, 5, 0)


def is_connected(graph):
    for node1 in range(len(graph)):
        for node2 in range(len(graph)):
            if not is_path_between(graph, node1, node2):
                return False
    return True


assert not is_connected(example_adjacency_list)
assert is_connected(example_adjacency_list_connected)
