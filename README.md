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

Once download `wfchiang-dev-service-account.json` from GCS... 

```
export GOOGLE_APPLICATION_CREDENTIALS=<KEY_PATH>
```

### Run the Dev Nodejs Annotation Tool (Locally)

First authenticate the app. Then... 

```
npm install 
npm start
```