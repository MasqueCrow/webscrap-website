myTS = document.getElementById('myTS');

var graphdic = document.getElementById('graphValue').value;

//converts string to object
var graphdic = JSON.parse(graphdic);

//Convert dic to key array and val array
var date = Object.keys(graphdic);
var value = Object.values(graphdic);

var data = [
{
  x: date, //datetime
  y: value, //Frequency of activating web scrape
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
  range: ['2021-01-01', '2021-06-31'],
  type: 'date'
  },

  yaxis: {
  autorange: true,
  range: [0, 50],
  type: 'linear'
}

}; //layout

Plotly.newPlot('myTS', data,layout,{scrollZoom: true});
