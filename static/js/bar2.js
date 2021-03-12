//HorizontalBar
var ctx3 = document.getElementById('barChart2').getContext('2d');

 data3 = {
   datasets: [{
   backgroundColor: ["rgba(12, 99, 132, 0.35)","rgba(204, 255, 204, 0.35)","rgba(255, 204, 153, 0.35)","rgba(51, 51, 255, 0.35)","rgba(102, 102, 255, 0.35)"],
   data:[10,15,18,20,30],
   borderWidth: 3,
   minBarLength: 1,
 }],
 labels: [
     'Product A',
     'Product B',
     'Product C',
     'Product D',
     'Product E'
 ]

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
          min: 0
        }
      }],
    }

    }

});
