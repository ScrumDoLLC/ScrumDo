$(document).ready( function() {
    loadTodo();
    loadDoing();
    loadDone();
    loadReviewing();    
    
    $( ".scrum_board_list" ).sortable({
		connectWith: ".scrum_board_list",
        placeholder: "ui-board-state-highlight" ,
        opacity: 0.6,
        cancel: ".board_story_body"
	});
	
	
} );

function loadColumn( column_div, story_type )
{
    $.ajax({
    url: "/projects/project/" + project_slug + "/stories/" + iteration_id + "/board/" + story_type ,
    success: function(responseText){            
            $( column_div ).html(responseText);                
         } // end success function
    });
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