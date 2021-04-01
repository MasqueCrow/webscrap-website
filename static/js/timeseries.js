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


var minDate = date[0];
var maxDate = date[date.length-1]

//Add one day to min and max date
var newMinDate =  new Date(minDate);
newMinDate.setDate(newMinDate.getDate()+1);
//to retrieve the new date use in string
minDate = [newMinDate.getFullYear(),newMinDate.getMonth()+1,newMinDate.getDate()].join('-');

var newMaxDate = new Date(maxDate);
newMaxDate.setDate(newMaxDate.getDate()+1);
//to retrieve the new date use in string
maxDate = [newMaxDate.getFullYear(),newMaxDate.getMonth()+1,newMaxDate.getDate()].join('-');

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
  range: [, date[date.length-1]],
  type: 'date'
  },

  yaxis: {
  //autorange: true,
  range: [minDate,maxDate],
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
