
function setupAutoClose( divID )
{  
  setTimeout( "$('body').one('click',function() { $(\"" + divID + "\").fadeOut(100); });" , 100);
}

function setStatus(storyID, project_slug, status, return_type)
{
    $(".todoButtons").hide();
    
    $.ajax({
	    url: "/projects/project/" + project_slug + "/story/" + storyID + "/set_" + status,
		type: "POST",
		data: ({return_type : return_type}),
		success: function(responseText) {
		$("#story_" + storyID).replaceWith(responseText);
		setUpStoryLinks();
	    }
	});
		
}


// When a page loads one or more story blocks, this function gets called to set up all of the links
// inside that block.  
function setUpStoryLinks() 
{

    // When the little comment icon is clicked, hide it and show the comment form
    $(".commentLink").click(function()
    {
        $(this).parent().children(".commentForm").show();
        $(this).hide();
        return false;
    });

    // When the comment form is submitted, invoke the filter button so the iteration reloads on the iteration page.
    $(".commentForm form").ajaxForm(
    {
        success: function(responseText, statusText, xhr, obj) {
            $("#filter_button").submit();
        }
    });

    // When the comment response form is submitted, invoke the filter button so the iteration reloads on the iteration page.
    $(".responses form  ").ajaxForm(
    {
        success: function(responseText, statusText, xhr, obj) {
            $("#filter_button").submit();
        }
    });

    // Set up the move-iteration button
    $(".moveIterationIcon").click(function(event)
    {
        var pos = $(this).offset();
        var width = $(this).width();

        //show the menu directly over the placeholder
        $("#subIterationList").css({
            "left": (pos.left + width) + "px",
            "top": pos.top + "px"
        });
        $("#subIterationList").fadeIn(100);

        current_story_popup = $(this).attr("story_id");

        $('body').one("click",
        function() {
            $("#subIterationList").fadeOut(100);
        });

        return false;
    });

    // Make sure all the tooltips will work with some good positioning.
    $(".storyIcons img").tipTip({
        delay: 100,
        edgeOffset: 10
    });
    
    // When someone clicks an add-task link, show the form.  
    $(".tasks_add_task_link a").click(function(){
        $(this).parent().parent().children(".tasks_add_task_form").show();        
        $(this).hide();
        return false;
    });
    
    // When someone uses the add task form, handle the result well.
    $(".tasks_add_task_form").submit(function(){
        form = $(this);
        
        storyID = $(this).find("input[name='story_id']").val();
        $.ajax({
          type:"POST",
          url: "/projects/task/create",
          data: form.serialize(),
          success: function(responseText){
             $("#story_" + storyID).replaceWith(responseText);
             setUpStoryLinks();
             $("#story_" + storyID).find(".tasks_add_task_link").hide();
             $("#story_" + storyID).find(".tasks_add_task_form").show();       
             $("#story_" + storyID).find(".tasks_add_task_form input[type='text']").focus();                    
          }
        });
        
        
        return false;
    });

}