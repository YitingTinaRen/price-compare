let isLogin=false;
let memID=null;

async function checkAuth() {
    try {
        const response = await fetch('/api/auth');
        const auth = await response.json();
        if (auth.hasOwnProperty('error')) {
            // console.log(auth['errormsg']);
            document.getElementById('logout-btn').style.display = 'none';
            document.getElementById('Linelogin-btn').style.display = 'block';
            isLogin = false;
        } else {
            // console.log('have auth');
            memID = auth.data.id;
            // console.log(memID);
            document.getElementById('logout-btn').style.display = 'block';
            document.getElementById('Linelogin-btn').style.display = 'none';
            isLogin = true;
        }
    } catch (error) {
        console.log(error);
    }
    return 'Done'
}

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
        // console.log(result);
        if (result) {
            window.location.reload();
        }
    });
}

function member(){
    if(isLogin){
        window.location.href="/member";

    }else{
        alert("請登入會員！")
    }
}


class NAVBAR extends HTMLElement {
    connectedCallback() {
        this.innerHTML =
            `
        <div class="frame">
            <div class="left" onclick="document.location.href='/'">PricePick
            </div>
            <div class="right">
                <div class="right-item" onclick="member()">
                        會員頁
                </div>
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
                    <div class="right-item" onclick="member()">
                            會員頁
                    </div>
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