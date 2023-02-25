from pprint import pprint as pp
from collections import deque
# Create a dequeue with deque()
# Add items to the right with q.append()
# Remove from the left with with q.popleft()


def bfs(graph, source, target):
    visited = set()
    to_visit = deque()
    to_visit.append(source)
    while to_visit:
        current = to_visit.popleft()
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
pp(bfs(graph, 0, 3))
