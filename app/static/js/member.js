let page=0;
let lastPage=false;
const CompareList = document.getElementsByClassName("compare-list");
let isLoading=false;

executeAfterCheckAuth();

// Event handlers
window.addEventListener("wheel", wheelfunc);
function wheelfunc() {
    didScroll = true;

    if (didScroll) {
        didScroll = false;

        if ((window.innerHeight + window.scrollY) + 100 >= document.querySelector(".content-frame").offsetHeight + document.querySelector(".content-frame").offsetTop) {
            if (!isLoading & !lastPage) { getMemberData(); }
        }
    }
}

// functions
async function executeAfterCheckAuth(){
    const Auth=await checkAuth();
    if(isLogin){
        getMemberData();
    }else{
        document.querySelector(".compare-list>span").textContent="請登入！"
    }
}

function getMemberData(){
    isLoading=true;
    fetch('/api/member?page='+page).then(function(res){
        return res.json();
    }).then(function(data){
        isLoading=false;
        // console.log(data)
        if(data.TrackProduct){
            if (page == 0) {
                profilePic = document.querySelector('.profile-pic');
                img = document.createElement('img');
                img.setAttribute('src', data.result[0]['ProfilePic']);
                profilePic.appendChild(img);
                nameTage = document.querySelector('.member-name span');
                nameTage.textContent = data.result[0]['Name'];
            }
            page++;
            if(data.result.length<=10){
                lastPage=true;
            }
            if (Boolean(document.querySelector(".compare-list>span"))) {
                document.querySelector('.compare-list>span').remove();
            }
            displayData(data.result.splice(0,10));
            if (window.innerHeight >= document.querySelector(".content-frame").offsetHeight + document.querySelector(".content-frame").offsetTop) {
                if (!lastPage) {
                    LoadData();
                }
            }
        }else{
            console.log("no product!")
            if (page == 0) {
                profilePic = document.querySelector('.profile-pic');
                img = document.createElement('img');
                img.setAttribute('src', data.result['ProfilePic']);
                profilePic.appendChild(img);
                nameTage = document.querySelector('.member-name span');
                nameTage.textContent = data.result['Name'];
            }
            document.querySelector(".compare-list>span").textContent="無追蹤商品！";
        }
        
    });
}

const displayData = (data) => {
    const htmlString = data.map((data) => {
        return `
        <li class="card">
                <div class="card-img">
                    <img src=${data.PicURL}>
                </div>
                <div class="card-details">
                    <div class="card-title">${data.ProductName}</div>
                    <div class="card-list">
                        <a href=${data.PCHProductURL} target="_blank">
                            <div class="market-img">
                                <img src="https://av.sc.com/tw/content/images/pchome_logo_400x400.jpg">
                            </div>
                            <div class="price">
                                $${data.PCHCurrentPrice}
                            </div>
                        </a>
                        <a href=${"https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=" + data.ProductID} target="_blank">
                            <div class="market-img">
                                <img src="https://mylazyweb.com/wp-content/uploads/thumbs_dir/%E6%87%B6%E4%BA%BA%E7%B6%B2-momo%E8%B3%BC%E7%89%A9-Logo-Large-1y1g1m7w385cqumoumxip7iy5c8c81bj9iteituevvvo.png">
                            </div>
                            <div class="price">
                                $${data.CurrentPrice}
                            </div>
                        </a>
                        <div class="side-functions">
                            <div>
                                <span class="history-btn" onclick="showChart(event)" data-arg1=${data.ProductID} data-arg2=${data.PCHProductID} >
                                歷史價格
                                </span>
                            </div>
                            <div>
                                <img id="untrackedHeart" onclick="track(event)" src="/static/img/heart_empty.png" data-arg1=${data.ProductID} data-arg2=${data.PCHProductID} data-arg3=${data.TrackingID} />
                                <span id="untracked" class="track-btn"data-arg3=${data.TrackingID} >
                                    追蹤
                                </span>
                                <img id="trackedHeart"  onclick="track(event)" src="/static/img/heart_full.png" data-arg1=${data.ProductID} data-arg2=${data.PCHProductID} data-arg3=${data.TrackingID} />
                                <span id="tracked" class="track-btn"  data-arg3=${data.TrackingID} >
                                    已追蹤
                                </span>
                            </div>
                            <div>
                                <input type="checkbox" name="priceNotify" value="yes" data-arg3=${data.TrackingID} onclick="PriceNotifyCheckbox(event)">
                                <label class="PriceNotify" data-arg3=${data.TrackingID}>
                                    到價通知
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </li>
        `;
    })
        .join('');

    if (page - 1 == 0) {
        CompareList[0].innerHTML = htmlString;
    } else {
        oldString = CompareList[0].innerHTML;
        CompareList[0].innerHTML = oldString + htmlString;
    }
    data.forEach(element => {
        if(element.NotifyBelowTarget){
            let TrackingID=element.TrackingID.toString();
            document.querySelector('input[type="checkbox"][data-arg3="'+TrackingID+'"]').checked=true;
            document.querySelector('.PriceNotify[data-arg3="'+TrackingID+'"]').textContent='低於$'+element.TargetPrice+'通知';
        }
    });
}

function track(event) {
    if (!isLogin) {
        alert("請先登入，再追蹤商品！");
    } else if (event.target.id === 'untrackedHeart') {
        // enable tracking the product!
        const momoID = event.target.getAttribute('data-arg1');
        const PCHID = event.target.getAttribute('data-arg2');
        fetch("/api/trackProduct?momoID=" + momoID + "&PCHID=" + PCHID).then(function (res) {
            return res.json()
        }).then(function (data) {
        })
        event.target.parentElement.querySelector('#trackedHeart').style.display = 'block';
        event.target.parentElement.querySelector('#tracked').style.display = 'block';
        event.target.nextElementSibling.style.display = 'none';
        event.target.style.display = 'none';
    } else {
        // untrack the product!
        const momoID = event.target.getAttribute('data-arg1');
        const PCHID = event.target.getAttribute('data-arg2');
        let yes=confirm("您確定要取消追蹤該商品？");
        if(yes){
            fetch("/api/trackProduct", {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ momoID: momoID, PCHID: PCHID })
            }).then(function (res) {
                return res.json()
            }).then(function (data) {
            })
            event.target.parentElement.querySelector('#untrackedHeart').style.display = 'block';
            event.target.parentElement.querySelector('#untracked').style.display = 'block';
            event.target.nextElementSibling.style.display = 'none';
            event.target.style.display = 'none';
            event.target.parentElement.parentElement.parentElement.parentElement.parentElement.remove();
            if(document.querySelectorAll(".card").length==0){
                span=document.createElement("span");
                span.textContent ="無追蹤商品！";
                CompareList[0].appendChild(span);
            }
        }
    }
}

function PriceNotifyCheckbox(event){
    if(event.target.checked){
        console.log("checked");
        console.log(event.target.getAttribute('data-arg3'));
        showTargetPrice(event);
    }else{
        console.log("unchecked");
        let productTitle = event.target.parentElement.parentElement.parentElement.previousElementSibling.textContent;
        let yes = confirm("您確定要取消該商品之到價通知？");
        if(yes){
            fetch("/api/Notify" ,{
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ TrackingID: event.target.getAttribute('data-arg3'),
                                    ProdTitle:productTitle})
            }).then(function(res){
                return res.json()
            }).then(function(data){
                console.log(data)
            })
            event.target.checked=false;
            event.target.nextElementSibling.textContent="到價通知";
        }
    }


}