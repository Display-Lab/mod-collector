#from asyncore import read
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
from .calc_gaps_slopes import gap_calc,trend_calc,monotonic_pred,mod_collector
from .insert import insert_gap,insert_trend ,insert_slope

# load()

warnings.filterwarnings("ignore")
# TODO: process command line args if using graph_from_file()
# Read graph and convert to dataframe
start_time = time.time()
graph_read = read(sys.argv[1])
performance_data_df = pd.read_csv(sys.argv[2])


#indv_preferences_read_df = pd.read_json(sys.argv[2], lines=True)
contenders_graph = read_contenders(graph_read)
contender_messages_df = to_dataframe(contenders_graph)
#contender_messages_df.to_csv("contenders.csv")

measures_graph = read_measures(graph_read)
measures_df = to_dataframe(measures_graph)
#measures_df.to_csv("measures.csv")
comparator_graph = read_comparators(graph_read)
comparator_df = to_dataframe(comparator_graph)
#comparator_df.to_csv("comparator.csv")
# print(contenders_graph)
# contenders_graph=graph_from_sparql_endpoint("http://localhost:3030/ds/sparql")
# print(contenders_graph.serialize(format="ttl"))
# Transform dataframe to more meaningful dataframe
comparison_values = transform(contenders_graph,measures_graph,comparator_graph)
comparison_values = comparison_values.rename({'name': 'comparison_type'}, axis=1)
comparison_values12=comparison_values[["comparison_value","comparison_type","Measure_Name"]]

comparison_values12.to_csv("comparison_values_1.csv",index=False)
mod_df=mod_collector(performance_data_df, comparison_values12)

final_df = comparison_values.merge(mod_df, left_on=['Measure_Name','comparison_type'], right_on=['Measure_Name','comparison_type'] ,how='left')
#final_df .to_csv("before_insert.csv")
# gap_size= gap_calc( performance_data_df, comparison_values12)
# trend_slope=trend_calc(performance_data_df,comparison_values12)
# monotonic_pred_df = monotonic_pred(performance_data_df,comparison_values12)


gap_graph =insert_gap(final_df,graph_read)
slope_graph =insert_slope(final_df,gap_graph)
trend_graph = insert_trend(final_df,gap_graph)
print(trend_graph.serialize(format='json-ld', indent=4))

