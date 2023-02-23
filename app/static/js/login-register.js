//Login form
// When the user clicks anywhere outside of the LoginForm, close it
window.onclick = function (event) {
    if (event.target.classList[0] == "LoginForm") {
        event.target.style.display = "none";
        msgs = document.querySelectorAll("#msg");
        if (msgs.length){
            msgs[0].remove();
            msgs[1].remove();
        }
        document.getElementsByName("uname")[0].value="";
        document.getElementsByName("email")[0].value = "";
        document.getElementsByName("email")[1].value = "";
        document.getElementsByName("psw")[0].value = "";
        document.getElementsByName("psw")[1].value = "";
    }
}

function register() {
    uname = document.getElementsByName("uname")[0].value;
    email = document.getElementsByName("email")[1].value;
    psw = document.getElementsByName("psw")[1].value;
    data = { "name": uname, "email": email, "password": psw };
    console.log(data);

    fetch("/api/user",
        {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }
    ).then(function (res) {
        return res.json();
    }).then(function (result) {
        console.log(result);
        if (result['ok']) {
            success_text = "註冊成功!";
            if (document.querySelectorAll("#id02 .LoginForm-content .form_text").length == 1) {
                referenceNode = document.querySelector("#id02 .LoginForm-content .form_text");
                parentNode = document.querySelectorAll("#id02 .LoginForm-content .container");
                newNode = document.createElement("div");
                newNode.setAttribute("class", "form_text");
                newNode.setAttribute("id", "msg");
                newNode.appendChild(document.createTextNode(success_text));
                parentNode[0].insertBefore(newNode, referenceNode);
            } else {
                document.querySelectorAll("#id02 .LoginForm-content .form_text")[0].textContent = success_text;
            }
        }
        if (result['error']) {
            if (document.querySelectorAll("#id02 .LoginForm-content .form_text").length == 1) {
                referenceNode = document.querySelector("#id02 .LoginForm-content .form_text");
                parentNode = document.querySelector("#id02 .LoginForm-content .container");
                newNode = document.createElement("div");
                newNode.setAttribute("class", "form_text");
                newNode.setAttribute("id", "msg");
                newNode.appendChild(document.createTextNode(result["message"]));
                parentNode.insertBefore(newNode, referenceNode);
            } else {
                document.querySelectorAll("#id02 .LoginForm-content .form_text")[0].textContent = result["message"];
            }
        }
    });
}

function login() {
    email = document.getElementsByName("email")[0].value;
    psw = document.getElementsByName("psw")[0].value;
    data = { "email": email, "password": psw };

    fetch("/api/user/auth",
        {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }
    ).then(function (res) {
        return res.json();
    }).then(function (result) {
        console.log(result);
        if (result['ok']) {
            window.location.reload();
        }
        else if (result['error']) {
            console.log(result);
            if (document.querySelectorAll("#id01 .LoginForm-content .form_text").length == 1) {
                referenceNode = document.querySelector("#id01 .LoginForm-content .form_text");
                parentNode = document.querySelector("#id01 .LoginForm-content .container");
                newNode = document.createElement("div");
                newNode.setAttribute("class", "form_text");
                newNode.setAttribute("id", "msg");
                newNode.appendChild(document.createTextNode(result["message"]));
                parentNode.insertBefore(newNode, referenceNode);
            } else {
                document.querySelectorAll("#id01 .LoginForm-content .form_text")[0].textContent = result["message"];
            }
        }
    });
}

function logout() {
    fetch("/api/user/auth",
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

function showLineHover(){
    document.getElementById("LineBase").src="/static/img/btn_login_hover.png";
}

function showLinePress(){
    document.getElementById("LineBase").src = "/static/img/btn_login_press.png";
}

function showLineBase(){
    document.getElementById("LineBase").src = "/static/img/btn_login_base.png";
}

class loginForm extends HTMLElement{
    connectedCallback(){
        this.innerHTML=`
            <div id="id01" class="LoginForm">
                <div class="LoginForm-content animate">
                    <div class="colorbar"></div>
                    <span onclick="document.getElementById('id01').style.display='none'" class="close" title="Close LoginForm"><img
                            src="/static/img/icon_close.png/" style="width:16px;height:16px;"></span>

                    <div class="container">
                        <div class="form_title">登入會員資料</div>
                        <input type="text" placeholder="登入電子信箱" name="email" required>
                        <input type="password" placeholder="輸入密碼" name="psw" required>

                        <button type="submit" onclick="login()">登入帳戶</button>
                        <div class="form_text">還沒有帳戶？<span id="id03"
                                onclick="document.getElementById('id01').style.display='none';document.getElementById('id02').style.display='flex'">點此註冊</span>
                        </div>
                    </div>
                    <div class="LineLogin">
                        <img style="disply:block" id="LineBase" 
                        onmouseover="showLineHover()" 
                        onmousedown="showLinePress()"
                        onmouseout="showLineBase()"
                        onclick="document.location.href='/api/login'" 
                        src="/static/img/btn_login_base.png"/>
                    </div>
                </div>
            </div>
        `
    }
}

customElements.define('login-form', loginForm)

// Register form
class registerForm extends HTMLElement{
    connectedCallback(){
        this.innerHTML=`
        <div id="id02" class="LoginForm">
            <div class="LoginForm-content animate">
                <div class="colorbar"></div>

                <span onclick="document.getElementById('id02').style.display='none'" class="close" title="Close LoginForm"><img
                        src="/static/img/icon_close.png/" style="width:16px;height:16px;"></span>

                <div class="container">
                    <div class="form_title">註冊會員帳號</div>
                    <input type="text" placeholder="輸入姓名" name="uname" required>
                    <input type="text" placeholder="登入電子信箱" name="email" required>
                    <input type="password" placeholder="輸入密碼" name="psw" required>

                    <button type="submit" onclick="register()">註冊新帳戶</button>
                    <div class="form_text">已經有帳戶了？<span id="id04"
                            onclick="document.getElementById('id01').style.display='flex';document.getElementById('id02').style.display='none'">點此登入</span>
                    </div>
                </div>
            </div>
        </div>
        `
    }
}

customElements.define('register-form', registerForm)