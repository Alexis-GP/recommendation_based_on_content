import pandas as pd
import sqlite3
import networkx as nx
from itertools import combinations
from collections import Counter
from build_network import config as cfg
import copy
import math
from collections import defaultdict


G = nx.read_graphml(cfg.FILE['graph_label'])

G_without_kw_edges = copy.deepcopy(G)
edges_to_remove = [(u, v) for u, v, data in G.edges(data=True) if data.get('attribute') == 'co-occurrence']
G_without_kw_edges.remove_edges_from(edges_to_remove)

G_without_kw_edges_vid_nodes = copy.deepcopy(G_without_kw_edges)
nodes_to_remove = [u for u, data in G_without_kw_edges.nodes(data=True) if data.get('type') == 'document']
G_without_kw_edges_vid_nodes.remove_nodes_from(nodes_to_remove)


# Print sample author-keyword edges
# random = 0
# for u, v, data in G.edges(data=True):
#     if data.get('attribute') == 'mention' and G.nodes[u].get('type') == 'author':
#         if random % 50 == 0:
#             print(f"uid: {u}, keyword: {v:7}, Weight: {round(data['weight'], 3)}")
#         random += 1
#         if random == 10000:
#             break


def recommend_based_on_keywords(graph, keywords, max_len=None, rst='author'):
    if len(keywords) < 2:
        raise ValueError("At least two keywords are required.")

    # Step 1: Find all pairs of keywords
    pairs = [(keywords[i], keywords[j]) for i in range(len(keywords)) for j in range(i + 1, len(keywords))]
    recommendation_counts = Counter()

    for kw1, kw2 in pairs:
        try:
            # Step 2: Find the shortest path
            paths = list(nx.all_shortest_paths(graph, source=kw1, target=kw2))
            # paths = nx.all_simple_paths(graph, source=kw1, target=kw2, cutoff=max_len)

            for path in paths:
                # Ensure path includes at least one doc or author
                docs_authors = [node for node in path if graph.nodes[node].get('type') in {rst,}]
                if docs_authors:
                    recommendation_counts.update(docs_authors)

        except nx.NetworkXNoPath:
            continue  # Skip if no path exists between the pair

    # Step 3: Rank authors and docs by their presence in paths
    recommendations = sorted(recommendation_counts.items(), key=lambda x: x[1], reverse=True)

    return recommendations



def rec_vid(keywords):
    return recommend_based_on_keywords(G_without_kw_edges, keywords, rst='document')

def rec_up(keywords):
    return recommend_based_on_keywords(G_without_kw_edges_vid_nodes, rst='author')

