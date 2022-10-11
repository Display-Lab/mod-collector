import warnings
import time
import logging

import pandas as pd
import numpy as np
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
    goal_gap_size_df['gap_size']=goal_gap_size_df['gap_size'].fillna(0)
    #goal_gap_size_df.to_csv("goal_gapsize.csv")
    return goal_gap_size_df
def trend_calc(performance_data_df,comparison_values):
    performance_data_df['Month'] = pd.to_datetime(performance_data_df['Month'])
    lenb= len( comparison_values[['Measure_Name']].drop_duplicates())
    idx= performance_data_df.groupby(['Measure_Name'])['Month'].nlargest(3) .reset_index()
    l=idx['level_1'].tolist()
    latest_measure_df =  performance_data_df[performance_data_df.index.isin(l)]
    latest_measure_df['performance_data'] = latest_measure_df['Passed_Count'] / latest_measure_df['Denominator']
    latest_measure_df['performance_data']=latest_measure_df['performance_data'].fillna(0)
    lenb= len( comparison_values[['RegardingMeasure']])
    #latest_measure_df.to_csv("latest_measure.csv")
    out = latest_measure_df.groupby('Measure_Name').apply(theil_reg, xcol='Month', ycol='performance_data')
    df_1=out[0]
    df_1 = df_1.reset_index()
    df_1 = df_1.rename({0:"performance_trend_slope"}, axis=1)
    slope_df = pd.merge( latest_measure_df,df_1 , on='Measure_Name', how='outer')
    slope_df=slope_df.drop_duplicates(subset=['Measure_Name'])
    slope_final_df =pd.merge( comparison_values,slope_df , on='Measure_Name', how='outer')
    #print(lenb)
    slope_final_df = slope_final_df[:(lenb-1)]
    slope_final_df=slope_final_df.drop_duplicates(subset=['RegardingMeasure'])
    slope_final_df['performance_trend_slope'] = slope_final_df['performance_trend_slope'].abs()
    #slope_final_df.to_csv("slope.csv")
    return slope_final_df

def theil_reg(df, xcol, ycol):
   model = stats.theilslopes(df[ycol],df[xcol])
   return pd.Series(model)


def calc_goal_comparator_gap(comparison_values_df, performance_data):
    performance_data['Month'] = pd.to_datetime(performance_data['Month'])
    idx= performance_data.groupby(['Measure_Name'])['Month'].transform(max) == performance_data['Month']
    latest_measure_df = performance_data[idx]
    latest_measure_df = latest_measure_df.reset_index()
    performance_data =[]
    #latest_measure_df['performance_data'] = latest_measure_df['Passed_Count'] / latest_measure_df['Denominator']
    for rowIndex, row in latest_measure_df.iterrows():
        if (row['Passed_Count']==0 and row['Denominator']==0):
            performance_data.append(0.0)
            #print("true")
        else:
            performance_data.append(row['Passed_Count']/row['Denominator'])
    #print(performance_data)
    latest_measure_df['performance_data']=performance_data
    #latest_measure_df.to_csv("latest_measure_df.csv")
        #latest_measure_df['performance_data'] =latest_measure_df['performance_data'] .fillna(0)
    #latest_measure_df['performance_data'] = latest_measure_df['performance_data'].astype('str')

    #print(latest_measure_df.dtypes)
    #latest_measure_df['performance_data'] = latest_measure_df['performance_data'].astype('double')
    #print(latest_measure_df.dtypes)
    #comparison_values_df.rename(columns = {'index':'Measure_Name'}, inplace = True)
    
    final_df=pd.merge(comparison_values_df, latest_measure_df, on='Measure_Name', how='outer')

    #print(final_df.dtypes)
    final_df['comparison_value'] = final_df['comparison_value'].astype('double') 
    #print(final_df.dtypes)
    final_df=final_df.drop_duplicates(subset=['comparison_id'])
    final_df['gap_size'] = final_df['comparison_value']- final_df['performance_data']
    final_df['gap_size'] = final_df['gap_size'].abs()
    #print(final_df['gap_size'])
    #final_df['gap_size'] = final_df['gap_size'].astype('str') 
    #final_df['gap_size']=final_df['gap_size'].fillna(0)
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
    #final_df = final_df.drop_duplicates('comparison_id', keep='first')
    #final_df.to_csv("final_df.csv")
    return final_df

def monotonic_pred(performance_data_df,comparison_values_df):
    performance_data_df['Month'] = pd.to_datetime(performance_data_df['Month'])
    idx= performance_data_df.groupby(['Measure_Name'])['Month'].nlargest(3) .reset_index()
    l=idx['level_1'].tolist()
    latest_measure_df =  performance_data_df[performance_data_df.index.isin(l)]
    latest_measure_df['performance_data'] = latest_measure_df['Passed_Count'] / latest_measure_df['Denominator']
    latest_measure_df['performance_data']=latest_measure_df['performance_data'].fillna(0)
    trend=[]
    performance_data_month1 =[]
    performance_data_month2=[]
    performance_data_month3= []
    trend_df=latest_measure_df.drop_duplicates(subset=['Measure_Name'])
    row1=latest_measure_df.iloc[0]
    Measure_Name =row1['Measure_Name']
    #performance_data_month1.append(row1['performance_data'])
    i=0
    for rowIndex, row in latest_measure_df.iterrows():
        if(row['Measure_Name']== Measure_Name and i==0):
            performance_data_month1.append(row['performance_data'])
            i=i+1
        elif(row['Measure_Name']== Measure_Name and i==1):
            performance_data_month2.append(row['performance_data'])
            i=i+1
        elif(row['Measure_Name']== Measure_Name and i ==2):
            performance_data_month3.append( row['performance_data'])
            i=0
        if(row['Measure_Name']!=Measure_Name):
            Measure_Name = row["Measure_Name"]
            performance_data_month1.append(row['performance_data'])
            i=i+1
    trend_df['performance_data_month1']  = performance_data_month1
    trend_df['performance_data_month2']  = performance_data_month2
    trend_df['performance_data_month3']  = performance_data_month3
    trend_df = trend_df[['Measure_Name','performance_data_month1','performance_data_month2','performance_data_month3']]
    #lenb= len(trend_df[['Measure_Name']])
    #comparison_values_df = comparison_values_df[0:(lenb-1)]
    trend_df =pd.merge( comparison_values_df,trend_df , on='Measure_Name', how='outer')
    for rowIndex, row in trend_df.iterrows():
        m1= row['performance_data_month2']-row['performance_data_month1']
        m2= row['performance_data_month3']-row['performance_data_month2']
        if (m1==0 or m2==0):
            trend.append("no trend")
        elif(m1>0 and m2 <0)or(m1<0 and m2>0):
            trend.append("non-monotonic")
        elif(m1>0 and m2>0) or (m1<0 or m2<0):
            trend.append("monotonic")
    

    trend_df['trend'] = trend

    #trend_df.to_csv("trend.csv")


    return trend_df