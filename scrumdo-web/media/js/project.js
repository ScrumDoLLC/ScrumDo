

$(document).ready(function () {
    
	$(".box a").tipTip({"delay":100, "defaultPosition":"left"});
	$(".box span").tipTip({"delay":100, "defaultPosition":"left"});
	/* get the height of the taller column and set them both to have that height. 
	   Math.max.apply(Math, LIST) is just a way of applying Math.max to a list, 
	   not two numbers */
	$(".story_list").css("min-height", (Math.max.apply(Math, ($.map($(".story_list"),function (e) { return $(e).height() })))));
    });