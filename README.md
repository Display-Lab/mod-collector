# mod-collector
This Repository is python codebase that calculates gap size and trend slopes. This was designed with the intention being included in the PFP pipeline

## Install the mod-collector package globally

```sh
pip install mod[/path/or/url/to/mod-collector-0.1.0-py3-none-any.whl]
```

## Installing the Mod-Collector package in development mode

```sh
pip install -e [path/to/module/displaylab/mod-collector/python]
```
example

```sh
pip install -e /Users/uniquename/display-lab/mod-collector/mod_collector
```

## Running the Mod-Collector script 
```sh
 python -m mod_collector.mod_collector [/path/to/spek_tp.json][/path/to/1_performers_all_measures.csv]
```

## Running the pfp pipeline (pfp.sh)
Note: This assumes that you installed the pfp pipeline installed and you have installed the esteemer package

```sh
cd $DISPLAY_LAB_HOME/vert-ramp-affirmation/vignettes/aspire
./$DISPLAY_LAB_HOME/vert-ramp-affirmation/pfp.sh
```
See vert-ramp-affirmation readme docs for more info

## How it works

#### Query inside
```
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
    
```
### Mod-Collector
Mod-Collector calculates the gap-size, trend slope and predicts monotonic,non-monotonic and no-trend.


#### Use (in progress):
Options:
- `-h | --help` print help and exit
- `-p | --pathways` path to causal pathways
- `-s | --spek` path to spek file (default to stdin)



#### Default Mod-Vollector Criteria
Mod-Collector calculates the gap-size, trend slope and predicts monotonic,non-monotonic and no-trend.


