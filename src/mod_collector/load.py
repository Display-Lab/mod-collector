import warnings
import time
import logging

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, XSD
from rdflib.serializer import Serializer
from rdfpandas.graph import to_dataframe
from SPARQLWrapper import XML, SPARQLWrapper

warnings.filterwarnings("ignore")


def read(file):
    start_time = time.time()
    g = Graph()
    g.parse(file)
    logging.critical(" reading graph--- %s seconds ---" % (time.time() - start_time)) 
    return g
def read_contenders(graph_read):
    start_time = time.time()
    qres = graph_read.query(
        """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX slowmo: <http://example.com/slowmo#>
    construct {
    ?candidate ?p ?o .
    ?candidate obo:RO_0000091 ?o2 .
    ?o2 slowmo:RegardingComparator ?comparator .
    ?o2 slowmo:RegardingMeasure ?measure .
    
    } 
    WHERE {
    ?candidate ?p ?o .
    ?candidate obo:RO_0000091 ?o2 .
    ?o2 slowmo:RegardingComparator ?comparator .
    ?o2 slowmo:RegardingMeasure ?measure .
    
    }
    """
    )
    logging.critical(" querying contenders graph--- %s seconds ---" % (time.time() - start_time)) 
    return qres.graph
def read_measures(graph_read):
    start_time = time.time()
    qres = graph_read.query(
        """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX slowmo: <http://example.com/slowmo#>
    construct {
    ?candidate slowmo:RegardingMeasure ?measure .
    ?measure ?p3 ?o3 .
    }
    WHERE {
    ?candidate slowmo:RegardingMeasure ?measure .
    ?measure ?p3 ?o3 .
    }
    """
    )
    logging.critical(" querying measures graph--- %s seconds ---" % (time.time() - start_time)) 
    return qres.graph
def read_comparators(graph_read):
    start_time = time.time()
    qres = graph_read.query(
        """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX slowmo: <http://example.com/slowmo#>
    construct {
    ?candidate slowmo:RegardingComparator ?comparator .
    ?comparator ?p2 ?o2 .
    }
    WHERE {
    ?candidate slowmo:RegardingComparator ?comparator .
    ?comparator ?p2 ?o2 .
    }
    """
    )
    logging.critical(" querying comparator graph--- %s seconds ---" % (time.time() - start_time)) 
    return qres.graph


def transform(contenders_graph,measures_graph,comparator_graph):
    start_time = time.time()
    contenders_graph.bind("obo", "http://purl.obolibrary.org/obo/")
    contenders_graph.bind("slowmo", "http://example.com/slowmo#")

    # start implementation of esteemer algorithm
    contender_messages_df = to_dataframe(contenders_graph)
    contender_messages_df.reset_index(inplace=True)
    contender_messages_df = contender_messages_df.rename(columns={"index": "id"})
    #contender_messages_df.to_csv("contenders.csv")
    measures_df = to_dataframe(measures_graph)
    measures_df.reset_index(inplace=True)
    measures_df = measures_df.rename(columns={"index": "id"})
    #measures_df.to_csv("measures.csv")
    comparator_df = to_dataframe(comparator_graph)
    comparator_df.reset_index(inplace=True)
    comparator_df = comparator_df.rename(columns={"index": "id"})
    #comparator_df.to_csv("comparators.csv")
    column_values = [
        "obo:RO_0000091{BNode}[0]",
        "obo:RO_0000091{BNode}[1]",
        "obo:RO_0000091{BNode}[2]",
        "obo:RO_0000091{BNode}[3]",
        "obo:RO_0000091{BNode}[4]",
        "obo:RO_0000091{BNode}[5]",
        "obo:RO_0000091{BNode}[6]",
        "obo:RO_0000091{BNode}[7]",
        "obo:RO_0000091{BNode}[8]",
        "obo:RO_0000091{BNode}[9]",
        "obo:RO_0000091{BNode}[10]",
    ]
    column_values1 =[
      "RegardingComparator",
    ]
    column_values2 =[
      "RegardingMeasure",
    ]

    reference_df = contender_messages_df.filter(
        [
            "id",
            "rdf:type{URIRef}",
            "slowmo:RegardingComparator{BNode}",
            "slowmo:RegardingMeasure{BNode}",
        ],
        axis=1,
    )
    reference_df2 = comparator_df.filter(
        [
            "id",
            "http://example.com/slowmo#ComparisonValue{Literal}(xsd:double)",
            "http://schema.org/name{Literal}"
        ],
        axis=1,
    )
    reference_df3 = measures_df.filter(
        [
            "id",
            "dcterms:title{Literal}",
            "http://schema.org/identifier{Literal}"
        ],
        axis=1,
    )
    

    meaningful_messages_df = contender_messages_df[
        contender_messages_df["slowmo:AncestorPerformer{Literal}"].notna()
    ]
    #reference_df1 = reference_df.dropna()
    reference_df1 = reference_df
    RegardingComparator = []
    RegardingMeasure = []
    disposition = []
    values = []
    
    for rowIndex, row in meaningful_messages_df.iterrows():  # iterate over rows
        b = 0
        for columnIndex, value in row.items():
            if columnIndex in column_values:
                a = reference_df1.loc[reference_df1["id"] == value]
                if not a.empty:
                    if b == 0:
                        a.reset_index(drop=True, inplace=True)
                        disposition.append(a["rdf:type{URIRef}"][0])
                        values.append(value)
                        RegardingComparator.append(
                            a["slowmo:RegardingComparator{BNode}"][0]
                        )
                        RegardingMeasure.append(a["slowmo:RegardingMeasure{BNode}"][0])
                        b = b + 1
    meaningful_messages_df["RegardingComparator"] = RegardingComparator
    meaningful_messages_df["RegardingMeasure"] = RegardingMeasure


    meaningful_messages_df["disposition"] = disposition
    meaningful_messages_df["reference_values"] = values
    intermediate_messages_final = meaningful_messages_df.filter(
        [
            "id",
            "slowmo:AncestorPerformer{Literal}",
            "slowmo:AncestorTemplate{Literal}",
            "disposition",
            "reference_values",
            "rdf:type{URIRef}",
            "psdo:PerformanceSummaryDisplay{Literal}",
            "psdo:PerformanceSummaryTextualEntity{Literal}",
            "RegardingComparator",
            "RegardingMeasure",
            "slowmo:acceptable_by{URIRef}[0]",
            "slowmo:acceptable_by{URIRef}[1]",
        ],
        axis=1,
    )
    #intermediate_messages_final.to_csv("intermediate.csv")
    
    # with_comparator_0 =[]
    # with_comparator_1 =[]
    title=[]
    identifier_1=[]
    comparison_value =[]
    name=[]
    comparison_id=[]
    for rowIndex, row in intermediate_messages_final.iterrows():  # iterate over rows
       for columnIndex, value in row.items():
         if columnIndex in column_values1:
          a = reference_df2.loc[reference_df2["id"] == value]
          if not a.empty:
            a.reset_index(drop=True, inplace=True)
    #         #with_comparator_0.append(a["slowmo:WithComparator{BNode}[0]"][0])
    #         #with_comparator_1.append(a["slowmo:WithComparator{BNode}[1]"][0])
    #         #title.append(a["dcterms:title{Literal}"][0])
    #         #identifier_1.append(a["http://schema.org/identifier{Literal}"][0])
            comparison_id.append(a["id"][0])
            comparison_value.append(a["http://example.com/slowmo#ComparisonValue{Literal}(xsd:double)"][0])
            name.append(a["http://schema.org/name{Literal}"][0])
            
    # #intermediate_messages_final["with_comparator_0"] = with_comparator_0
    # #intermediate_messages_final["with_comparator_1"] = with_comparator_1
    # #intermediate_messages_final["title"] = title
    # #intermediate_messages_final["Measure Name"] = identifier_1
    intermediate_messages_final["comparison_value"] = comparison_value
    intermediate_messages_final["name"]=name
    intermediate_messages_final["comparison_id"]=comparison_id
    # #meaningful_messages_df["disposition"] = disposition
    # #meaningful_messages_df["reference_values"] = values
    for rowIndex, row in intermediate_messages_final.iterrows():  # iterate over rows
      for columnIndex, value in row.items():
        if columnIndex in column_values2:
          a = reference_df3.loc[reference_df3["id"] == value]
          if not a.empty:
            a.reset_index(drop=True, inplace=True)
    #         with_comparator_0.append(a["slowmo:WithComparator{BNode}[0]"][0])
    #         with_comparator_1.append(a["slowmo:WithComparator{BNode}[1]"][0])
            title.append(a["dcterms:title{Literal}"][0])
            identifier_1.append(a["http://schema.org/identifier{Literal}"][0])
    #         #comparison_value.append(a["slowmo:ComparisonValue{Literal}(xsd:double)"][0])
    #         #name.append(a["http://schema.org/name{Literal}"][0])
            
    # intermediate_messages_final["with_comparator_0"] = with_comparator_0
    # intermediate_messages_final["with_comparator_1"] = with_comparator_1
    intermediate_messages_final["title"] = title
    intermediate_messages_final["Measure_Name"] = identifier_1
    # #intermediate_messages_final["comparison value"] = comparison_value
    # #intermediate_messages_final["name"]=name
           
    #intermediate_messages_final.to_csv("intermediate1.csv")
     
    meaningful_messages_final = intermediate_messages_final.filter(
        [
            "id",
            "slowmo:AncestorPerformer{Literal}",
            "slowmo:AncestorTemplate{Literal}",
            "disposition",
            "reference_values",
            "rdf:type{URIRef}",
            "psdo:PerformanceSummaryDisplay{Literal}",
            "psdo:PerformanceSummaryTextualEntity{Literal}",
            "slowmo:acceptable_by{URIRef}[0]",
            "slowmo:acceptable_by{URIRef}[1]",
            "RegardingMeasure",
            "comparison_value",
            "comparison_id",
            "name",
            "title",
            "Measure_Name"

        ],
        axis=1,
    )
    #meaningful_messages_final.to_csv("final_list.csv")
    logging.critical("transforming--- %s seconds ---" % (time.time() - start_time))
    # return contender_messages_df
    return meaningful_messages_final