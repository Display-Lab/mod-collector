# Moderators for Digital Feedback Interventions (M-DFI) - Knowledge Object

This knowledge object (KO) contains a collection of moderator functions **specific to digital feedback interventions**.

## Background

**Moderators** are variables that determine the influence of an intervention. Computable moderators are functions that generate a dependent variable that estimates the magnitude of influence a selected intervention will have. Moderators are based on the existing theory around the intervention. For example, in feedback-intervention theory, a moderator may include gap size. This compares an individual�s performance to a comparator. If the individual has a larger gap between their performance and the comparator, the moderator is larger, and thus a feedback intervention may have a greater influence on the individual.

A **causal pathway** represents the relationships among variables and outcomes of interest in a given context. In implementation research, causal pathways specify the structural relationships (a mechanism) between implementation strategies and their outcomes. When applied to implementation strategies, causal pathways attempt to describe the implementation strategy using inputs, moderators, and preconditions that influence the outcome of the strategy.

An **implementation strategy** is a chosen set of behaviors, tasks, or interventions perceived to address barriers and facilitators to behavioral or organizational change.

A **precondition** is a factor that is necessary for a causal pathway to be activated.

## What is in the M-DFI KO?

The M-DFI KO contains a collection of moderators specific to causal pathways of digital feedback interventions, as identified by feedback theory. The packaged moderators in M-DFI can be plugged into computable casual pathway mechanisms to inform the magnitude of the influence of selected characteristics on the feedback intervention represented by the causal pathway.

### Included Moderators:
- Gap size: *Assess the magnitude of influence of the gap between inputs and a comparator. Comparators may include an explicit target/goal comparitor, a benchmark, or peer-based comparators.*
- Trend slope: *Assess the magnitude of influence of the slope trend of inputs. This is a self comparison of inputs over time.*
- Monotonicity prediction: *Assess the magnitude of influence of monotonic & non-monotonic trends of the inputs.*

## API

### Moderator inputs

All moderators in the M-DFI KO function independently of each other. M-DFI requires two inputs:
1. Performance data - a data frame including the following:
- Measures -> the measure captured by the inputs
- Ascribees -> the feedback recipient (the source of inputs) and the comparators
- Performance levels -> ascribee performance on the selected measure
- Time intervals -> the time measures are observed
2. Comparison values - a csv file containing the measure names, comparison values, and comparison type.

### Moderator outputs

The M-DFI KO outputs results from all the included moderators into a single data frame. The output data frame (mod_df) contains the measure name, performance data, comparison type, gap size, trend slope, and monotonicity prediction.

## Running the code

### Sample Client

A sample client is included, to test run M-DFI on sample data. The sample client includes the client application, a sample performance data csv and a comparison values csv. The sample performance data csv is *"1_performers_10_measures_test.csv"*. The sample comparison values csv is *"comparison_values_1.csv"*. To run the sample client:
1. Move the *sample_client* folder to a local directory
2. If you want to test your own performance data and comparison value csv files, place them in the *sample_client* directory. (otherwise use the sample csv files provided)
3. Run *client.py*. The client will ask you for the performance data and comparison value file names. It will output the results of the M-DFI functions as a csv file in the *sample_client* directory.

### Using M-DFI in unique programs and apps

If you are developing a program or application that will utilize the M-DFI functions, the functions can be found directly in the file *calc_gaps_slopes.py*. M-DFI can either be called to as a python module, or inserted directly into the source code for the newly developed program or application.

