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

LoadData()

// Event handlers
window.addEventListener("wheel", wheelfunc);

// Functions
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
    console.log("in displayData")
    const htmlString=data.map((data)=>{
        return `
        <li class="card">
                <div class="card-img">
                    <img src=${data.PicURL}>
                </div>
                <div class="card-details">
                    <div class="card-title">${data.ProductName}</div>
                    <div class="card-list">
                        <a href=${data.PCHProductURL}>
                            <div class="market-img">
                                <img src="https://av.sc.com/tw/content/images/pchome_logo_400x400.jpg">
                            </div>
                            <div class="price">
                                ${data.PCHCurrentPrice}
                            </div>
                        </a>
                        <a href=${data.ProductURL}>
                            <div class="market-img">
                                <img src="https://mylazyweb.com/wp-content/uploads/thumbs_dir/%E6%87%B6%E4%BA%BA%E7%B6%B2-momo%E8%B3%BC%E7%89%A9-Logo-Large-1y1g1m7w385cqumoumxip7iy5c8c81bj9iteituevvvo.png">
                            </div>
                            <div class="price">
                                ${data.CurrentPrice}
                            </div>
                        </a>
                    </div>
                </div>
            </li>
        `;
    })
    .join('');

    if(page-1==0){
        CompareList[0].innerHTML =  htmlString;
    }else{
        oldString = CompareList[0].innerHTML;
        CompareList[0].innerHTML = oldString+htmlString;
    }
}
function LoadData(){
    isLoading=true;
    fetch("/api/compare" + queryString+"&page="+page).then(function (res) {
        return res.json();
    }).then(function (data) {
        isLoading=false;
        console.log(data)
        console.log(data.length)
        if (data.length > 10) {
            page++;
            console.log(page);
        } else {
            lastPage = true;
            console.log(page)
            console.log("final page!")
        }
        displayData(data.splice(0, 10));
    })
}

