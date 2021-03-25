myTS = document.getElementById('myTS');

var graphdic = document.getElementById('graphValue').value;

//converts string to object
var graphdic = JSON.parse(graphdic);

//Convert dic to key array and val array
var date = Object.keys(graphdic);
var value = Object.values(graphdic);

//Retrieve width and height of graph container
let width =  myTS.offsetWidth;
let height = myTS.offsetHeight;

//Create custom array func to get min and max value in array
Array.prototype.max = function() {
  return Math.max.apply(null, this);
};

Array.prototype.min = function() {
  return Math.min.apply(null, this);
};

var data = [
{
  x: date, //datetime
  y: value, //Frequency of activating web scrape
  type: 'scatter'
}
];

var layout = {
  title: {
    font:{
      family:'Helvetica Neue,Helvetica, Arial, sans-serif',
      color: '#6c757d',
      size: 20,
    }
  },
  //autosize:true,
  width:  width ,
  height: height * 1.2 ,

  xaxis: {
  range: ['2021-01-01', '2021-06-31'],
  type: 'date'
  },

  yaxis: {
  //autorange: true,
  range: [value.min()-1, value.max()+1],
  type: 'linear'
}

}; //layout


Plotly.newPlot('myTS', data,layout,{scrollZoom: true});

// update the layout to expand to the available size
// when the window is resized
window.onresize = function() {
  let width =  myTS.offsetWidth;
  let height = myTS.offsetHeight;

   Plotly.relayout('myTS', {
    width: width,
    height: height,
   });

};
