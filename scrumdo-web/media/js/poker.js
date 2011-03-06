
var hookbox_connection = null;
var hookbox_subscription = null;
var hookbox_channel_id = null;
var votes_revealed = false;
var current_story_url = "";
var scrum_master = false;
var my_username = "";
var scrum_master_username = "";
var poker_ajax_url = "";

function poker_connection_error( error )
{
    
}

function poker_on_publish(args) 
{
    if( args.payload.message == "vote" )
    {
        // Somebody has submitted a vote.
        poker_process_vote(args);
    }
    else if( args.payload.message=="story" )
    {
        // The scrum master selected a story to vote on.
        poker_load_story( args );
    }
    else if( args.payload.message=="refresh")
    {
        // Somebody changed the story, we should reload it.
        update_current_story();
    }
    else if( args.payload.message == "scrum_master")
    {
        // Somebody has become the scrum master.
        poker_handle_scrum_master( args.user );
    }
    else if( args.payload.message == "who_is_scrum_master")
    {
        // A new user logged on and asked who the scrum master is.
        poker_handle_who_scrum_master( args );
    }
}

function load_stories_to_size()
{
    $.ajax({
        url: poker_ajax_url,
        data: {action:"stories_to_size"},
        type: "POST",
        success: function(data) {
            $("#stories_to_size_list").html(data);
            $(".load_story_link").click( function() { 
                story_url = $(this).attr("href");
                hookbox_connection.publish(hookbox_channel_id, {message:"story", story_url:story_url} );
                return false;
            });
        }
    });        
}

function poker_handle_scrum_master( username )
{
    if( my_username == username )
    {
        scrum_master = true;
        message = "Please pick a story.";
        $("#scrum_master_block").show();
        $("#normal_user_block").hide();    
        load_stories_to_size();    
    }
    else
    {
        message = "Please wait while the Scrum Master picks a story";
        scrum_master = false;
        $("#scrum_master_block").hide();
        $("#normal_user_block").show();        
        
        if( username != scrum_master_username)
        {
            scrum_master_username = username;
            //alert(scrum_master_username + " is now the Scrum Master");
        }
    }
    
    if( current_story_url == "" )
    {
        $("#current_story_block").html(message);
    }
    
    $("#scrum_master_title").text("Scrum Master: " + username );
}

function reset_votes()
{
    votes_revealed = false;
    $("#votelist").html("");
    $(".point_button").removeClass("blue");
}

function poker_load_story( args )
{
    if( current_story_url != args.payload.story_url)
    {
        reset_votes();
    }
    current_story_url = args.payload.story_url;
    update_current_story();
}

function update_current_story()
{
    $.ajax({
        url: current_story_url,
        success: function(data) {
            $("#current_story_block").html(data);
        }
    });
}

function poker_process_vote(args)
{
    content = "<div id='vote_" + args.user + "' class='vote_card'><div class='vote_val hidden'>" + args.payload.estimate + "</div><br/>" + args.user + "</div>";
    oldnode = $("#vote_" + args.user );
    if( oldnode.length > 0 )
    {
        newnode = $(oldnode).replaceWith(content);
        $("#vote_" + args.user ).effect("highlight", {}, 2000);        
    }
    else
    {
        $("#votelist").append( content );
        $("#vote_" + args.user ).hide();
        
        $("#vote_" + args.user ).slideDown();
    }
    
    if( votes_revealed )
    {
        $(".vote_val").removeClass("hidden");
    }
    
}

function poker_userlist_change(frame) 
{
    $("#userlist").html( hookbox_subscription.presence );

}

function poker_subscribed(channelName, _subscription) 
{
   hookbox_subscription = _subscription;
   hookbox_subscription.onSubscribed = poker_userlist_change;
   hookbox_subscription.onUnsubscribe = poker_userlist_change;
   hookbox_subscription.onPublish = poker_on_publish;
   
   hookbox_connection.publish(hookbox_channel_id, { message:"who_is_scrum_master" } );
}

function poker_startup(hookbox, hookbox_server, channel_id, username, ajax_url)
{
    my_username = username;

    poker_ajax_url = ajax_url;

    hookbox_channel_id = channel_id;
    hookbox_connection = hookbox.connect( hookbox_server );
    hookbox_connection.onOpen = function() { hookbox_connection.subscribe( channel_id ); } ;
    hookbox_connection.onError = poker_connection_error;    
    hookbox_connection.onSubscribed = poker_subscribed;    
    
    $(".point_button").click(function(){
       poker_make_estimate( $(this).attr("value") ) ;
       $(".point_button").removeClass("blue");
       $(this).addClass("blue");
    });
        
    $(".scrum_master_button").click(function(){
        var answer = confirm("Are you sure you want to take over as Scrum Master?  Only one person can be the Scrum Master in a planning poker session at a time.")
        if( answer )
        {
            poker_become_scrum_master();
        }
    });

}

function poker_handle_who_scrum_master( args )
{
    if( scrum_master )
    {
        poker_become_scrum_master();
    }
}

function poker_become_scrum_master()
{
    hookbox_connection.publish(hookbox_channel_id, { message:"scrum_master" } );
}

function reloadStoryCallback() 
{
    refresh_story();
}

function refresh_story( )
{
    hookbox_connection.publish(hookbox_channel_id, { message:"refresh" } );
}

function poker_make_estimate( value )
{    
    votes_revealed = true;
    hookbox_connection.publish(hookbox_channel_id, {message:"vote", story_id: "blah", estimate:value} );
}

function calculateBothPoints()
{
    
}