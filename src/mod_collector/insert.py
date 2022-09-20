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
    
    for index ,row in gap_df.iterrows():
        node = row['comparison_id']
        b_node = BNode(node)
        p = (URIRef("http://example.com/slowmo#PerformanceGapSize"))
        o = Literal(row['gap_size'])
        graph_read.add((b_node, p, o,))
    return graph_read

def insert_trend(gap_df,graph_read):
    
    for index ,row in gap_df.iterrows():
        node = row['RegardingMeasure']
        b_node = BNode(node)
        p = (URIRef("http://example.com/slowmo#PerformanceTrendSlope"))
        o = Literal(row['performance_trend_slope'])
        graph_read.add((b_node, p, o,))
    return graph_read