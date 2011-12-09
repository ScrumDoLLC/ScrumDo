story_size = 3;

$(document).ready( function() {
    reloadAllColumns();

	$("body").bind("storyListChanged", reloadAllColumns );
    
    $( ".scrum_board_list" ).sortable({
		connectWith: ".scrum_board_list",
        placeholder: "ui-board-state-highlight" ,
        opacity: 0.6,
        cancel: ".board_story_body",
        update: onSortStory        
	});
	
	$( "#scrum-board-options" ).buttonset();
	$("#small_stories").click( setSmallStories );
	$("#med_stories").click( setMedStories );
	$("#big_stories").click( setBigStories );

	
} );

function reloadAllColumns()
{
    loadTodo();
    loadDoing();
    loadDone();
    loadReviewing();
}

function setStorySize()
{
    switch( story_size )
    {
        case 1: setSmallStories(); break;
        case 2: setMedStories(); break;
        case 3: setBigStories(); break;
    }
}

function setSmallStories()
{
    $(".story_footer").hide();
    $(".story_detail").hide();
    $(".scrum_board_story_block").css("min-height","25px");
    $(".task_section").hide();
    $(".tasks_link").hide();
    story_size = 1;
}

function setMedStories()
{
    $(".story_footer").show();
    $(".story_detail").hide();
    $(".scrum_board_story_block").css("min-height","25px");
    $(".task_section").hide();
    $(".tasks_link").hide();    
    story_size = 2;
}

function setBigStories()
{
    $(".story_footer").show();
    $(".story_detail").show();    
    $(".scrum_board_story_block").css("min-height","110px")
    $(".tasks_link").show();    
    story_size = 3;
}

var last_story_sort = null;

function onSortStory(event, ui)
{
    var ind = ui.item.index();
    var before = "";
    var after = "";
    var children = ui.item.parent().children();
    if( ind > 0)
    {
        before = $(children[ind-1]).attr("story_id");
    }
    
    if( children.length > (1+ind) )
    {
        after = $(children[ind+1]).attr("story_id");
    }
    var story_id = $(ui.item).attr("story_id");
    var target_status = $(ui.item).parent().attr("id");
    var unique_key = story_id + target_status + before + after;
    if( last_story_sort == unique_key )
    {
        // Hack... we're getting double entries here on some browsers.  Here's a quick check to avoid that.
        return;
    }
    last_story_sort = unique_key;
    $.ajax({
    	    url: "/projects/project/" + project_slug + "/story/" + story_id + "/scrum_board",
    		data:({ action:"reorder", before:before, after:after, iteration:iteration_id, status:target_status, rank_type:"board_rank" }),
    		type: "POST",
    		success: function() {    
    		    resizeColumns();
    	    }
	    });
}
// 
// function onDropColumn(event, ui)
// {    
//     var story_id = ui.item.attr("story_id");
//     var target_status = $(event.target).attr("id");
//     var url = "/projects/project/" + project_slug + "/story/" + story_id + "/set_" + target_status;
//     $.ajax({
//         url: url,
//         type: "POST"        
//     });
//     
// }

function loadColumn( column_div, story_type )
{
    $.ajax({
    url: "/projects/project/" + project_slug + "/stories/" + iteration_id + "/board/" + story_type ,
    success: function(responseText){            
            $( column_div ).html(responseText); 
            setStorySize();             
            resizeColumns();    
            setUpStoryLinks();          
         } // end success function
    });
}

function resizeColumns()
{   
    var target = Math.max( $("#board_todo_column ul").innerHeight(), 
                           $("#board_doing_column ul").innerHeight(), 
                           $("#board_done_column ul").innerHeight(), 
                           $("#board_reviewing_column ul").innerHeight(), 1000);

    $("#board_todo_column ul.scrum_board_list").css("min-height", target);
    $("#board_doing_column ul.scrum_board_list").css("min-height", target);
    $("#board_done_column ul.scrum_board_list").css("min-height", target);
    $("#board_reviewing_column ul.scrum_board_list").css("min-height", target);
}

function loadTodo()
{
    loadColumn("#board_todo_column ul", "TODO")
}

function loadDoing()
{
    loadColumn("#board_doing_column ul", "Doing")
}

function loadDone()
{
    loadColumn("#board_done_column ul", "Done")
}

function loadReviewing()
{
    loadColumn("#board_reviewing_column ul", "Reviewing")
}