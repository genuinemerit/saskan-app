#!python
"""
:module:    saskan_report.py
:author:    GM (genuinemerit @ pm.me)
Saskan Admin Report Generator

@DEV:
- Consider whether it makes sense to move Analysis
  reporting functions to this module.
- For some reason it was using networkx OK then it
  started saying it could not be imported. WTF??
"""

import matplotlib.pyplot as plt         # type: ignore
import networkx as nx                   # type: ignore
import subprocess as shl
# import sys

from dataclasses import dataclass
# from os import path
# from pathlib import Path
from pprint import pprint as pp     # noqa: F401

# from io_file import FileIO          # type: ignore
# from io_shell import ShellIO        # type: ignore
# from io_wiretap import WireTap      # type: ignore

# FI = FileIO()
# SI = ShellIO()
# WT = WireTap()


# ====================================================
#  SASKAN REPORT
# ====================================================
class SaskanReport(object):
    """Provide report and monitoring methods for Saskan Admin.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the object.
        """
        pass

    @dataclass
    class COLOR:
        """Define CLI/terminal colors.

        See https://stackoverflow.com/a/287944/119527
        and https://pypi.org/project/termcolor/

        Also see saskan_admin.py for more of these, and
        for PyGame colors, which are RGB tuples.
        """
        BLUE = '\033[94m'
        BOLD = '\033[1m'
        CYAN = '\033[96m'
        DARKCYAN = '\033[36m'
        END = '\033[0m'
        GREEN = '\033[92m'
        PURPLE = '\033[95m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        UNDERLINE = '\033[4m'

    @classmethod
    def run_cmd(cls, cmd):
        """
        Execute a shell command from Python.
        Best to execute scripts using `bash` not `touch`, `.` or `sh`

        :Args:  {list} shell command as a string in a list

        :Return: {tuple} ({boolean} success/failure, {bytes} result)
        """
        cmd_rc = False
        cmd_result = b''  # Stores bytes

        if cmd == "" or cmd is None:
            cmd_rc = False
        else:
            # shell=True means cmd param contains a regular cmd string
            shell = shl.Popen(cmd, shell=True,
                              stdin=shl.PIPE, stdout=shl.PIPE,
                              stderr=shl.STDOUT)
            cmd_result, _ = shell.communicate()
            if 'failure'.encode('utf-8') in cmd_result or\
                    'fatal'.encode('utf-8') in cmd_result:
                cmd_rc = False
            else:
                cmd_rc = True
        return (cmd_rc, cmd_result.decode('utf-8').strip())

    def rpt_ufw_status(self):
        """Get UFW status.
        """
        ok, result = self.run_cmd("ufw status numbered")
        if ok:
            return result

    def rpt_running_jobs(self,
                         p_job_nm: str):
        """Return display of running jobs matching grep param."""
        ok, result = self.run_cmd(f"ps -ef | grep {p_job_nm}")
        if not ok:
            raise Exception(f"{result}")
        running_jobs = result.split("\n")
        return (result, running_jobs)

    # Helper functions
    def get_ntype(self,
                  p_N: dict,
                  p_node_nm: str):
        """Return node type for a given node name.

        :args:
        - p_N (dict): additional nodes metadata for graph object
        - p_title (str): Name of a schema/ontology, e.g. "scenes"
        - p_node_nm (str): Node name.
        """
        node_type = None
        for nt, nodes in p_N["name"].items():
            if p_node_nm in nodes:
                node_type = nt
                break
        return node_type

    def set_graph(self,
                  p_E: dict,
                  p_incl_nodes: list = []):
        """Populate networkx graph dataset using edges dataset.
        - Defining the edges automatically also defines the nodes.
        - Limiting the graph to a subset of nodes here affects what
          is reported and displayed by report and display functions.
        - If no subset is defined, all nodes are included.

        :args:
        - p_E (dict): Edge data for graph object
        - p_incl_nodes (list): Node names to include in graph (optional)
        """
        G = nx.MultiDiGraph()
        for e_list in p_E["name"].values():
            edges = list()
            for (n1, n2) in e_list:
                if p_incl_nodes == []:
                    edges.append(tuple((n1, n2)))
                elif n1 in p_incl_nodes or n2 in p_incl_nodes:
                    edges.append(tuple((n1, n2)))
            G.add_edges_from(edges)
        return G

    def report_degrees(self,
                       p_title: str,
                       p_G,
                       p_N: dict):
        """Show report of degrees for graphed nodes.

        :args:
        - p_title (str): Title for report, usually the name of the graph set
        - p_G (nx.MultiDiGraph()): networkx graph object
        - p_N (dict): additional node metadata for graph object

        @DEV:
        - Integrate Analysis() into the admin app
        - Provide interactive options and reports like:
            - List all nodes, be able to pick a subset
            - List node-type and edge-type, be able to pick subset
            - List scenes on a timeline,
                optionally list selected nodes in each scene
        - Do NOT try to create an editor for the JSON file,
            just use a fucking editor. :-)
        - Parameterize report options
        """
        print(f"{p_title}\n=====================")
        rpt_data = sorted([(p_G.degree(n), n, self.get_ntype(p_N, n))
                           for n in p_G.nodes()], reverse=True)
        pp((rpt_data))

    def draw_graph(self,
                   p_title: str,
                   p_G,
                   p_N: dict,
                   p_E: dict):
        """Draw graph based on G data.

        :args:
        - p_title (str): name of the graph set
        - p_G (nx.MultiDiGraph()): networkx graph object
        - p_N (dict): additional node metadata for graph object
        - p_E (dict): additional edge metadata for graph object
        """
        node_sizes = [p_G.degree(n) * 23 for n in p_G.nodes()]
        node_labels = {n: f"\n{self.get_ntype(p_N, n)}\n{n}"
                       for n in p_G.nodes()}
        node_colors = [p_N["color"][n] for n in p_G.nodes()]
        edge_colors = [p_E["color"][
                        (self.get_ntype(p_N, e[0]),
                         self.get_ntype(p_N, e[1]))].replace("0", "5")
                       for e in p_G.edges()]
        # Folks online tend to recommend graphviz for drawing graphs, but
        # I could not get graphviz to work with my environment, networkx.

        # See: https://networkx.org/documentation/stable/reference/drawing.html

        # Most of these layouts need or require additional parameters,
        #  but I am not clear yet on how to set them usefully.

        # Ones I prefer so far are marked with a "# *" comment.
        pos = nx.spiral_layout(p_G)                   # *
        # pos = nx.spring_layout(G, seed=13648)     # *
        # pos = nx.circular_layout(G)               # *
        # pos = nx.shell_layout(G)                  # *
        # pos = nx.kamada_kawai_layout(G)           # requires scipy
        # pos = nx.random_layout(G)
        # pos = nx.spectral_layout(G)
        plt.title(p_title)
        cmap = plt.cm.plasma
        ax = plt.gca()
        ax.set_axis_off()
        nx.draw_networkx_nodes(p_G, pos,
                               linewidths=1,
                               node_color=node_colors,
                               node_size=node_sizes)
        nx.draw_networkx_edges(p_G, pos,
                               arrows=False,
                               edge_color=edge_colors,
                               edge_cmap=cmap,
                               width=1)
        # Node labels
        nx.draw_networkx_labels(p_G, pos,
                                font_size=9,
                                font_color='indigo',
                                labels=node_labels,
                                verticalalignment="top")
        plt.show()
