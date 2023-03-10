//footer
class FOOTER extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
        <div class="new-footer"><span>copy right @ Price Pick</span></div>
        `
    }
}

customElements.define('my-footer', FOOTER);
