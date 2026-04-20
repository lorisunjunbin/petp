'use strict';
(params) => {

    params.jsKey = 'jsVal';
    params.jsKey1 = 'jsVal1';
    let result = {};
    for (let k in params) {
        result[k] = params[k];
    }
    result['JSKey'] = 'JSVal';

    return result;
};