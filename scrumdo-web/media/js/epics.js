var load_delay = 0;




function onStoryEdited(event, target_epic)
{
	// Reload the epic containing where the story was.
	var old_epic = $(event.target).parents(".epic_list_item").attr("epic_id");
	if( old_epic )
	{
		reloadEpic( old_epic );
	}
	if( target_epic != "" && target_epic != old_epic)
	{
		// Reload the epic continaing where the story is now
		reloadEpic( target_epic );
	}
}

function onEpicEdited(event)
{
	var epic = $(event.target).attr("epic_id");
	reloadEpic( epic );
	closeOverlay();
}

function setSmallEpics()
{
    $(".epic_story_list").slideUp();
    $(".story_footer").slideUp();
    $(".pointsBox").hide();
    $(".storyIcons").hide();
    $(".story_detail").hide();
    $(".story_block").addClass("story_block_collapsed");
    $(".epic_detail").slideUp();
}
function setMedEpics()
{
    $(".epic_story_list").slideDown();
    $(".story_footer").slideUp();
    $(".pointsBox").hide();
    $(".storyIcons").hide();
    $(".story_detail").hide();
    $(".story_block").addClass("story_block_collapsed");
    $(".epic_detail").slideUp();
}
function setBigEpics()
{
    $(".epic_story_list").slideDown();
    $(".story_footer").slideDown();
    $(".pointsBox").show();
    $(".storyIcons").show();
    $(".story_detail").show();
    $(".story_block").removeClass("story_block_collapsed");
    $(".epic_detail").slideDown();

}

function reloadEpic( epic_id )
{    
    $.ajax({
        url: "/projects/epic/" + epic_id ,       
        success: function(responseText) {
            $("#epic_" + epic_id).html(responseText);
            $("body").trigger("storyListChanged"); 
            $("#epic_" + epic_id).trigger("epicLoaded");
            $("div.epic_list_block[parent_id='" + epic_id + "']").each( function(index,ele){
                load_delay += 100;
                var eid = $(ele).attr("epic_id");
                setTimeout( "reloadEpic('" + eid + "');", load_delay );                
            });
            
            load_delay -= 100;
            load_delay = Math.max(0,load_delay);
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


function setupSortableLists()
{
	$(".epic_story_list").sortable("destroy");
	$(".epic_story_list").sortable({
        tolerance: 'intersect',
        distance: 5,
		dropOnEmpty: true,
        opacity: 0.5,
		greedy: true,
        placeholder: "ui-state-highlight",
        cancel: ".block_story_body",
		connectWith: ".epic_story_list",
		stop: updateBacklogStoryPosition
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

function setupEpicLinks()
{
    $(".add_epic_link").unbind("click");
    $(".add_epic_link").click(function(){
        openOverlayDiv('#add_epic_popup');
        $("#addEpicForm #id_parent").val( $(this).parents(".epic_list_block").attr("epic_id") );
        return false;
    });

    $(".add_story_link").unbind("click");
    $(".add_story_link").click(function(){
        openOverlayDiv("#add_story_popup");
        $("#createdStories").hide();
        $("#addStoryForm #id_epic").val( $(this).parents(".epic_list_block").attr("epic_id") );
        return false;
    });
    
    setUpStoryLinks();
}

$(document).ready(function(){
    setupSortableLists();
    setupEpicLinks();

    $("#size-options").buttonset();
    $("#small_epics").click( setSmallEpics );
    $("#med_epics").click( setMedEpics );
    $("#big_epics").click( setBigEpics );
    $("#story_details").show();
    $("#epic_details").show();    
    $("#loadingIcon").hide();
    $("body").bind("epicListChanged", function(){window.location.reload();} );         
  	$("body").bind("storyListChanged",setupSortableLists);
  	$("body").bind("storyListChanged",setupEpicLinks);
  	$("body").bind("storyEdited", onStoryEdited );
  	$("body").bind("epicEdited", onEpicEdited );
    
});
