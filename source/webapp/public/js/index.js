// maximum file size to upload
const maxSize = 2 * 1024 * 1024;
// duration of loading effect
const duration = 3 * 1000;

async function findTop() {
    clearTab('tab2');

    let form = document.getElementById('find-top');
    let srcFile = document.getElementById('tab2-srcFile').files[0];
    let numHOIs =  document.getElementById('tab2-numHOIs').value;

    if (!form.checkValidity()) {
        return form.classList.add('was-validated');
    }
    if (srcFile.size > maxSize) {
        return displayMsg('tab2', false, 'Source file size is too big!');
    }
    form.classList.remove('was-validated');
    
    let formData = new FormData();
    formData.append('srcFile', srcFile);
    formData.append('numHOIs', numHOIs);

    showLoading('tab2');
    let res = await fetch('/find-top', {
        method: 'POST',
        body: formData
    });
    let json = await res.json();
    await hideLoading('tab2');

    if (!json.success) {
        return displayMsg('tab2', false, json.message);
    }
    displayMsg('tab2', true, json.message);
    displayFile('tab2', json.file, srcFile.name);
}

async function mineItemset() {
    clearTab('tab3');

    let form = document.getElementById('mine-itemset');
    let srcFile = document.getElementById('tab3-srcFile').files[0];
    let minOcp = document.getElementById('tab3-minOcp').value;

    if (!form.checkValidity()) {
        return form.classList.add('was-validated');
    }
    if (srcFile.size > maxSize) {
        return displayMsg('tab3', false, 'Source file size is too big!');
    }
    form.classList.remove('was-validated');

    let formData = new FormData();
    formData.append('srcFile', srcFile);
    formData.append('minOcp', minOcp);

    showLoading('tab3');
    let res = await fetch('/mine-itemset', {
        method: 'POST',
        body: formData
    });
    let json = await res.json();
    await hideLoading('tab3');

    if (!json.success) {
        return displayMsg('tab3', false, json.message);
    }
    displayMsg('tab3', true, json.message);
    displayFile('tab3', json.file, srcFile.name);
}

function clearTab(tab) {
    document.getElementById(`${tab}-msg`).innerHTML = '';
    document.getElementById(`${tab}-file`).innerHTML = '';
}

function displayMsg(tab, success, msg) {
    let html;
    if (success) {
        html = `<div class="alert alert-success alert-dismissible fade show">
                    <i class="bi bi-check-circle-fill"></i>&ensp;
                    ${msg}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>`;
    } else {
        html = `<div class="alert alert-danger alert-dismissible fade show">
                    <i class="bi bi-exclamation-triangle-fill"></i>&ensp;
                    ${msg}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>`;
    }
    document.getElementById(`${tab}-msg`).innerHTML = html;
}

function displayFile(tab, path, name) {
    let html = `<a href="/download/${path}&${name}" class="text-decoration-none">
                    <img src="/images/text.jpg" width="50">
                    ${name}
                </a>`;
    document.getElementById(`${tab}-file`).innerHTML = html;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showLoading(tab) {
    let loading = document.getElementById(`${tab}-loading`);
    loading.style.display = 'block';
}

async function hideLoading(tab) {
    await sleep(duration);
    let loading = document.getElementById(`${tab}-loading`);
    loading.style.display = 'none';
}

function toTag(id) {
    document.getElementById(id).scrollIntoView();
}