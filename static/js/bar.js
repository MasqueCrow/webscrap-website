//HorizontalBar
var ctx2 = document.getElementById('barChart').getContext('2d');

 data2 = {
   datasets: [{
   backgroundColor: ["rgba(215, 99, 132, 0.35)","rgba(178, 37, 37, 0.35)","rgba(204, 0, 0, 0.35)","rgba(0, 102, 102, 0.35)","rgba(153, 76, 0, 0.35)"],
   data:[5,4,8,13,10],
   borderWidth: 3,
   minBarLength: 1,
 }],
 labels: [
     'User A',
     'User B',
     'User C',
     'User D',
     'User E'
 ]

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
          min: 0
        }
      }],
    }
    }

});
