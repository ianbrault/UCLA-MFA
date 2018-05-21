/*
 * modal.js
 */

document.addEventListener("click", (e) => {
    function getPasscode() {
        // check URL of active tab
        browser.tabs.query({ 
            currentWindow: true, 
            active: true 
        }).then(tabs => {
            let tabUrl = tabs[0].url
            fetch("http://aef01152.ngrok.io/passcode", {
                method: "GET",
                mode: "cors",
                headers: { "Tab-Url": tabUrl },
            }).then(res => res.text()).then(code => {
                console.log(code)
            })
        }, err => console.error(err))
    }

    if (e.target.classList.contains("button")) getPasscode()
});