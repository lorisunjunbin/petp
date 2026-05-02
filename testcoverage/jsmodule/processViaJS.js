'use strict';
(parameters) => {

    parameters.jsKey = 'jsVal';
    parameters.jsKey1 = 'jsVal1';
    let result = {};
    for (let k in parameters) {
        result[k] = parameters[k];
    }
    result['JSKey'] = 'JSVal';

    return result;
};