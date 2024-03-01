import express from 'express';
import hbs from 'hbs';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import formidable from 'formidable';
import { spawn } from 'child_process';

const app = express();
const port = 3000;

const fileName = fileURLToPath(import.meta.url);
const dirName = path.dirname(fileName);

const form = formidable({
    maxFileSize: 2 * 1024 * 1024,
    keepExtensions: true
});
// path to python script running ATHOI
const script1 = path.join(dirName, 'public', 'python', 'runATHOI.py');
// path to python script running DFHOI
const script2 = path.join(dirName, 'public', 'python', 'runDFHOI.py');
// maximum duration before deleting file
const maxTime = 5 * 60 * 1000;

app.set('view engine', 'html');
app.engine('html', hbs.__express);

app.use(express.static(path.join(dirName, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
    res.render('index');
});

app.post('/find-top', (req, res) => {
    form.parse(req, (err, fields, files) => {
        if (err) return res.status(400).json({
            success: false,
            message: 'Upload file fail, please try again!'
        });

        let file = files.srcFile[0];
        let numHOIs = fields.numHOIs[0];
        let srcFile = file.filepath;
        let desFile = path.join(dirName, 'public', 'files', file.newFilename);

        let process = spawn('python', [script1, srcFile, numHOIs, desFile]);
        setTimeout(() => {
            process.kill();
        }, maxTime);

        process.on('close', (code) => {
            fs.unlinkSync(srcFile);
            if (code == 0) {
                setTimeout(() => {
                    fs.unlinkSync(desFile);
                }, maxTime);
                
                return res.status(200).json({
                    success: true,
                    message: 'Your file is ready, click on it to download!',
                    file: file.newFilename
                });
            }
            res.status(400).json({
                success: false,
                message: 'Process file fail, please try again!'
            });
        });
    });
});

app.post('/mine-itemset', (req, res) => {
    form.parse(req, (err, fields, files) => {
        if (err) return res.status(400).json({
            success: false,
            message: 'Upload file fail, please try again!'
        });

        let file =  files.srcFile[0];
        let minOcp = fields.minOcp[0];
        let srcFile = file.filepath;
        let desFile = path.join(dirName, 'public', 'files', file.newFilename);

        let process = spawn('python', [script2, srcFile, minOcp, desFile]);
        setTimeout(() => {
            process.kill();
        }, maxTime);

        process.on('close', (code) => {
            fs.unlinkSync(srcFile);
            if (code == 0)  {
                setTimeout(() => {
                    fs.unlinkSync(desFile);
                }, maxTime);

                return res.status(200).json({
                    success: true,
                    message: 'Your file is ready, click on it to download!',
                    file: file.newFilename
                });
            }
            res.status(400).json({
                success: false,
                message: 'Proccess file fail, please try again!'
            });
        });
    });
});

app.get('/download/:file&:name', (req, res) => {
    let filePath = path.join(dirName, 'public', 'files', req.params.file);
    let fileName = req.params.name;
    res.download(filePath, fileName, (err) => {
        if (err) res.status(404).send('File Not Found');
    });
});

// handle 404 error
app.use((req, res) => {
    res.status(404).send('Not Found');
});

// handle 500 error
app.use((err, req, res, next) => {
    res.status(500).send('Internal Server Error');
});

app.listen(port, () => {
    console.log(`Server is listening on http://localhost:${port}`);
});