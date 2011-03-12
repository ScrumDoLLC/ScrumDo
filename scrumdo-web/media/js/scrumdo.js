
function setupAutoClose( divID )
{  
  setTimeout( "$('body').one('click',function() { $(\"" + divID + "\").fadeOut(100); });" , 100);
}

function setStatus(storyID, project_slug, status, return_type)
{
    $(".todoButtons").hide();
    if(typeof reloadStoryCallback == 'function') { reloadStoryCallback(); }
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

function showTaskEditForm( task_id )
{
    $.ajax({
	    url: "/projects/task/" + task_id + "/edit",
		type: "GET",
		success: function(responseText) {
    		$("#task_" + task_id).html(responseText);
    		$("#task_" + task_id + " input[type='text']").focus();
    		story_id = $("#edit_task_" + task_id).find("input[name='story_id']").val();
    		$("#edit_task_" + task_id).ajaxForm(
            {
                success: function(responseText, statusText, xhr, obj) {
                    reloadStory(story_id, false, true);
                }
            });
	    }
	});
}

function deleteTask( story_id, task_id )
{
    if( ! confirm("Do you wish to delete this task?") )
    {
        return;
    }
 
    if(typeof reloadStoryCallback == 'function') { reloadStoryCallback(); }   
    $.ajax({
	    url: "/projects/task/" + task_id + "/delete",
		type: "POST",
		success: function(responseText) {
		    reloadStory(story_id, false, true);
	    }
	}); 
}

function setTaskStatus(story_id, task_id, status)
{

    if(typeof reloadStoryCallback == 'function') { reloadStoryCallback(); }
    $.ajax({
	    url: "/projects/task/" + task_id + "/set_status",
		type: "POST",
		data: ({status : (status==1 ? "notdone" : "done" ) }),
		success: function(responseText) {
		    reloadStory(story_id, false, true);
	    }
	});
}

function showTasksForStory( story_id , animate)
{
    if( (animate == null) || animate )
    {
        $("#story_" + story_id + " .task_section").toggle(150);    
    }
    else
    {
        $("#story_" + story_id + " .task_section").toggle();    
    }
}

function showCommentsForStory( story_id , animate)
{
    if( (animate == null) || animate )
    {
        $("#story_" + story_id + " .comment_section").toggle(150);    
    }
    else
    {
        $("#story_" + story_id + " .comment_section").toggle();    
    }
    
    $("#story_" + story_id + " .comment_section form").unbind("submit");
    $("#story_" + story_id + " .comment_section form").submit(function() {
        form = $(this);
        $.ajax({
          type:"POST",
          url: form.attr("action"),
          data: form.serialize(),
          success: function(responseText){
             reloadStory(story_id, true, false);
          }          
        });
        return false;
    });
      
}

function reloadStory( story_id , display_comments, display_tasks)
{
    $.ajax({
	    url: "/projects/story/" + story_id,
		type: "GET",
		success: function(responseText) {
    		$("#story_" + story_id).replaceWith(responseText);
    		setUpStoryLinks();
    		
    		if( display_tasks ) { showTasksForStory( story_id , false);}
    		if( display_comments ) { showCommentsForStory(story_id, false);}    		
	    }
	});
    
}


// When a page loads one or more story blocks, this function gets called to set up all of the links
// inside that block.  Since there might be a block already on screen that was previously set up, this
// function always unbinds the handler before adding it, to make sure we only ever get one handler per
// event.
function setUpStoryLinks() 
{

    if(typeof setUpStoryLinksCallback == 'function') { setUpStoryLinksCallback(); }

    
    $(".tasks_task").mouseenter(function() {      
      $(this).find(".task_controls").css("visibility","visible");
    }).mouseleave(function() {
      $(this).find(".task_controls").css("visibility","hidden");
    });
    
    

    // Set up the move-iteration button
    $(".moveIterationIcon").unbind("click");
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
    
    
    // When someone uses the add task form, handle the result well.
    $(".tasks_add_task_form").unbind("submit");
    $(".tasks_add_task_form").submit(function(){
        form = $(this);        
        storyID = $(this).find("input[name='story_id']").val();

        $.ajax({
          type:"POST",
          url: "/projects/task/create",
          data: form.serialize(),
          success: function(responseText){
             reloadStory(storyID, false, true);
             setTimeout( function()
             {
                 $("#story_" + storyID).find(".tasks_add_task_link").hide();
                 $("#story_" + storyID).find(".tasks_add_task_form").show();       
                 $("#story_" + storyID).find(".tasks_add_task_form input[type='text']").focus();                    
                 
             }, 100);
          }
        });
        
        
        return false;
    });

}