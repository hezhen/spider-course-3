# coding=utf-8

# python-graph https://code.google.com/p/python-graph/

# Import graphviz
import graphviz as gv

# Import pygraph
from pygraph.classes.digraph import digraph
from pygraph.readwrite.dot import write

# Define pagerank function
def pagerank(graph, damping_factor=0.85, max_iterations=100, \
             min_delta=0.00001):
    """
    Compute and return the PageRank in an directed graph.

    @type  graph: digraph
    @param graph: Digraph.

    @type  damping_factor: number
    @param damping_factor: PageRank dumping factor.

    @type  max_iterations: number
    @param max_iterations: Maximum number of iterations.

    @type  min_delta: number
    @param min_delta: Smallest variation required for a new iteration.

    @rtype:  Dict
    @return: Dict containing all the nodes PageRank.
    """

    nodes = graph.nodes()
    graph_size = len(nodes)
    if graph_size == 0:
        return {}
    # value for nodes without inbound links
    min_value = (1.0-damping_factor)/graph_size

    # itialize the page rank dict with 1/N for all nodes
    #pagerank = dict.fromkeys(nodes, 1.0/graph_size)
    pagerank = dict.fromkeys(nodes, 1.0)

    for i in range(max_iterations):
        diff = 0 #total difference compared to last iteraction
        # computes each node PageRank based on inbound links
        for node in nodes:
            rank = min_value
            for referring_page in graph.incidents(node):
                rank += damping_factor * pagerank[referring_page] / \
                        len(graph.neighbors(referring_page))

            diff += abs(pagerank[node] - rank)
            pagerank[node] = rank

        print 'This is NO.%s iteration' % (i+1)
        print pagerank
        print ''

        #stop if PageRank has converged
        if diff < min_delta:
            break

    return pagerank

# Graph creation
gr = digraph()

# Add nodes and edges
gr.add_nodes(["1","2","3","4"])

gr.add_edge(("1","2"))
gr.add_edge(("1","3"))
gr.add_edge(("1","4"))
gr.add_edge(("2","3"))
gr.add_edge(("2","4"))
gr.add_edge(("3","4"))
gr.add_edge(("4","2"))

# Draw as PNG
dot = write(gr)
gvv = gv.readstring(dot)
gv.layout(gvv,'dot')
gv.render(gvv,'png','Model.png')
