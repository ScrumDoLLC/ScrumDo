// this code based on that in:
// http://www.palewire.com/posts/2010/11/07/django-recipe-twitter-style-infinite-scroll/

// Scroll globals
var pageNum = -1;
var hasNextPage = true
var baseUrl = '/activities/user/';


// loadOnScroll handler
var loadOnClick = function() {
    
    $("#moreactivity").unbind('click');
    $("#moreactivity").remove()
    if(pageNum == 1){
        $("#moreactivity").remove()
        var e = $("<div id='moreactivity'><a href='#'>Load More...</a></div>");
        $('#feedContent').append(e);
    }
    loadItems();
    
};

var loadItems = function() {
    // If the next page doesn't exist, just quit now 
    if (hasNextPage === false) {
        return false
    }
    // Update the page number
    pageNum = pageNum + 1;
    // Configure the url we're about to hit
    var url = baseUrl + pageNum;
    $.ajax({
	    url: url, 
		success: function(html) {
		// Update global next page variable
		// Pop all our items out into the page
		$("#loadingIcon").hide();
		$("#feedContent").append(html);
	    },
		error: function () {
		hasNextPage = false;
	    },
		complete: function(html, textStatus){
		// Turn the scroll monitor back on
		$("#moreactivity").bind('click', loadOnClick);
		activateLinks();
	    }
	});
};



function like(activity_id) {
    $.ajax({
	    url: "/activities/like/"+activity_id,
		data:{},
		success: function(html){
		$("#"+activity_id+"like").html(html);  
	    }
	});

}
function loadNewsFeed()
{
    $("#loadingIcon").show();
    $("#feedContent").html("");
    var n;
    for(n = 1; n <= pageNum; n++) {
	$.ajax({
		url: "/activities/user/1",
		    data:{},
		    success: function(html){
		    $("#feedContent").append(html);
		    activateLinks();
		}
	    });
    }
    $("#loadingIcon").hide();

}
    

function activateLinks () {
    /*    $(".commentLink").click( function() 
			     {                    
				 $(this).parent().children(".commentForm").show();
				 $(this).hide();
				 return false;
			     } );

    $(".commentForm form").ajaxForm(function () 
				    { loadNewsFeed(); activateLinks();});

    $(".responses form").ajaxForm(function () {
	    loadNewsFeed(); activateLinks();});

    */}


$(document).ready(function() {
	activateLinks();	
    });



$(document).ready(function () {
	$(".box-heading li a").hover(function() {
		$(this).css("cursor","pointer");
	    });

	$(".buttons a").tipTip({"defaultPosition":"bottom","delay":100});
	$(".box-top .title a").tipTip({"defaultPosition":"bottom","delay":100});
	
	$("#announcements-box .buttons a").click(function () {$("#announcements-box").fadeOut()});
    });
    
loadItems();