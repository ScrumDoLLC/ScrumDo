
function generateBurnDown( divID, projectSlug, iterationID , delay)
{
  setTimeout( "realGenerateBurnDown( '" + divID + "','" + projectSlug + "','" + iterationID + "')" , delay * 1000);
}

function weekendAreas(axes) {
    var markings = [];
    var d = new Date(axes.xaxis.min);
    // go to the first Saturday
    d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 1) % 7))
    d.setUTCSeconds(0);
    d.setUTCMinutes(0);
    d.setUTCHours(0);
    var i = d.getTime();
    do {
        // when we don't set yaxis, the rectangle automatically
        // extends to infinity upwards and downwards
        markings.push({ xaxis: { from: i, to: i + 2 * 24 * 60 * 60 * 1000 } });
        i += 7 * 24 * 60 * 60 * 1000;
    } while (i < axes.xaxis.max);

    return markings;
}

function plotBurndown( divID, series, options)
{
  if(series[0].data.length > 0)
  {
      $.plot($(divID), series, options);
  }
  else
  {
    $(divID).addClass("noData");
    $(divID).html("Not enough data"); // No data
    $(divID).hide(true);
  }
}

function realGenerateBurnDown(  divID, projectSlug, iterationID )
{
  var options = {
     colors: ["#2292ff", "#ADD75C"],
     xaxis: { minTickSize: [1, "day"] , mode: "time", timeformat: "%m/%d/%y" },
     grid: { markings: weekendAreas } ,
     legend: {    position: "nw" },
     series: { lines: {   show: true , fill:true  }, 
               points: { radius:5, show: true, fill: true} 
                 }                   
  };
  
  if( iterationID != "null" )
  {
    $.ajax({
        url: "/projects/project/" + projectSlug + "/" + iterationID + "/burndown",
        method: 'GET',
        dataType: 'json',
        success: function(series) {   plotBurndown( divID, series, options);   }
      });    
  }
  else
  {
    $.ajax({
        url: "/projects/project/" + projectSlug + "/burndown",
        method: 'GET',
        dataType: 'json',
        success: function(series) {    plotBurndown( divID, series, options);    }
      });
  }
}


