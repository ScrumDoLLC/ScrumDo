function setSmallEpics()
{
    $(".epic_list_holder").slideUp();
    $(".epic_detail").slideUp();
    $(".epicPointsBox").slideUp();
}
function setMedEpics()
{
    $(".epic_list_holder").slideUp();
    $(".epic_detail").slideDown();
    $(".epicPointsBox").slideDown();
}
function setBigEpics()
{
    $(".epic_list_holder").slideDown();
    $(".epic_detail").slideDown();   
    $(".epicPointsBox").slideDown();
}

function reloadEpic( epic_id )
{    
    $.ajax({
        url: "/projects/epic/" + epic_id ,       
        success: function(responseText) {
            $("#epic_" + epic_id).html(responseText);
            $("#epic_" + epic_id + " .show_assigned_stories").click(function(){
               $(this).siblings(".epic_assigned_stories").show();
               $(this).hide();
               return false;
            });
            $("body").trigger("storyListChanged"); 
            $("#epic_" + epic_id).trigger("epicEdited");
            
        }
    });
}


function updateBacklogStoryPosition(event, ui)
 {
    $("#loadingIcon").show();
    
    var ind = ui.item.index();
    var before = "";
    var after = "";
    var epic = ui.item.parent().attr("epic_id");

    children = ui.item.parent().children();
    
    // Try to find the story before/after this one so the sorting algorithm know where this story goes.
    if (ind > 0) { before = $(children[ind - 1]).attr("story_id");  }
    if (children.length > (1 + ind)) { after = $(children[ind + 1]).attr("story_id"); }
    
    if( typeof epic  == "undefined")
    {
        epic = -1;
    }
    
    $.ajax({
        url: "/projects/project/" + project_slug + "/story/" + $(ui.item).attr("story_id") + "/reorder",
        data: ({
            action: "reorder",
            before: before,
            after: after,
            epic: epic
        }),
        type: "POST",
        success: function() {
            $("body").trigger("storyListChanged");
            $("#loadingIcon").hide();
        }
    });

}


function moveCurrentlyOpenStoryToIteration(iteration_id)
 {
    $("#loadingIcon").show();
    var epic_id = $("#story_" + current_story_popup).parent().attr("epic_id");
    $.ajax({
        url: "/projects/project/" + project_slug + "/story/" + current_story_popup + "/reorder",
        data: ({
            action: "move_iteration",
            iteration: iteration_id
        }),
        type: "POST",
        success: function() {
            $("#loadingIcon").hide();
            $("#story_" + current_story_popup).hide(true);
            reloadEpic( epic_id );
        }
    });
}


$(document).ready(function(){
    $( "#size-options" ).buttonset();
    $("#small_epics").click( setSmallEpics );
    $("#med_epics").click( setMedEpics );
    $("#big_epics").click( setBigEpics );
    $("#story_details").show();
    $("#epic_details").show();
    
    $(".add_epic_link").click(function(){
        jQuery.facebox({ div: '#add_epic_popup' });        
        $("#addEpicForm #id_parent").val( $(this).parents(".epic_list_block").attr("epic_id") );
        return false;
    });

    $(".add_story_link").click(function(){
        jQuery.facebox({ div: '#add_story_popup' });        
        $("#addStoryForm #id_epic").val( $(this).parents(".epic_list_block").attr("epic_id") );
        return false;
    });
    
    $(".show_assigned_stories").click(function(){
       $(this).siblings(".epic_assigned_stories").show();
       $(this).hide();
       return false;
    });
         
});
