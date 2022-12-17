# You can use either a dequeue with append() and pop()
# to simulate a stack, or use a built-in array

from pprint import pprint as pp


def dfs(graph, source, target):
    visited = set()
    to_visit = [source]
    while to_visit:
        current = to_visit.pop()
        if current is target:
            return visited
        if current not in visited:
            visited.add(current)
            neighbours = graph[current]
            for neighbour in neighbours:
                to_visit.append(neighbour)
    return None


graph = [
    [0, 1],
    [2, 3],
    [3],
    [0]
]

pp(dfs(graph, 0, 3))
