function scrollTo(item) {
    $("html,body").animate({scrollTop: $(item).offset().top});
}

function generateMenu() {
    $("h2").each(function (i, e) {
	    var shortname = $(e).attr("alt");
	    var menuitem = $("<span><a href='#'>" + shortname + "</a> | </span>");
	    $(e).attr("id", "h2_" + i);
	    menuitem.click(function () { scrollTo("#h2_"+i); });
	    $("#menu").append(menuitem);
	    var top = $("<span><a href='#'>" + arrow_up + "</a> </span>");
	    top.click(function () { scrollTo("body"); });
	    $(e).prepend(top);
	});
}

$(document).ready(function () {
	generateMenu();
    });