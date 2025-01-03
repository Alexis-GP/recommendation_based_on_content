import pandas as pd
import sqlite3
import networkx as nx
from itertools import combinations
from collections import Counter
from build_network import config as cfg

G = nx.Graph()

con = sqlite3.connect(cfg.FILE['subtitle_cut'])
sql = '''
select bvid, uid, lables, duration
from video_info
limit 1000
'''
# sql = '''
# select bvid, uid, lables, duration
# from video_info
# '''
data = pd.read_sql(sql=sql, con=con, index_col='bvid', )

# Add document and author nodes
for _, row in data.iterrows():
    G.add_node(row['bvid'], type='document')
    G.add_node(row['uid'], type='author')

    # Add doc-author edge
    G.add_edge(row['bvid'], row['uid'], attribute='author')
    # G.add_edge(row['bvid'], row['uid'], weight=row['duration'], attribute='author')

# Add keyword nodes and doc-keyword edges
for _, row in data.iterrows():
    doc_id = row['bvid']
    keywords = row['lables'].to_string().split(',')

    # Add keyword nodes and edges
    for keyword in keywords:
        G.add_node(keyword, type='keyword')

        # Doc-keyword edge
        keyword_count = keywords.count(keyword)
        G.add_edge(doc_id, keyword, weight=keyword_count, attribute='contain')

    # Add keyword-keyword edges
    for kw1, kw2 in combinations(keywords, 2):
        if G.has_edge(kw1, kw2):
            G[kw1][kw2]['weight'] += 1
        else:
            G.add_edge(kw1, kw2, weight=1, attribute='mentioned')

