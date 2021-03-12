var ctx = document.getElementById('doughChart').getContext('2d');
data = {
    datasets: [{
        data: [10, 20, 30,],
        backgroundColor: [
        'rgba(255, 99, 132, 0.35)',
        'rgba(54, 162, 235, 0.35)',
        'rgba(255, 206, 86, 0.35)'
      ],
      hoverBorderColor: [
      'rgba(75, 192, 192, 0.5)',
      'rgba(75, 192, 192, 0.5)',
      'rgba(75, 192, 192, 0.5) ',
      ]
    }],

    // These labels appear in the legend and in the tooltips when hovering different arcs
    labels: [
        'Red',
        'Blue',
        'Yellow'
    ]
};
// And for a doughnut chart
var myDoughnutChart = new Chart(ctx, {
    type: 'doughnut',
    data: data,
    options: {
        maintainAspectRatio: false,
        responsive: false,
        plugins: {
          labels: [/*{
            render: 'label',
            position:'outside',
          },*/
            {
              render:'value',
              // font style, default is defaultFontStyle
              fontSize: 12,
              fontStyle: 'normal',
              // font color, can be color array for each data or function for dynamic color, default is defaultFontColor
              fontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",

            }

      ]
    }
  }
});
