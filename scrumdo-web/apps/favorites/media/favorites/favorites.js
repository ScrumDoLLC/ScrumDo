function hook_up_favorites() {
    $(".favorite_link").click( function(){
        var url;
        var img = $(this).find("img");
        var img_src = img.attr("src");
        if( $(this).attr("favorite") == "true" )
        {
            // Turning off the favorite
            url = $(this).attr("remove_url");  
            $(this).attr("favorite","false");
            img.attr("src", img_src.replace("favorite_on","favorite_off") );
        }
        else
        {
            url = $(this).attr("add_url");
            $(this).attr("favorite","true");
            img.attr("src", img_src.replace("favorite_off","favorite_on") );
        }
        $.ajax({
            url: url,
            method: "POST"            
        });
        return false;
    });
}

$(document).ready( hook_up_favorites );