'use strict';


// Create an express app 
const express = require('express');
const path = require('path');

const {BigQuery} = require('@google-cloud/bigquery');

const app = express();
app.set('view engine', 'ejs'); 
app.use(express.json()); 

const bigquery = new BigQuery(); 

const dataTableName = 'wfchiang-dev.do_not_be_fooled_tw.2021_10_19_setn'; 

const dataTableCols = [
    'Anti_China', 
    'Anti_Japan', 
    'Anti_US', 
    'China_Fellow', 
    'Japan_Fellow', 
    'US_Fellow', 
    'Anti_KMT', 
    'KMT_Fellow', 
    'Anti_DPP', 
    'DPP_Fellow', 
    'Anti_Taiwan_Gov', 
    'Taiwan_Gov_Fellow'
]; 


// Bigquery functions 
async function bq_query() {
    console.log("bq_query started"); 

    let query = 'SELECT * FROM \`' + dataTableName + '\` WHERE ' 

    for (var i = 0 ; i < dataTableCols.length ; i++) {
        var c = dataTableCols[i]; 
        query = query + c + ' not in (0, 1) '; 
        if (i != dataTableCols.length-1) {
            query = query + ' OR '; 
        }
    }

    query = query + ' LIMIT 1';

    const options = {
        query: query, 
        location: 'US' 
    }; 

    // Run the query as a job
    const [job] = await bigquery.createQueryJob(options);
    // console.log(`Job ${job.id} started.`);

    // Wait for the query to finish
    const [rows] = await job.getQueryResults();

    // Print the results
    console.log('Rows retrieved');
    // rows.forEach(row => console.log(row));

    console.log("bq_query finished"); 

    return Promise.resolve(rows); 
}

async function bq_update(row_json) {
    console.log("bq_update started"); 

    let query = 'UPDATE \`wfchiang-dev.do_not_be_fooled_tw.2021_10_19_setn\` SET '; 

    for (var i = 0 ; i < dataTableCols.length ; i++) {
        var c = dataTableCols[i]; 
        query = query + c + ' = ' + String(row_json[c]); 
        if (i != dataTableCols.length-1) {
            query = query + ', '; 
        }
    }

    query = query + ' WHERE UUID = \'' + row_json['UUID'] + '\''; 

    const options = {
        query: query, 
        location: 'US' 
    }; 

    // Run the query as a job
    const [job] = await bigquery.createQueryJob(options);
    // console.log(`Job ${job.id} started.`);

    // Wait for the query to finish
    const [rows] = await job.getQueryResults();

    // Print the results
    console.log('Table updated');
    // rows.forEach(row => console.log(row));

    console.log("bq_update finished"); 

    return Promise.resolve(rows); 
}


// Endpoints 
app.get('/ping', (req, res) => {
    res.json({}); 
}); 


// app.get('/', (req, res) => {
//     res.render('index.pug'); 
// });


app.get('/', (req, res) => {
    bq_query()
        .then(rows => {
            var oneRow = rows[0]; 

            oneRow['article'] = oneRow['article'].replace(/\n/i, '<br>');
            
            console.log('Display row UUID: ' + oneRow['UUID']); 
            
            res.render(
                'list.ejs', 
                {
                    hostname: req.hostname, 
                    rows: [oneRow]
                }
            );
        }) 
        .catch(err => {
            console.log(err); 
            res.status(500).render(
                'error.ejs', 
                {
                    message: err 
                }
            );
        }); 

    console.log('bq_query job scheduled'); 
});


app.post('/update', (req, res) => {
    console.log('endpoint /update called...'); 
    
    let req_json = req.body; 
    console.log(req_json); 

    bq_update(req_json)
        .then(rows => {
            console.log('Updated row UUID: ' + req_json['UUID']); 
            res.json({'message': 'ok'}); 
        }) 
        .catch(err => {
            console.log(err); 
            res.status(500).render(
                'error.ejs', 
                {
                    message: err 
                }
            );
        }); 

    console.log('bq_update job scheduled');
});


// Start the server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`App listening on port ${PORT}`);
    console.log('Press Ctrl+C to quit.');
});


// Export 
module.exports = app;