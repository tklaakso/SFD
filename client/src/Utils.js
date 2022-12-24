import React from "react";
import Cookies from 'universal-cookie';

import { MenuItem } from './components/MenuView';

const cookies = new Cookies();

export function isResponseOk(response) {
    if (response.status >= 200 && response.status <= 299) {
        return response.json();
    } else {
        throw Error(response.statusText);
    }
}

export function postJson(addr, data, onError = (err) => {}) {
    return fetch(addr, {
        method: "POST",
        headers: {
            "Content-Type" : "application/json",
            "X-CSRFToken" : cookies.get("csrftoken"),
        },
        credentials: "same-origin",
        body: JSON.stringify(data),
    })
    .then(isResponseOk)
    .catch((err) => {
        onError(err);
        console.log(err);
    });
}

export function getJson(addr, onError = (err) => {}) {
    return fetch(addr, {
        credentials: "same-origin",
    })
    .then(isResponseOk)
    .catch((err) => {
        onError(err);
        console.log(err);
    });
}