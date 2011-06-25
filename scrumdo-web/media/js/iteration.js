
/** 
 * Loads an iteration on the iteration and backlog pages.
 **/
function loadIteration(iterationID, page, query_string)
 {
    if (last_load_iter_req)
    {
        // A load request is already pending, so stop it to avoid double loads.
        last_load_iter_req.abort();
    }

    // TODO: Does not work if ScrumDo is deployed to a non-root location.
    last_load_iter_req = $.ajax({
        url: "/projects/project/" + project_slug + "/stories/" + iterationID + "/" + page + "?display_type=block&" + query_string,
        success: function(html) {
            if (page == 1)
            {
                // If we're loading the first page of results, replace anything there.
                $("#story_list").html(html);
            }
            else
            {
                // Otherwise, append it to the end.
                $("#story_list").append(html);
            }
            $("#story_list").attr("iteration_id", iterationID); // We use this attribute occasionally in other places.
            $("#loadingIcon").hide();

            // if we came here with the name of a specific story in the url, scroll to it
            // TODO: it'd be nice to avoid the #hash tag so the page doesn't scroll unexpectedly later.
            if ($(window.location.hash).offset()) {
                $("html,body").animate({
                    scrollTop: $(window.location.hash).offset().top
                })
            }
            
            // Re-setup some facebox stuff.
            $('a[rel*=facebox]').unbind('click.facebox');
            $('a[rel*=facebox]').facebox({
                loadingImage: static_url + 'images/facebox/loading.gif',
                closeImage: static_url + 'images/facebox/closelabel.png'
            });

            setUpStoryLinks();
            $("a.delete").confirm("Are you sure you want to delete this?");            
            $("#story_count").text($("#story_list").children().length + " stories");
        }
    });

    $("#loadingIcon").show();
}



function updateStoryPosition(event, ui)
 {
    if ($(ui.item).attr("draggedOffScreen") == "1")
    {
        // We were getting double sort/drag events sometimes when dragging to a different iteration, this fixes that.
        return;
    }
    $("#loadingIcon").show();

    var ind = ui.item.index();
    var before = "";
    var after = "";
    children = ui.item.parent().children();
    
    // Try to find the story before/after this one so the sorting algorithm know where this story goes.
    if (ind > 0) { before = $(children[ind - 1]).attr("story_id");  }
    if (children.length > (1 + ind)) { after = $(children[ind + 1]).attr("story_id"); }

    $.ajax({
        url: "/projects/project/" + project_slug + "/story/" + $(ui.item).attr("story_id") + "/reorder",
        data: ({
            action: "reorder",
            before: before,
            after: after,
            iteration: iteration_id
        }),
        type: "POST",
        success: function() {
            calculateBothPoints();
            $("#loadingIcon").hide();
        }
    });

}

function filterByTag(tag)
 {
    $("#filterDialog").show();
    $("#tags_input").val(tag);
    $("#filter_button").submit();
}

function calculateBothPoints()
 {
    setUpStoryLinks();
}



$(document).bind('afterReveal.facebox',
function() {
    $("#id_start_date-2").datepicker({
        dateFormat: 'yy-mm-dd'
    });
    $("#id_end_date-2").datepicker({
        dateFormat: 'yy-mm-dd'
    });
});

$(document).bind('reveal.facebox',
function() {
    $('#facebox input').each(function(intIndex) {
        $(this).attr('id', jQuery(this).attr('id') + '-2')
    });
});


/** 
 * Moving a story to an iteration is a 2-step process.  First, display the menu of iterations to pick form,
 * and then actually move it when the user selects one.  This function handles the second step.
 **/
function moveCurrentlyOpenStoryToIteration(iteration_id)
 {
    $("#loadingIcon").show();
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
            if (typeof updateStoryList == 'function') {
                updateStoryList();
            }
        }
    });

}



/**
 * Updates the left hand side panel with number of stories in the iterations and the stats 
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





$(document).ready(function() {
    $(".showFilter").click(function() {
        $("#filterDialog").toggle();
        return false;
    });


    $(".filterForm").ajaxForm(
    {
        beforeSend: function() {
            if (last_load_iter_req)
            {
                last_load_iter_req.abort();
            }
            $("#loadingIcon").show();
        },
        success: function(html)
        {
            $("#story_list").html(html);
            $(document).trigger('close.facebox');
            $("#loadingIcon").hide();

            $("ul").sortable("disable");
            setUpStoryLinks();

            $("#story_count").text($("#story_list").children().length + " stories");
        }
    });


    if ($.cookie("chart") == "hidden")
    {
        $("#burnup_chart").hide();
        $(".hide_burndown_chart_link").text("Show Chart");
    }

    $(".subIteration").click(function()
    {
        var iteration_id = $(this).attr("iteration_id");
        moveCurrentlyOpenStoryToIteration(iteration_id);
    });

});