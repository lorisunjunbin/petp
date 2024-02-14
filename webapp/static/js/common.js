function byId(id) {
    return document.getElementById(id);
}

function load() {
    byId('fileList').innerHTML = '';
    $.ajax('api/v1/search/files', {
        dataType: "json",
        type: 'GET',
        data: {q: byId('search').value},
        contentType: 'application/json;charset=utf8',
        success: function (resp) {
            byId('recordcount').innerText = `Found ${resp.length}  file${resp.length > 1 ? 's' : ''}`;
            resp.sort().forEach((url, i) => createRowForm(url, 'f_' + i));
        }
    });
}

function createRowForm(url, formId) {
    let form = document.createElement('form');
    form.id = formId;
    form.action = '/shared' + (url.startsWith('/') ? url : '/' + url);
    form.classList = ['form'];
    form.method = "POST";
    form.target = "_blank";

    let a = document.createElement('a');
    a.innerHTML = url;
    a.href = "javascript:byId('" + form.id + "').submit()";
    form.appendChild(a);

    byId('fileList').appendChild(form);
}

byId("search").addEventListener("keyup", load);
byId('search').value = new URLSearchParams(window.location.search).get('q') || '';
load();