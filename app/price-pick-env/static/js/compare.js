const queryString=window.location.search;

const urlParams=new URLSearchParams(queryString);
const Category=urlParams.get('Category');
const CompareList=document.getElementsByClassName("compare-list");

document.addEventListener('DOMContentLoaded', function () {
    document.getElementsByClassName('category')[0].children[0].textContent = Category;
    document.getElementsByTagName('title')[0].textContent = Category;
}, false);
fetch("/api/compare"+queryString).then(function(res){
    return res.json();
}).then(function(data){
    console.log(data)
    displayData(data);
})


// Functions

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
    CompareList[0].innerHTML=htmlString;
}

