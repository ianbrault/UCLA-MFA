/*
 * modal.js
 */

document.addEventListener("click", (e) => {
    function getPasscode() {
        // hide button & display spinner
        document.getElementById("button").className = "hidden"
        document.getElementById("spinner").className = "spinner"
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
                // hide spinner, display MFA passcode
                document.getElementById("spinner").className = "hidden"
                codeNode = document.createElement("p")
                codeNode.className = "passcode"
                codeNode.innerHTML = code
                document.getElementById("content").appendChild(codeNode)
            })
        }, err => console.error(err))
    }

    if (e.target.classList.contains("button")) getPasscode()
});