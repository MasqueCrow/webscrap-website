//HorizontalBar
var ctx3 = document.getElementById('barChart2').getContext('2d');

var graphArr = document.getElementById('bar2Value').value;


//converts string to object
var graphArr = JSON.parse(graphArr);

var graphdic = {};

for(var i = 0; i <5;i++){

  var asin = graphArr[i]["ASIN"];
  var review = graphArr[i]["number_of_reviews"];
  graphdic[asin] = review;
}

//Convert dic to key array and val array
var asin = Object.keys(graphdic);
var reviews = Object.values(graphdic);

 data3 = {
   datasets: [{
   backgroundColor: ["rgba(12, 99, 132, 0.35)","rgba(204, 255, 204, 0.35)","rgba(255, 204, 153, 0.35)","rgba(51, 51, 255, 0.35)","rgba(102, 102, 255, 0.35)"],
   data:reviews,
   borderWidth: 3,
   minBarLength: 1,
 }],
 labels: asin
 };

var myBarChart = new Chart(ctx3, {
type: 'horizontalBar',
data: data3,
options: {
        title: {
            display: true,
            text: 'Top 5 Products with most reviews',
            fontSize: 20,
            fontStyle: 'normal'
        },
        legend: {
       display: false
    },
    maintainAspectRatio: false,
    responsive: false,
    scales: {
      xAxes: [{
        ticks: {
        }
      }],
    }
    }

});
