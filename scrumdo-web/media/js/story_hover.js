// Handles displaying the hover-story display.  The one the eye icon invokes on the iteration page and
// the iteration planning page.  Make sure to have something like this on your page:
// <div id="story_hover_window" >
//   <div id="story_hover_content">
//   </div>
// </div>
// And set up your hover icons like so:
// $(".hoverDetails").hover( displayStoryHover, hideStoryHover );

 var popupStatus = 0;  
 function displayStoryHover(event)
 {

    if(popupStatus==0)
    { 
      var left_coord = event.pageX - ($("#story_hover_window").width() + 40);
      if( left_coord < 0 )
      {
        left_coord = event.pageX + 30; // don't let it go off the screen to the left.
      }
      
      $("#story_hover_content").html("Loading...");
      $("#story_hover_window").fadeIn("fast");         
      $("#story_hover_window").centerInClient();
      $("#story_hover_window").css('left', left_coord);
 
      story_id = $(this).attr("story_id");
      $.ajax({
        url: "/projects/project/" + project_slug + "/story/" + story_id + "/pretty",
        type: "GET",
        success: function(data) { $("#story_hover_window").html(data); }
      });
      popupStatus = 1;           
    }      
 }
 
 function hideStoryHover()
 {
   $("#story_hover_window").fadeOut("fast");
   popupStatus = 0;
 }