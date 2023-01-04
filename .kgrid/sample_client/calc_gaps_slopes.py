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

def mod_collector(performance_data,comparison_values):
    gap_size= gap_calc( performance_data, comparison_values)
    trend_slope=trend_calc(performance_data,comparison_values)
    monotonic_pred_df = monotonic_pred(performance_data,comparison_values)
    mod_df=gap_size.merge(trend_slope,on='Measure_Name').merge(monotonic_pred_df,on='Measure_Name')
    mod_df=mod_df.drop_duplicates()
    mod_df.to_csv("mod_df.csv",index=False)
    return mod_df

    


def gap_calc( performance_data_df, comparison_values):
    comparison_values_df = comparison_values
    goal_gap_size_df = calc_goal_comparator_gap(comparison_values_df,performance_data_df)
    goal_gap_size_df['gap_size']=goal_gap_size_df['gap_size'].fillna(0)
    goal_gap_size_df=goal_gap_size_df[["Measure_Name","comparison_type","performance_data","gap_size"]]
    goal_gap_size_df=goal_gap_size_df.drop_duplicates()
    #goal_gap_size_df.to_csv('gap_size.csv')
    return goal_gap_size_df

def trend_calc(performance_data_df,comparison_values):
    performance_data_df['Month'] = pd.to_datetime(performance_data_df['Month'])
    lenb= len( comparison_values[['Measure_Name']].drop_duplicates())
    idx= performance_data_df.groupby(['Measure_Name'])['Month'].nlargest(3) .reset_index()
    l=idx['level_1'].tolist()
    latest_measure_df =  performance_data_df[performance_data_df.index.isin(l)]
    latest_measure_df['performance_data'] = latest_measure_df['Passed_Count'] / latest_measure_df['Denominator']
    latest_measure_df['performance_data']=latest_measure_df['performance_data'].fillna(0)
    lenb= len( comparison_values[['Measure_Name']])
    out = latest_measure_df.groupby('Measure_Name').apply(theil_reg, xcol='Month', ycol='performance_data')
    df_1=out[0]
    df_1 = df_1.reset_index()
    df_1 = df_1.rename({0:"performance_trend_slope"}, axis=1)
    slope_df = pd.merge( latest_measure_df,df_1 , on='Measure_Name', how='outer')
    slope_df=slope_df.drop_duplicates(subset=['Measure_Name'])
    slope_final_df =pd.merge( comparison_values,slope_df , on='Measure_Name', how='outer')
    slope_final_df = slope_final_df[:(lenb-1)]
    slope_final_df=slope_final_df.drop_duplicates(subset=['Measure_Name'])
    slope_final_df['performance_trend_slope'] = slope_final_df['performance_trend_slope'].abs()
    slope_final_df=slope_final_df[["Measure_Name","performance_trend_slope"]]
    #slope_final_df.to_csv('slope.csv')
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
    for rowIndex, row in latest_measure_df.iterrows():
        if (row['Passed_Count']==0 and row['Denominator']==0):
            performance_data.append(0.0)
        else:
            performance_data.append(row['Passed_Count']/row['Denominator'])
    latest_measure_df['performance_data']=performance_data
    final_df=pd.merge(comparison_values_df, latest_measure_df, on='Measure_Name', how='outer')
    final_df['comparison_value'] = final_df['comparison_value'].astype('double') 
    #final_df=final_df.drop_duplicates(subset=['comparison_id'])
    final_df['gap_size'] = final_df['comparison_value']- final_df['performance_data']
    final_df['gap_size'] = final_df['gap_size'].abs()
    
    #final_df.to_csv('final_df.csv')
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
    # comparison_values_df["slowmo:acceptable_by{URIRef}[0]"].fillna(130, inplace = True)
    # comparison_values_df = comparison_values_df[comparison_values_df['slowmo:acceptable_by{URIRef}[0]']!= 130]
    # comparison_values_df=comparison_values_df.reset_index()
    # comparison_values_df.drop(columns=comparison_values_df.columns[0], axis=1, inplace=True)
    comparison_values_df= comparison_values_df.drop_duplicates()
    trend_df =pd.merge( comparison_values_df,trend_df , on='Measure_Name', how='inner')
    for rowIndex, row in trend_df.iterrows():
        m1= row['performance_data_month2']-row['performance_data_month1']
        m2= row['performance_data_month3']-row['performance_data_month2']
        if (m1==0 or m2==0):
            trend.append("no trend")
        elif(m1>0 and m2 <0)or(m1<0 and m2>0):
            trend.append("non-monotonic")
        elif(m1>0 and m2>0) or (m1<0 or m2<0):
            trend.append("monotonic")
    lenc= len(trend)
    trend_df['trend'] = trend
    trend_df=trend_df[["Measure_Name","trend"]]
    #trend_df.to_csv('trend_df.csv')
    return trend_df