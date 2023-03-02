
class targetPrice extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div id="target-price-modal" class="modal">
                <div class="TP-container">
                    <span onclick="closeTPModal(event)" class="close" title="Close LoginForm" id="close-icon" ><img
                            src="/static/img/icon_close.png/" style="width:16px;height:16px;"></span>
                    <div class="card-title" style="width:100%;font-size:1em;"></div>
                    <div style="width:100%;">價格低於<input type="number" name="price" id="TargetPrice" min="0" step="1">會透過line通知您!</div>
                    <div style="font-size:0.2em;margin:5px 0;">請加<strong>PricePick Notify</strong>好友來接收通知(Line ID: <strong>@019vofkv</strong>)</div>
                    <div style="font-size:0.2em;margin: 5px 0;">或者掃描下方QR code來加入好友:</div>
                    <div style="margin:5px 0;"><img style="width:50px;height:50px;margin:0 5px;" src="/static/img/019vofkv.png"></div>
                    <div><button id="button" class="button" onclick="enableNotify(event)">確定</button></div>   
                    
                </div>
            </div>
        `
    }
}
customElements.define('target-price-tag', targetPrice)

function showTargetPrice(event){
    let productTitle = event.target.parentElement.parentElement.parentElement.previousElementSibling.textContent;
    document.querySelector(".TP-container>.card-title").textContent=productTitle;
    document.querySelector(".button").setAttribute("data-arg3", event.target.getAttribute("data-arg3"));
    document.getElementById("target-price-modal").style.display='flex';
}

function closeTPModal(event) {
    let TrackingID = document.querySelector(".button").getAttribute("data-arg3");
    document.getElementById('target-price-modal').style.display = 'none';
    document.querySelector(".button").setAttribute("data-arg3","");
    document.getElementById("TargetPrice").value="";
    console.log(event.target);
    if(event.target.nodeName !=="BUTTON"){
        document.querySelector('input[type="checkbox"][data-arg3="' + TrackingID + '"]').checked = false;
    }
}

function enableNotify(event){
    let TargetPrice=document.getElementById("TargetPrice").value;
    let ProductTitle = document.querySelector(".TP-container>.card-title").textContent;
    console.log(TargetPrice)
    fetch("/api/Notify?TrackingID="+event.target.getAttribute("data-arg3")+"&TargetPrice="+TargetPrice+"&ProdTitle="+ProductTitle).then(function(res){
        return res.json()
    }).then(function(data){
        console.log(data);
    });
    TrackingID=event.target.getAttribute("data-arg3");
    document.querySelector('input[type="checkbox"][data-arg3="' + TrackingID + '"]').checked = true;
    document.querySelector('.PriceNotify[data-arg3="' + TrackingID + '"]').textContent = '低於$' + TargetPrice + '通知';
    closeTPModal(event);
}




