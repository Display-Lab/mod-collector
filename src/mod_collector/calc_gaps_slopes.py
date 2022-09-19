import warnings
import time
import logging

import pandas as pd
import scipy
from scipy import stats
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper

warnings.filterwarnings("ignore")

def gap_calc( performance_data_df, comparison_values):
    comparison_values_df = comparison_values
    goal_gap_size_df = calc_goal_comparator_gap(comparison_values_df,performance_data_df)
    
    return goal_gap_size_df



def calc_goal_comparator_gap(comparison_values_df, performance_data):
    performance_data['Month'] = pd.to_datetime(performance_data['Month'])
    idx= performance_data.groupby(['Measure_Name'])['Month'].transform(max) == performance_data['Month']
    latest_measure_df = performance_data[idx]
    latest_measure_df['performance_data'] = latest_measure_df['Passed_Count'] / latest_measure_df['Denominator']
    #comparison_values_df.rename(columns = {'index':'Measure_Name'}, inplace = True)
    
    final_df=pd.merge(comparison_values_df, latest_measure_df, on='Measure_Name', how='inner')
    #print(final_df.dtypes)
    final_df['comparison_value'] = final_df['comparison_value'].astype('double') 
    #print(final_df.dtypes)
    
    final_df['gap_size'] = final_df['comparison_value']- final_df['performance_data']
    final_df['gap_size'] = final_df['gap_size'].abs()
    #final_df.to_csv("final_df.csv")

#     lenb= len(latest_measure_df[['Passed_Count']])
#     final_df1 = final_df[0:(lenb-1)]
#     final_df1['performance_data'] = final_df1['performance_data'].fillna(0)
#     #final_df['GoalComparator'].astype(float)
#     final_df1['GoalComparator'] = pd.to_numeric(final_df1['GoalComparator'],errors='coerce')
#     final_df1['SocialComparator'] = pd.to_numeric(final_df1['SocialComparator'],errors='coerce')
#     final_df1['performance_data'] = pd.to_numeric(final_df1['performance_data'],errors='coerce')
#     final_df1['goal_comparator_size'] = final_df1['GoalComparator']- final_df1['performance_data']
#     final_df1['goal_comparator_size'] = final_df1['goal_comparator_size'].abs()
#     c
#     final_df1['social_comparator_size'] = final_df1['social_comparator_size'].abs()
#     #final_df1['goal_comparator_size'] = final_df1['performance_data'].fillna(0)
#     #print(lenb)
#     #final_df1.to_csv("final_df.csv")
#     final_df1 = final_df1[['Measure_Name','goal_comparator_node','social_comparator_node','GoalComparator','SocialComparator','Passed_Count','Flagged_Count','Denominator','performance_data','goal_comparator_size','social_comparator_size']]
#     #final_df1.to_csv("final_df.csv")
#    # final_df1 = final_df1.rename({'http://example.com/slowmo#WithComparator{BNode}[0]': 'goal_comparator_node', 'http://example.com/slowmo#WithComparator{BNode}[1]': 'social_comparator_node'}, axis=1)
#     #final_df1.to_csv("final_df.csv")
    #print(latest_measure_df.head())
    final_df = final_df.drop_duplicates('comparison_id', keep='first')
    #final_df.to_csv("final_df.csv")
    return final_df
