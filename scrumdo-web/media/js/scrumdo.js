scrumdo_special_tags = [ ];
story_template_type = 'block';

function setupFavoriteLinks()
{
    // $(".favorite_link img").css("opacity","0.2");
    //    $(".favorite_link img").hover(
    //           function()
    //           {
    //               $(this).css("opacity","1")
    //           },
    //           function()
    //           {
    //               $(this).css("opacity","0.2")
    //           }
    //  );

}

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
		$("#story_" + storyID).trigger("storyEdited");
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
    $.ajax({
    url: "/projects/story/" + story_id + "/comments",
    success: function(responseText){
            
            $("#story_comments_" + story_id ).html(responseText);
        
            if( (animate == null) || animate )
            {
                $("#story_comments_" + story_id ).toggle(150);    
            }
            else
            {
                $("#story_comments_" + story_id ).toggle();    
            }

            $("#story_comments_" + story_id + " form").unbind("submit");
            $("#story_comments_" + story_id + " form").submit(function() {
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
         } // end success function
    });
}

function reloadStory( story_id , display_comments, display_tasks)
{
    $.ajax({
	    url: "/projects/story/" + story_id,
		type: "GET",
		data: {story_type:story_template_type},
		success: function(responseText) {
    		$("#story_" + story_id).replaceWith(responseText);    		
    		$("#story_" + story_id).trigger("storyEdited");
    		
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

    $(".tagsBox a").tipTip({
        delay: 100,
        edgeOffset: 10
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

var overlay_div = false;

function sizeOverlay()
{
    $("#scrumdo_overlay input").css("z-index",5001);
    $("#scrumdo_overlay").css("max-height", $(window).height() - 90 + "px");
    $("#scrumdo_overlay").css("left", (($(window).width() - $("#scrumdo_overlay").outerWidth()) / 2) + $(window).scrollLeft() + "px");
}

function openOverlayDiv(div_selector)
{
    var div = $(div_selector);
    overlay_div = true;
    $("body").append("<div id='scrumdo_overlay'><div class='overlay_close'><a href='#'>Close</a></div><div id='overlay_body'></div></div>");
    $("#overlay_body").append(div[0]);
    div.show();
    div.attr("display","block");
    $(".overlay_close").click(function(){
        closeOverlay();
        return false;
    });
    $("#scrumdo_overlay").fadeIn(150);
    sizeOverlay();
    $("#scrumdo_overlay input:first").focus();
}

function openOverlay( url )
{
    overlay_div = false;
    $("body").append("<div id='scrumdo_overlay'><div class='overlay_close'><a href='#'>Close</a></div><div id='overlay_body'>Loading...</div></div>");
    $(".overlay_close").click(function(){
        closeOverlay();
        return false;
    });
    $("#scrumdo_overlay").fadeIn(150);
    $.ajax({
        url: url,
        success: function(data) {            
            $("#scrumdo_overlay #overlay_body").html(data);            
            //$("body").css("overflow", "hidden");
            $("#scrumdo_overlay input:first").focus();
        }
    });
    sizeOverlay();
    
}

function closeOverlay()
{
    $("#scrumdo_overlay").fadeOut(250, function(){
        if( overlay_div )
        {
            var div = $("#overlay_body div:first");
            $("body").append( div[0] );
            div.hide();
        }
        $("#scrumdo_overlay").remove();        
    });
    //$("body").css("overflow", "auto");
}


/**
 * Updates the right hand side panel with number of stories in the iterations and the stats 
 * for this iteration.
 **/
function updatePanel()
 {
    $.ajax({
        url: iteration_list_url,
        type: "GET",
        success: function(responseText) {
            $("#iteration_list").html(responseText);
        }
    });
    $.ajax({
        url: iteration_stats_url,
        type: "GET",
        success: function(responseText) {
            $("#iteration_stats").html(responseText);
        }
    });
}

function setupNewsItemMoreLinks() {
    $(".news-item-more-link").each(function(){
        var link = this;

        $(this).parent().find(".news-body").each(function(){
            var height = $(this).height();
            // alert(height);
            if( height > 90)
            {
                $(this).css("height","60px");
            }
            else
            {
                // The item fits, so don't show the link
                $(link).hide();
            }
        });
    });
    
    $(".news-item-more-link").click(function(){
        $(this).parent().find(".news-body").css("height","");
        $(this).hide();
        return false;
    });
    
}

var AJAX_CALL_ABORTED = false;
function onAjaxError(request, status, error) {
    var errorMsg = "";

    if( AJAX_CALL_ABORTED )
    {
        AJAX_CALL_ABORTED = false;
        return;
    }
    
	if(request.responseText) {
		errorMsg = request.responseText.substr(0,100);
	}
	$(".ajax-error").html("There was an error handling that request.<br/>" + errorMsg )
	$(".ajax-error").slideDown(400);
	
	setTimeout('$(".ajax-error").slideUp(400);',3000);
}

$(document).ready(function() {
    setupFavoriteLinks();
    $("body").bind("storyListChanged", setUpStoryLinks );
    $('body').bind("epicEdited", setUpStoryLinks );    
    $('body').bind("storyEdited", setUpStoryLinks );    
    $(".subIteration").click(function()
    {
        var iteration_id = $(this).attr("iteration_id");
        moveCurrentlyOpenStoryToIteration(iteration_id);
    });
    $(".add_category_link").click(function(){
        $("#id_category").hide();
        $(".add_category_link").hide();
        $(".category_name").show();
        $(".category_name").focus();
        return false;
    });
    
    var page_unloading = false;
    
    $(document).ajaxError(function(request, status, error) {

        if( page_unloading ) {
            return;
        }
        globalErrorHandler = function() { onAjaxError(request, status, error); };
        setTimeout("globalErrorHandler()",2000); // The 2 second delay is a hack to make this not happen when a user navigates away from a page during a request.
		
	});
	
	$(window).unload(function() {
      page_unloading = true;
      $(".ajax-error").hide();
      $(document).unbind('ajaxError');
    });
    
});


// $.ajaxError(function(event, xhr, ajaxOptions, thrownError) 
// {
//   // TODO!
// }); 