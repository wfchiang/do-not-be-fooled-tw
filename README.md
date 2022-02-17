# do-not-be-fooled-tw 

## User Guide 

### Installation 
```
pip install .
```

### Running the Web Crawler 
```
python -m do_not_be_fooled_tw.main --start-at https://www.setn.com --life-in-sec 3 --output ./20211014_setn.xlsx 
```

### Initializing the Data Sheet 
```
python -m do_not_be_fooled_tw.data.init_data_sheet --input-file ./20220217_setn.csv --output-file ./20220217_setn_init.csv 
```

### Example Entry News Sites 

* SETN: https://www.setn.com/  

* Yahoo News: https://tw.news.yahoo.com/ 

## Dev Note 

### Google Cloud SDK Installation 

In tools... 

```
python install_gsutil.py
```

Set `PATH`: 

```
export PATH=/home/runner/do-not-be-fooled-tw/tools/google-cloud-sdk/bin:$PATH
```

Then 

```
gcloud init --console-only 
```

### Authenticate Dev Nodejs Application 

Download `wfchiang-dev-service-account.json` from GCS... 

```
gsutil cp gs://wfchiang-dev/credentials/wfchiang-dev-service-account.json /home/runner/do-not-be-fooled-tw
```

Once downloaded... 

```
export GOOGLE_APPLICATION_CREDENTIALS=/home/runner/do-not-be-fooled-tw/wfchiang-dev-service-account.json
```

### Run the Dev Nodejs Annotation Tool (Locally)

First authenticate the app. Then... 

```
npm install 
npm start
```