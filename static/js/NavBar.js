class NAVBAR extends HTMLElement {
    connectedCallback() {
        this.innerHTML =
            `
        <div class="frame">
            <div class="left" onclick="document.location.href='/'">PricePick
            </div>
            <div class="right">
                <div class="right-item" onclick="">
                    會員登入
                </div>
            </div>

            <div class="dropdown">
                <div class="hamberg-container">
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
                <div class="dropdown-content">
                    <div onclick="">
                        會員登入
                    </div>
                </div>
            </div>

        </div>
        `
    }
}

customElements.define('nav-bar', NAVBAR);