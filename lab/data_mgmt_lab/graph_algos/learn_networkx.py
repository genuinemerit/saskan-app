# From Oreilly course on Graph Data Structures and Alogrithms,
# basic intro to networkx:

from pprint import pprint as pp
import networkx as nx
from networkx.algorithms import shortest_path
from networkx.algorithms import all_simple_paths
from networkx.algorithms import simple_cycles
from networkx.algorithms import is_tree
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_node(1)
G.add_nodes_from([2, 3])
G.add_edge(1, 2)

pp(G.degree[1])
print(f"number of edges: {G.number_of_edges()}")
print(f"number of nodes: {G.number_of_nodes()}")

G.add_nodes_from([4, 5, 6, 7])
G.add_edges_from([(3, 4), (4, 6), (3, 5), (3, 7), (5, 7), (6, 7), (1, 3)])

# Here is how to breadth-first search in a graph
pp(list(shortest_path(G, 1, 7)))

# As an exercise: Do a depth-first search! 
# You can use the `dfs_edges` algorithm.
# consider reading the docs here:
# https://networkx.org/documentation/stable/reference/algorithms/traversal.html#module-networkx.algorithms.traversal.depth_first_search

pp(list(all_simple_paths(G, 1, 7)))

D = nx.DiGraph()
D.add_nodes_from([4, 5, 6, 7])
D.add_edges_from([(3, 4), (4, 6), (3, 5), (3, 7), (5, 7), (6, 7), (1, 3), (7, 1), (7, 3)])
# We can also find cycles in a graph.
# Use the `simple_cycles` algorith to find all simple cycles, and
# use `find_cycle` to find any particular cycle.

pp(list(simple_cycles(D)))

# Is this graph a tree?
# Use the `is_tree` algorithm to determine it!
pp(is_tree(D))

# We can render graphs by using
G = nx.complete_graph(6)
plt.plot()
nx.draw(G, with_labels=True, font_weight='bold')
plt.title("Test Diagrams")
plt.savefig("/home/bow/Desktop/test.png")
