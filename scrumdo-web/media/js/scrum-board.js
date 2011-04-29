story_size = 3;

$(document).ready( function() {
    loadTodo();
    loadDoing();
    loadDone();
    loadReviewing();    
    
    $( ".scrum_board_list" ).sortable({
		connectWith: ".scrum_board_list",
        placeholder: "ui-board-state-highlight" ,
        opacity: 0.6,
        cancel: ".board_story_body",
        receive: onDropColumn,
        update: onSortStory        
	});
	
	$( "#scrum-board-options" ).buttonset();
	$("#small_stories").click( setSmallStories );
	$("#med_stories").click( setMedStories );
	$("#big_stories").click( setBigStories );

	
} );

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
    story_size = 1;
}

function setMedStories()
{
    $(".story_footer").show();
    $(".story_detail").hide();
    $(".scrum_board_story_block").css("min-height","25px");
    story_size = 2;
}

function setBigStories()
{
    $(".story_footer").show();
    $(".story_detail").show();    
    $(".scrum_board_story_block").css("min-height","110px")
    story_size = 3;
}

function onSortStory(event, ui)
{
    var ind = ui.item.index();
    var before = "";
    var after = "";
    children = ui.item.parent().children();
    if( ind > 0)
    {
        before = $(children[ind-1]).attr("story_id");
    }
    
    if( children.length > (1+ind) )
    {
        after = $(children[ind+1]).attr("story_id");
    }
    
    $.ajax({
    	    url: "/projects/project/" + project_slug + "/story/" + $(ui.item).attr("story_id") + "/reorder",
    		data:({ action:"reorder", before:before, after:after, iteration:iteration_id, rank_type:"board_rank" }),
    		type: "POST",
    		success: function() {
    		    
    	    }
	    });
}

function onDropColumn(event, ui)
{    
    story_id = ui.item.attr("story_id");
    status = $(event.target).attr("id");
    var url = "/projects/project/" + project_slug + "/story/" + story_id + "/set_" + status;
    $.ajax({
        url: url,
        method: "POST"        
    });
    resizeColumns();
}

function loadColumn( column_div, story_type )
{
    $.ajax({
    url: "/projects/project/" + project_slug + "/stories/" + iteration_id + "/board/" + story_type ,
    success: function(responseText){            
            $( column_div ).html(responseText); 
            resizeColumns();               
         } // end success function
    });
}

function resizeColumns()
{   
    var target = Math.max( $("#board_todo_column ul").innerHeight(), 
                           $("#board_doing_column ul").innerHeight(), 
                           $("#board_done_column ul").innerHeight(), 
                           $("#board_reviewing_column ul").innerHeight(), 800);

    $("#board_todo_column ul").css("min-height", target);
    $("#board_doing_column ul").css("min-height", target);
    $("#board_done_column ul").css("min-height", target);
    $("#board_reviewing_column ul").css("min-height", target);
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