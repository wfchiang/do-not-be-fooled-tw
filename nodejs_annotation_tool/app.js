'use strict';


// Create an express app 
const express = require('express');
const path = require('path');

const {BigQuery} = require('@google-cloud/bigquery');

const app = express();
app.set('view engine', 'ejs'); 
app.use(express.json()); 

const bigquery = new BigQuery() 


// Bigquery functions 
async function bq_query() {
    console.log("bq_query started"); 

    const query = 'SELECT * FROM \`wfchiang-dev.do_not_be_fooled_tw.2021_10_19_setn\` LIMIT 1';

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
            console.log('>> begin <<'); 
            console.log(rows);
            console.log('>> end <<');
            // res.render(
            //     'index.ejs', 
            //     {}
            // );
            res.render(
                'list.ejs', 
                {
                    hostname: req.hostname, 
                    rows: rows 
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

    console.log('bq_query jon scheduled'); 
});


app.post('/update', (req, res) => {
    console.log('endpoint /update called...'); 
    
    let req_json = req.body; 
    console.log(req_json); 

    res.json({
        message: 'done'
    }); 
});


// Start the server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`App listening on port ${PORT}`);
    console.log('Press Ctrl+C to quit.');
});


// Export 
module.exports = app;