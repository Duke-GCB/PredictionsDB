# iMADS [![CircleCI](https://circleci.com/gh/Duke-GCB/iMADS.svg?style=svg)](https://circleci.com/gh/Duke-GCB/iMADS)

Website for searching and creating transcription factor binding predictions/preferences.
Searches predictions and preference data by gene lists and custom ranges.
Creates predictions/preferences for user uploaded DNA sequences.


## Major Components
__Predictions Config File__

imadsconf.yaml - this config file determines what will be downloaded and how prediction/preference database will work

__Predictions Database__

Postgres database contains indexed gene lists, custom user data and predictions/preference data for use by webserver.py

__Database Loading Script__

load.py - downloads files and loads the database based on imadsconf.yaml

__Webserver__

webserver.py serves web portal and API for accessing the 'pred' database

__Database Vacuum Script__

vacuum.py deletes old user data from the 'pred' database

__Web Portal__

Directory portal/ contains the reactjs project that builds static/js/bunde.js for webserver.py to serve.

__Custom Prediction/Preference Worker__

Calculates predictions and preferences for user uploaded sequences.
https://github.com/Duke-GCB/iMADS-worker

## Running

__Deployment__

We use playbook imads.yml from https://github.com/Duke-GCB/gcb-ansible.

__Run via docker-compose__

Download `docker-compose.yml` and `.env_sample`.
Rename `.env_sample` to `.env`
Change DB_PASS_ENV and POSTGRES_PASSWORD to be whatever password you want.
Start the database and webserver.
```
docker-compose up -d
```
Populate the database. (This will take quite a while depending upon imadsconf.yaml)
```
docker-compose run --no-deps --rm web python load.py
```


## Javascript unit tests
Requires mocha and chai.
Setup:
```
cd portal
npm install -g mocha
npm install --dev
```

To run:
```
cd portal
npm run test
```

## Python unit tests
From the root directory run this:
```
nosetests
```
Integration tests are skipped (they are run by circleci).
See tests/test_integration.py skip_postgres_tests for instructions for running them manually.

## Config file updates
Under the `util` directory there is a python script for updating the config file.
It can be run like so:
```
cd util
python create_conf.py
```
This will lookup the latest predictions based on the __DATA_SOURCE_URL__ in create_conf.yaml.
If you want to add a new gene list you will need to update __GENOME_SPECIFIC_DATA__ in create_conf.yaml.

## Data provenance

This database consists of datasets generated using the following programs:

- https://github.com/Duke-GCB/Predict-TF-Binding
- https://github.com/Duke-GCB/Predict-TF-Preference

__Binding Predictions__

Binding predictions were generated for each transcription factor on both fasta-formatted hg19 and hg38 genome assemblies using [predict\_tf\_binding.py](https://github.com/Duke-GCB/Predict-TF-Binding/blob/master/predict_tf_binding.py) in https://github.com/Duke-GCB/Predict-TF-Binding. The work was divided to run the program for each combination of:

- Genome Assembly (hg19, hg38)
- Chromosome (chr1, chr2, chr3, ...)
- Model/core combination (E2f1 GCGC, E2f1 GCGG, E2f4 GCGC, E2f4 GCGG, ...)

Configuration arguments for the model/core combinations are decoded from  [tracks-predictions.yaml](https://github.com/Duke-GCB/TrackHubGenerator/blob/master/yaml/tracks/tracks-predictions.yaml). Each invocation of predict\_tf\_binding.py produced a [BED format](https://genome.ucsc.edu/FAQ/FAQformat#format1) file containing genomic coordinates and the probability (score) that the considered TF will bind at that site.

These per-chromosome and per-model/core files were combined to produce a single [bigBed format](https://genome.ucsc.edu/FAQ/FAQformat#format1.5) file for each transcription factor on each assembly (hg19 E2f1, hg38 E2f1, hg19 E2f4, hg38 E2f4), using a  [CWL](https://commonwl.org) workflow: [bigbed-workflow-no-resize.cwl](https://github.com/Duke-GCB/TrackHubGenerator/blob/master/cwl/bigbed-workflow-no-resize.cwl) in https://github.com/Duke-GCB/TrackHubGenerator/.

The browser tracks are published at http://trackhub.genome.duke.edu/gordanlab/tf-dna-binding-predictions/. Scores from these tracks are ingested using [load.py](load.py).

__Binding Preferences__

Binding Preferences were generated for the pairs of transcription factors in a family, enumerated in [predict-TF-preference.R](https://github.com/Duke-GCB/Predict-TF-Preference/blob/6173ca8e9541df1965aa047c28f803bbdcdf7084/predict-tf-preference.R#L42). The preference data are derived from the prediction data, starting with the [BED format](https://genome.ucsc.edu/FAQ/FAQformat#format1) files generated by predict\_tf\_binding.py.

The collections of per-assembly-chromosome and per-model/core files were fed into [predict-TF-preference.R](https://github.com/Duke-GCB/Predict-TF-Preference/blob/master/predict-tf-preference.R) in https://github.com/Duke-GCB/Predict-TF-Preference.

The preference scores were generated for each of the pairs using a [CWL](https://commonwl.org) workflow: [preference-bigbed-workflow.cwl](https://github.com/Duke-GCB/TrackHubGenerator/blob/master/cwl/preference-bigbed-workflow.cwl) in https://github.com/Duke-GCB/TrackHubGenerator/. This workflow considers the binding prediction at each site, determines preference using predict-TF-preference.R, and filters out insignificant preferences.
This produced a [bigBed format](https://genome.ucsc.edu/FAQ/FAQformat#format1.5) track, containing the preference score at each site.

The browser tracks are published at http://trackhub.genome.duke.edu/gordanlab/tf-dna-preferences/. Scores from these tracks are ingested using [load.py](load.py).
