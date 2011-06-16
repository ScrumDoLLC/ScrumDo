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
            epic: epic,
            iteration: iteration_id
        }),
        type: "POST",
        success: function() {
            calculateBothPoints();
            $("#loadingIcon").hide();
        }
    });

}
