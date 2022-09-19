from asyncore import read
import json
import sys
import warnings
import time
import logging
import json
#from asyncore import read

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper


# from .load_for_real import load
from .load import  read, transform,read_contenders,read_measures,read_comparators
from .calc_gaps_slopes import gap_calc
from .insert import insert_gap

# load()

warnings.filterwarnings("ignore")
# TODO: process command line args if using graph_from_file()
# Read graph and convert to dataframe
start_time = time.time()
graph_read = read(sys.argv[1])
performance_data_df = pd.read_csv(sys.argv[2])

#indv_preferences_read_df = pd.read_json(sys.argv[2], lines=True)
contenders_graph = read_contenders(graph_read)
measures_graph = read_measures(graph_read)
comparator_graph = read_comparators(graph_read)
# print(contenders_graph)
# contenders_graph=graph_from_sparql_endpoint("http://localhost:3030/ds/sparql")
# print(contenders_graph.serialize(format="ttl"))
# Transform dataframe to more meaningful dataframe
comparison_values = transform(contenders_graph,measures_graph,comparator_graph)
gap_size= gap_calc( performance_data_df, comparison_values)

gap_graph =insert_gap(gap_size,graph_read)
print(gap_graph.serialize(format='json-ld', indent=4))

