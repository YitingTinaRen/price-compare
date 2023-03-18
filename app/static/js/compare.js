const queryString=window.location.search;

const urlParams=new URLSearchParams(queryString);
const Category=urlParams.get('Category');
const CompareList=document.getElementsByClassName("compare-list");
let isLoading=false;
let didScroll = false;
let page=0;
let lastPage=false;

document.addEventListener('DOMContentLoaded', function () {
    document.getElementsByClassName('category')[0].children[0].textContent = Category;
    document.getElementsByTagName('title')[0].textContent = Category;
}, false);

executeAfterCheckAuth();


// Event handlers
window.addEventListener("wheel", wheelfunc);
// window.addEventListener("click", clickEvent);

// Functions
async function executeAfterCheckAuth(){
    const Auth= await checkAuth();
    if(Auth=='Done'){
        LoadData()
        LoadBrand()
    }
}

function wheelfunc() {
    didScroll = true;
    
    if (didScroll) {
        didScroll = false;
        
        if ((window.innerHeight + window.scrollY)+100 >= document.querySelector(".content-frame").offsetHeight + document.querySelector(".content-frame").offsetTop) {
            if (!isLoading & !lastPage) { LoadData(); }
        }
    }
}

const displayData = (data)=>{
    const htmlString=data.map((data)=>{
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
                        <a href=${"https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code="+data.ProductID} target="_blank">
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
                        </div>
                    </div>
                </div>
            </li>
        `;
    })
    .join('');

    if(page-1==0){
        // console.log("in page-1==0")
        CompareList[0].innerHTML =  htmlString;
    }else{
        oldString = CompareList[0].innerHTML;
        CompareList[0].innerHTML = oldString+htmlString;
    }
}
function LoadData(){
    isLoading=true;
    fetch("/api/compare"+queryString+"&page="+page).then(function (res) {
        return res.json();
    }).then(function (data) {
        isLoading=false;
        if (data.length > 10) {
            page++;
        } else {
            lastPage = true;
            page++;
            // console.log("final page!")
        }
        if(Boolean(document.querySelector(".compare-list>span"))){
            document.querySelector('.compare-list>span').remove();
        }
        displayData(data.splice(0, 10));

        if (window.innerHeight >= document.querySelector(".content-frame").offsetHeight + document.querySelector(".content-frame").offsetTop) {
            if (!lastPage){
                LoadData();
            }
        }
    })
}

function LoadBrand(){
    fetch("/api/brand?Category="+Category).then(function (res) {
        return res.json();
    }).then(function (data) {
        if (Boolean(document.querySelector(".filter-bar>span"))) {
            document.querySelector(".filter-bar>span").remove()
        }
        CreateDOM("#myDropdown", 'a', '', '', '全部');
        data.forEach(element => {
            CreateDOM("#myDropdown", 'a', 'id',element, element);
        });

    })
}

function CreateDOM(parent, DOM,attri_name, attri_value,content){
    ele_parent = document.querySelector(parent);
    ele = document.createElement(DOM);
    
    if (Boolean(attri_value)){
        ele.setAttribute(attri_name, attri_value);
        ele.href = "/compare?Category=" + Category + "&Brand=" + attri_value;
    }else{
        ele.href = "/compare?Category=" + Category ;
    }
    ele.appendChild(document.createTextNode(content));
    ele_parent.appendChild(ele);
}

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
}

function filterFunction() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    div = document.getElementById("myDropdown");
    a = div.getElementsByTagName("a");
    for (i = 0; i < a.length; i++) {
        txtValue = a[i].textContent || a[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            a[i].style.display = "";
        } else {
            a[i].style.display = "none";
        }
    }
}

function track(event){
    if(!isLogin){
        alert("請先登入，再追蹤商品！");
    } else if (event.target.id==='untrackedHeart'){
        // enable tracking the product!
        const momoID = event.target.getAttribute('data-arg1');
        const PCHID = event.target.getAttribute('data-arg2');
        fetch("/api/trackProduct?momoID="+momoID+"&PCHID="+PCHID).then(function(res){
            return res.json()
        }).then(function(data){
        })
        event.target.parentElement.querySelector('#trackedHeart').style.display = 'block';
        event.target.parentElement.querySelector('#tracked').style.display = 'block';
        event.target.nextElementSibling.style.display = 'none';
        event.target.style.display = 'none';
    }else{
        // untrack the product!
        const momoID = event.target.getAttribute('data-arg1');
        const PCHID = event.target.getAttribute('data-arg2');
        fetch("/api/trackProduct",{
            method:'DELETE',
            headers:{
                'Content-Type': 'application/json'
            },
            body:JSON.stringify({momoID:momoID, PCHID:PCHID})
        }).then(function (res) {
            return res.json()
        }).then(function (data) {
            // console.log(data);
        })
        event.target.parentElement.querySelector('#untrackedHeart').style.display = 'block';
        event.target.parentElement.querySelector('#untracked').style.display = 'block';
        event.target.nextElementSibling.style.display = 'none';
        event.target.style.display = 'none';
    }
}

