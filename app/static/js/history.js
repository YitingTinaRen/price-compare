
class showHistory extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div id="history-modal" class="modal">
                <div class="chart-container">
                    <span onclick="closeModal()" class="close" title="Close LoginForm" style="display:none;"><img
                            src="/static/img/icon_close.png/" style="width:16px;height:16px;"></span>
                    <div class="Wait4HisData" style="display:flex;">A minute ...</div>    
                    <canvas id="myChart" class="myChart" style="display:none;"></canvas>
                </div>
            </div>
        `
    }
}
customElements.define('history-tag', showHistory)

let lineChart;
function showChart(event){
    const momoID = event.target.getAttribute('data-arg1');
    const PCHID = event.target.getAttribute('data-arg2');
    let rawTitle = event.target.parentElement.parentElement.parentElement.parentElement.children[0].textContent;
    let chunks=[];
    for(let i=0; i<rawTitle.length;i+=27){
        chunks.push(rawTitle.substring(i,i+27));
    }


    fetch("/api/history?momoID="+momoID+"&PCHID="+PCHID).then(function (res){
        return res.json()
    }).then(function(data){
        const ctx = document.getElementById('myChart')
        console.log(data)

        // Create two datasets
        var PCHData = {
            label: 'PCHome',
            data: data["PCHomeData"],
            borderDash: [5, 5],
            borderColor: `rgb(54, 162, 235)`,
        };

        var MomoData = {
            label: 'Momo',
            data: data["MomoData"],
            borderColor: `rgb(255, 99, 132)`,
        };
        
        let DataSets;
        if (data["PCHomeData"].length >= data["MomoData"].length){
            DataSets = [PCHData, MomoData];
        }else{
            DataSets = [MomoData, PCHData];
        }

        lineChart = new Chart(ctx, {
            type:'line',
            xLabel: '日期', // optional
            yLabel: '$ TWD', // optional
            data: {
                datasets: DataSets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: chunks
                    }
                }
            },
        });

        document.querySelector(".Wait4HisData").style.display = 'none';
        document.querySelector("canvas").style.display = 'flex';
        document.querySelector(".close").style.display = 'flex';
    });
    document.getElementById("history-modal").style.display="flex";
}

function closeModal(){

    document.getElementById('history-modal').style.display = 'none';
    document.querySelector(".Wait4HisData").style.display = 'flex';
    lineChart.destroy();
    document.querySelector("canvas").style.display = 'none';
    document.querySelector(".close").style.display = 'none';

}



