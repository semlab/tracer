#!/usr/bin/python3

import argparse
import re
import json
import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from networkx.readwrite import json_graph
from gensim.models import KeyedVectors
from sklearn.manifold import TSNE

from entities import Node, Link


class GraphBuilder:

    relation_labels = {
        0: "collaborate with",
        1: "compete against",
        2: "produce",
        3: "consume",
        4: "operates in",
    }

    def __init__(self, dataframe=None, entlinks=None, 
            graph_path=None): 
        """
        :param dataframe: containing the dataset
        :param entlinks: dictionnary representing the entities links
        :graph_path: saved graph file path
        """
        if graph_path is not None:
            self.load_graph(graph_path)
        elif dataframe is not None:
            self.G = nx.Graph() # should be multigraph
            self.df = dataframe
            self.entlinks = entlinks
            self.nodes = []
            self.links = []
        else:
            raise ValueError("Provide a dataframe or a path to load the graph")
        


    def build(self, self_links=True):
        """
        :param recursive_links: show self link or not
        """
        self.list_nodes_links()
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node.id)
            n = G.nodes[node.id]
            n['type'] = node.ner_type
            n['label'] = node.label
            n['aliases'] = node.aliases
        for link in self.links:
            if not self_links and link.source.id == link.target.id: continue
            G.add_edge(link.source.id, link.target.id)
            e = G.edges[link.source.id, link.target.id]
            e['labels'] = link.labels
            e['type'] = link.rel_type
        self.G = G
        return self.G


    def list_nodes_links(self):
        nodes = []
        links = []
        for idx, row in self.df.iterrows():
            subj_ent = row['SUBJ_ENT']
            # TODO uncomment
            #label = self.entlookup[subj_ent] if subj_ent in self.entlookup else subj_ent 
            label = subj_ent
            ner_type = row['SUBJ_ENT_TYPE']
            source = Node(label, ner_type)
            if source not in nodes:
                nodes.append(source)
            obj_ent = row['OBJ_ENT']
            # TODO uncomment
            #label = self.entlookup[obj_ent] if obj_ent in self.entlookup else obj_ent 
            label = obj_ent
            ner_type = row['OBJ_ENT_TYPE']
            target = Node(label, ner_type)
            if target not in nodes:
                nodes.append(target)
            #link = Link(source, target, rel_type=row['RELATION_TYPE']) 
            link = Link(source, target, rel_type=row['REL_TYPE']) 
            #link = Link(source, target) 
            #label = row['RELATION']
            label = GraphBuilder.relation_labels[row['REL_TYPE']]
            try:
                idx = links.index(link)
                links[idx].labels.append(label)
            except ValueError:
                link.labels.append(label)
                links.append(link)
        self.nodes = nodes
        self.links = links
        return self.nodes, self.links


    def save_graph(self, filename, graph=None):
        if graph is None:
            data = json_graph.node_link_data(self.G)
        else:
            data = json_graph.node_link_data(graph)
        file_content = json.dumps(data)
        with open(filename, 'w') as outfile: 
            outfile.write(file_content)
    

    def load_graph(self, filename):
        file_content = ""
        with open(filename, 'r') as infile:
            file_content = infile.read()
        data = json.loads(file_content)
        self.G = json_graph.node_link_graph(data)


    def embbedings_layout(self, embeddings_path, nodes=None):
        # TODO 2D/3D and tsne/pca
        if nodes is None:
            nodes = G.nodes()
        model = KeyedVectors.load(embeddings_path)
        #vectors = [model.wv[node] for node in nodes]
        tsne = TSNE(perplexity=40, n_components=2, init='pca', 
                n_iter=2500, random_state=23)
        zero = np.zeros_like(model.wv[0])
        vectors = [model.wv[k] if k in model.wv else zero 
                for k in model.wv.key_to_index]
        X = np.array(vectors)
        lowd_vecs = tsne.fit_transform(X) 
        nodes_pos = [lowd_vecs[model.wv.key_to_index[node]] 
                if node in model.wv else [0,0]
                for node in nodes]
        pos = dict(zip(nodes, nodes_pos))
        return pos


    @staticmethod
    def nodecolors(nodes):
        # TODO improve like link
        colormap = {"ORGANIZATION": "r", 
            "PERSON":"g",
            "LOCATION":"b",
            "COMMODITY":"y",
        }
        colors = [colormap[nodes[key]['type']] 
            if 'type' in nodes[key] and nodes[key]['type'] in colormap 
            else "w" for key in nodes]
        return colors


    @staticmethod
    def linkcolors(edges):
        #print(edges[0])
        reltypes = [d['type'] for _, d in edges.items()]
        coldic = {rel:col for col, rel in enumerate(set(reltypes)) }
        colors = [coldic[reltype] for reltype in reltypes]
        return colors


def kgbuild(df_path=None, graph_path=None, component=None, 
        outpath=None, figure=None, wv_path=None, verbose=False):
    builder = None
    if df_path is None and graph_path is None:
        raise ValueError("Provide a csv file path or a graph to load")
    if graph_path is not None:
        if verbose : print("Loading graph from file: {}".format(graph_path))
        builder = GraphBuilder(graph_path=graph_path)
    elif df_path is not None:
        if verbose : print("Building graph from dataframe")
        df = pd.read_csv(df_path)
        builder = GraphBuilder(df)
        builder.build(self_links=False)
    G = builder.G
    if component is not None:
        if component < 0: 
            raise ValueError("Component argumnent should be >= 0")
        if verbose : print("Processing subgraph (from component {})".format(component))
        compset = sorted(nx.connected_components(G), key=len, reverse=True)
        G = G.subgraph(compset[component])
    if outpath is not None:
        if verbose : print("Saving to {}".format(outpath))
        builder.save_graph(outpath, graph=G)
    if figure is not None:
        if verbose : print("Drawing figure to {}".format(figure))
        if verbose: print("....Creating layout")
        if wv_path is not None:
            layout = builder.embbedings_layout(wv_path, G.nodes())
        else:
            layout = nx.spring_layout(G)
        if verbose: print("....Drawing nodes")
        plt.figure(figsize=(10,8))
        #node_colors = GraphBuilder.nodecolors(G.nodes())
        nodetypes = ['ORGANIZATION', 'PERSON', 'LOCATION', 'COMMODITY']
        for nodetype in nodetypes:
            if verbose: print(f"...Drawing {nodetype}")
            allnodes = G.nodes()
            nodes = [node for node in allnodes 
                        if 'type' in allnodes[node] and allnodes[node]['type']== nodetype]
            nodecolors = GraphBuilder.nodecolors(G.subgraph(nodes).nodes())
            nx.draw_networkx_nodes(G, pos=layout, nodelist=nodes, 
                    node_color=nodecolors, label=nodetype,
                    node_size=25, linewidths=0.5)
        #nx.draw_networkx_nodes(G, layout, node_size=25, linewidths=0.5,
        #        node_color=node_colors)
        if verbose: print("....Drawing edges")
        link_colors = GraphBuilder.linkcolors(G.edges)
        nx.draw_networkx_edges(G, layout, width=0.5, arrows=True, 
                edge_color=link_colors, edge_cmap=plt.cm.tab20)
        plt.legend(scatterpoints=1)
        plt.savefig(figure, dpi=100)


    

def getargs():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--input', required=False, 
            help="triples csv filepath")
    group.add_argument('-l', '--load', required=False, 
            help="input file of the network to load. Do not build from csv.")
    parser.add_argument('-V', '--vectors', required=False, 
            help="vectors file model.")
    parser.add_argument('-o', '--output', required=False, 
            help="Output file of the network")
    parser.add_argument('-f', '--figure', required=False, 
            help="Output file of the network figure")
    parser.add_argument('-c', '--component', required=False, type=int,
            help="use indexes to isolate a component of the graph 0 being the biggest")
    parser.add_argument('-v', '--verbose', required=False, action="store_true",
            help="verbose mode. showing operation being done")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    args_dict['figure'] = args.figure
    args_dict['component'] = args.component
    args_dict['load'] = args.load
    args_dict['vectors'] = args.vectors
    args_dict['verbose'] = args.verbose
    return args_dict

# TODO add legend
# TODO possibility to show labels
    
if __name__ == "__main__":
    args = getargs()
    kgbuild(df_path = args['input'], 
            graph_path = args['load'], 
            component = args['component'], 
            outpath = args['output'], 
            figure = args['figure'], 
            wv_path = args['vectors'], 
            verbose = args['verbose'])

    """
    triples_fpath = args['input']#"../data/triples/triples-elinked-rand-lbl.csv"
    wv_fpath = args['vectors'] #"../data/gensim.55K.100.bin"
    fig_fpath = args['figure']#"../data/figs/network.pdf"
    df = pd.read_csv(triples_fpath)
    builder = GraphBuilder(df)
    builder.list_nodes_links()
    G = builder.build(self_links=False)
    compset = sorted(nx.connected_components(G), key=len, reverse=True)
    giant = G.subgraph(compset[0])
    giant_pos = builder.embbedings_layout( wv_fpath, giant.nodes())
    node_colors = GraphBuilder.nodecolormap(giant.nodes())
    plt.figure(figsize=(10,8))
    nx.draw(G)
    plt.savefig('../data/figs/net.pdf', dpi=100)
    plt.clf()
    nx.draw_networkx_nodes(giant, giant_pos, 
        node_size=15, linewidths=0.3, 
        node_color=node_colors, arrows=True)
    nx.draw_networkx_edges(giant, giant_pos)
    plt.savefig('../data/figs/net-giant.pdf', dpi=100)
    plt.clf()
    nx.draw(G.subgraph(compset[1]), arrows=True)
    plt.savefig('../data/figs/comp1.pdf', dpi=100)
    plt.clf()
    plt.close()
    #"""
   
