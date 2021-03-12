myTS = document.getElementById('myTS');

var data = [
{
  x: ['2013-10-04 22:23:00', '2013-11-04 22:23:00', '2013-12-04 22:23:00','2013-12-10 22:23:00',
  '2013-12-20 22:23:00','2014-02-04 22:23:00','2014-05-04 22:23:00','2015-05-06 22:23:00',
  '2015-06-10 22:23:00'], //datetime
  y: [1, 3, 6,4,50,18,20,42,32], //Frequency of activating web scrape
  type: 'scatter'
}
];

var layout = {
  title: {
    text: 'WebScrape Activity Timeline',
    font:{
      family:'Helvetica Neue,Helvetica, Arial, sans-serif',
      color: '#6c757d',
      size: 20,
    }
  },
  width: 710,
  height: 400,
  xaxis: {
  range: ['2013-10-01', '2015-05-31'],
  type: 'date'
  },

  yaxis: {
  autorange: true,
  range: [0, 50],
  type: 'linear'
}

}; //layout

Plotly.newPlot('myTS', data,layout,{scrollZoom: true});
