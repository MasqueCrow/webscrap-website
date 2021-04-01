//HorizontalBar
var ctx2 = document.getElementById('barChart').getContext('2d');

var graphArr = document.getElementById('barValue').value;

//converts string to object
var graphArr = JSON.parse(graphArr);

var graphdic = {};

for(var i = 0; i <6;i++){

  var user = graphArr[i]["profile_name"];
  var review = graphArr[i]["number_of_reviews"];
  graphdic[user] = review;
}

//Convert dic to key array and val array
var users = Object.keys(graphdic);
var reviews = Object.values(graphdic);

data2 = {
   datasets: [{
   backgroundColor: ["rgba(215, 99, 132, 0.35)","rgba(178, 37, 37, 0.35)","rgba(204, 0, 0, 0.35)","rgba(0, 102, 102, 0.35)","rgba(153, 76, 0, 0.35)"],
   data:reviews,
   borderWidth: 3,
   minBarLength: 1,
 }],
 labels: users
 };

var myBarChart = new Chart(ctx2, {
type: 'horizontalBar',
data: data2,
options: {
        title: {
            display: true,
            text: 'Top 5 Users Contribution to Product Review',
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
