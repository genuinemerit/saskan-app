from pprint import pprint as pp
nodes = list(range(4))
edges = [(0, 1), (1, 2), (0, 2), (1, 3), (3, 0)]
adj_list = [[] for _ in range(4)]
adj_matrix = [[0 for _ in range(4)] for _ in range(4)]


def load_adj_list():
    for s, t in edges:
        adj_list[s].append(t)
    pp(adj_list)


def load_adj_matrix():
    for s, t in edges:
        adj_matrix[s][t] = 1
    pp(adj_matrix)


load_adj_list()
load_adj_matrix()
