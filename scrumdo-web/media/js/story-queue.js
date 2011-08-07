var current_queue_page = 1;
var total_queue_pages = 1;

function reloadStoryQueue() {
    loadPage(current_queue_page);
}

function loadNextPage() {
    if( current_queue_page >= total_queue_pages ) { return; }
    loadPage( current_queue_page + 1);
}

function loadPrevPage() {
    if( current_queue_page <= 1 ) { return; }
    loadPage( current_queue_page - 1);
}

function loadPage( page ) {
    $.ajax({
        url:STORY_QUEUE_URL + page,
        data:{archived:$("#view_ignored").attr("checked") },
        success: function(response) {
            $(".select_all_checkbox").removeAttr("checked");
            $("#story_queue_list").html(response);
            setupCheckedCounter();
        }
    });
}

function setPageNumbers(page_num, total_pages) {
    current_queue_page = page_num;
    total_queue_pages = total_pages
    $("#page_numbers").text(page_num + "/" + total_pages)
    if( page_num > 1 )
    {
        $("#prev_button").removeClass("disabled");        
    }
    else
    {
        $("#prev_button").addClass("disabled");        
    }
    
    if( page_num == total_pages )
    {
        $("#next_button").addClass("disabled");     
    }
    else
    {
        $("#next_button").removeClass("disabled");     
    }
}

function setupCheckedCounter() {
    $("input[type='checkbox']").click(function(){
        $("#selected_count").text( $(".story_queue_selector:checked").length + " stories selected" );
    });
    $("#selected_count").text( $(".story_queue_selector:checked").length + " stories selected" );
}

function ignoreStories() {
    var stories = $.map( $(".story_queue_selector:checked"), function(n){return $(n).attr("story_id");} ).join(",") ;
    $.ajax({
        url: IGNORE_STORY_URL,
        type: "POST",
        data:{ stories:stories },
        success: function() { loadPage(current_queue_page); }        
    });    
}

function importStories() {
    var stories = $.map( $(".story_queue_selector:checked"), function(n){return $(n).attr("story_id");} ).join(",") ;
    $.ajax({
        url: IMPORT_STORY_URL,
        type: "POST",
        data:{ stories:stories },
        success: function() { loadPage(current_queue_page); updatePanel(); }        
    });    
}

$(document).ready( function(){
    reloadStoryQueue();
    $(".select_all_checkbox").click(function(){
        checked = this.checked;                
        $(".story_queue_selector").attr("checked",checked);
    });
    $("#import_story_button").click(importStories);
    $("#ignore_story_button").click(ignoreStories);
    $("#view_ignored").click(reloadStoryQueue);
    $("#prev_button").click(loadPrevPage);
    $("#next_button").click(loadNextPage);
});