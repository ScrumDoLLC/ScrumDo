// this code based on that in:
// http://www.palewire.com/posts/2010/11/07/django-recipe-twitter-style-infinite-scroll/

// Scroll globals
var pageNum = 1;
var hasNextPage = true
var baseUrl = '/activities/user/';


// loadOnScroll handler
var loadOnScroll = function() {
    // If the current scroll position is past out cutoff point...
    if ($(window).scrollTop() > $(document).height() - ($(window).height()*3)) {
        // temporarily unhook the scroll event watcher so we don't call a bunch of times in a row
        $(window).unbind();
        // execute the load function below that will visit the JSON feed and stuff data into the HTML
        loadItems();
    }
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
		$("#feedContent").append(html);
	    },
		error: function () {
		hasNextPage = false;
	    },
		complete: function(html, textStatus){
		// Turn the scroll monitor back on
		$(window).bind('scroll', loadOnScroll);
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
		    $(window).bind('scroll', loadOnScroll);
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
	$(window).bind('scroll', loadOnScroll);
	activateLinks();	
    });



var currentButton = "#your-projects-button";
var currentBox = "#your-projects";

function swap(buttonName, boxName) {
    if (currentButton != buttonName) {
	$(currentButton).removeClass("active");
	$(currentBox).hide();
	$(buttonName).addClass("active");
	$(boxName).show();
	currentButton = buttonName;
	currentBox = boxName;
    }
}

$(document).ready(function () {
	$(".box-heading li a").hover(function() {
		$(this).css("cursor","pointer");
	    });

	$(".buttons a").tipTip({"defaultPosition":"bottom","delay":100});
	$(".box-top .title a").tipTip({"defaultPosition":"bottom","delay":100});
	
	$("#your-projects-button").click(function () { swap("#your-projects-button", "#your-projects");});
	$("#other-projects-button").click(function () { swap("#other-projects-button", "#other-projects");});
	$("#announcements-box .buttons a").click(function () {$("#announcements-box").fadeOut()});
    });