from tracemalloc import start
import warnings
import time
import logging
import csv

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef ,BNode
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD 
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper
import numpy as np 

warnings.filterwarnings("ignore")

def insert_gap(gap_df,graph_read):
    print(gap_df.dtypes)
    for index ,row in gap_df.iterrows():
        if row["performance_data"] != 0:
            node = row['comparison_id']
            b_node = BNode(node)
            p = (URIRef("http://example.com/slowmo#PerformanceGapSize"))
            o = Literal(row['gap_size'])
            graph_read.add((b_node, p, o,))
        # else:
        #     print(row['gap_size'])
    return graph_read

def insert_slope(gap_df,graph_read):
    
    for index ,row in gap_df.iterrows():
        node = row['RegardingMeasure']
        b_node = BNode(node)
        p = (URIRef("http://example.com/slowmo#PerformanceTrendSlope"))
        o = Literal(row['performance_trend_slope'])
        graph_read.add((b_node, p, o,))
    return graph_read

def insert_trend(gap_df,graph_read):
    for index ,row in gap_df.iterrows():
        node = row['id']
        b_node = BNode(node)
        p = (URIRef("http://purl.obolibrary.org/obo/RO_0000091"))
        o =BNode()
        graph_read.add((b_node, p, o,))
        s=o
        p1 = RDF.type
        if row['trend']== "no trend":
            trend ="http://example.com/slowmo#NoTrend"
        elif row['trend']== "monotonic":
            trend ="http://example.com/slowmo#MonotonicTrend"
        elif row['trend']== "non-monotonic":
            trend ="http://example.com/slowmo#NonMonotonicTrend"
        node1 = Literal(trend)
        o1 = BNode(node1)
        graph_read.add((s,p1,o1))
        p2=(URIRef("http://example.com/slowmo#RegardingComparator"))
        node2=row['comparison_id']
        o2=BNode(node2)
        graph_read.add((s,p2,o2))
        p3=(URIRef("http://example.com/slowmo#RegardingMeasure"))
        node3=row['RegardingMeasure']
        o3=BNode(node3)
        graph_read.add((s,p3,o3))
    
    return graph_read
