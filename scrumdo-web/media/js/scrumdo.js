
function setupAutoClose( divID )
{  
  setTimeout( "$('body').one('click',function() { $(\"" + divID + "\").fadeOut(100); });" , 100);
}