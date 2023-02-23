fetch("/api/auth").then((response) => { return response.json() }).then(function (auth) {
    if (auth.hasOwnProperty("error")) {
        console.log(auth["errormsg"])
        document.getElementById("logout-btn").style.display = 'none';
        document.getElementById("Linelogin-btn").style.display = 'block';
        return false;
    } else {
        console.log("have auth")
        document.getElementById("logout-btn").style.display = 'block';
        document.getElementById("Linelogin-btn").style.display = 'none';
        return true;
    }
})

function showLineHover() {
    document.getElementById("Linelogin-icon").src = "/static/img/btn_login_hover.png";
}

function showLinePress() {
    document.getElementById("Linelogin-icon").src = "/static/img/btn_login_press.png";
}

function showLineBase() {
    document.getElementById("Linelogin-icon").src = "/static/img/btn_login_base.png";
}

function logout() {
    fetch("/api/auth",
        {
            method: "DELETE",
        }
    ).then(function (res) {
        return res.json();
    }).then(function (result) { 
        console.log(result);
        if (result) {
            window.location.reload();
        }
    });
}


class NAVBAR extends HTMLElement {
    connectedCallback() {
        this.innerHTML =
            `
        <div class="frame">
            <div class="left" onclick="document.location.href='/'">PricePick
            </div>
            <div class="right">
                <div class="right-item" id="logout-btn" onclick="logout()" style="display:none">
                        登出系統
                </div>
                <div class="right-item" id="Linelogin-btn">
                    <img style="height:25px;" id="Linelogin-icon" 
                    onmouseover="showLineHover()" 
                    onmousedown="showLinePress()"
                    onmouseout="showLineBase()"
                    onclick="document.location.href='/api/login'" 
                    src="/static/img/btn_login_base.png"/>
                </div>
            </div>

            <div class="dropdown">
                <div class="hamberg-container">
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
                <div class="dropdown-content">
                    <div class="right-item" id="logout-btn" onclick="logout()" style="display:none">
                            登出系統
                    </div>
                    <div class="right-item" id="Linelogin-btn">
                        <img style="height:25px" id="Linelogin-icon" 
                        onmouseover="showLineHover()" 
                        onmousedown="showLinePress()"
                        onmouseout="showLineBase()"
                        onclick="document.location.href='/api/login'" 
                        src="/static/img/btn_login_base.png"/>
                    </div>
                </div>
            </div>

        </div>
        `
    }
}

customElements.define('nav-bar', NAVBAR);