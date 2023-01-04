import pandas as pd
import os

#Call input and comparison value csv
performance_data_file_name = " "
while performance_data_file_name == " ":
    performance_data_file_name = input("Name of performance data csv: ")
    try:
        performance_data = pd.read_csv(performance_data_file_name)
    except:
        performance_data_file_name = " "
        print("No such file was found")

comparison_values_file_name = " "
while comparison_values_file_name == " ":
    comparison_values_file_name = input("Name of comparison values csv: ")
    try:
        comparison_values = pd.read_csv(comparison_values_file_name)
    except:
        comparison_values_file_name = " "
        print("No such file was found")


#Call moderator knowledge object
from calc_gaps_slopes import mod_collector

#Call each function from the moderator knowledge object
output_df = mod_collector(performance_data, comparison_values).reset_index(drop=True)

#Return sample outputs
output_file_name_original = "mod_df.csv"
output_file_name_updated = input("File output name: ") 
os.rename(output_file_name_original, output_file_name_updated)
