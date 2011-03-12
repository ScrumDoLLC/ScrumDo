var hookbox_connection = null;
var hookbox_subscription = null;
var hookbox_channel_id = null;
var votes_revealed = false;
var current_vote = "";
var current_story_id = "";
var current_story_url = "";
var scrum_master = false;
var my_username = "";
var scrum_master_username = "";
var poker_ajax_url = "";

function poker_connection_error( error )
{    
    retryConnect();
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
    else if( args.payload.message == "save_points" )
    {
        // The scrum master saved the current story.
        poker_handle_save_points();
    }
    else if( args.payload.message == "reset_votes" )
    {
        reset_votes();
    }
    poker_userlist_change(null);
}

function poker_handle_save_points()
{
    $("#current_story_block").html("");
    
    
    $.ajax({
        url: poker_ajax_url,
        data: {action:"single_story", story:current_story_id},
        type: "POST",
        success: function(data) {
            $(".recently_sized_stories").prepend(data);           
        }
    });
        
    reset_votes();
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
    $("#mainPokerArea").show();
    if( my_username == username )
    {
        scrum_master = true;
        message = "<h1>Please pick a story.</h1>";
        $("#scrum_master_block").show();
        $("#normal_user_block").hide();    
        load_stories_to_size();    
        
        $(".reset_button").show();
        $(".save_button").show();
    }
    else
    {
        message = "Please wait while the Scrum Master picks a story";
        scrum_master = false;
        $("#scrum_master_block").hide();
        $("#normal_user_block").show();        
        $(".reset_button").hide();
        $(".save_button").hide();
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
    
    $("#scrum_master_title").text( username );
}

function reset_votes()
{
    current_vote = "";
    votes_revealed = false;
    $("#votelist").html("");
    $(".point_button").removeClass("blue");
}

function poker_show_all_incomplete_stories()
{
    $.ajax({
        url: poker_ajax_url,
        data: {action:"all_incomplete_stories_to_size"},
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
    return false;
}
function poker_show_all_stories()
{
    $.ajax({
        url: poker_ajax_url,
        data: {action:"all_stories_to_size"},
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
    return false;
}

function poker_load_story( args )
{
    $("#buttonArea").show();
    
    if( current_story_url != args.payload.story_url)
    {
        reset_votes();
    }
    current_story_url = args.payload.story_url;
    
    //http://localhost:8000/projects/story/542
    var re = new RegExp("projects/story/([0-9]+)");
    var m = re.exec(current_story_url);
    if( m != null)
    {
        current_story_id = m[1];
    }
    
    update_current_story();
}

function update_current_story()
{
    $.ajax({
        url: current_story_url,
        success: function(data) {
            $("#current_story_block").html(data);
            $(".moveIterationIcon").hide();
            setUpStoryLinks();            
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
    $("#userlist").html( hookbox_subscription.presence.join("<br/> ") );
}

function poker_subscribed(channelName, _subscription) 
{
    $("#current_story_block").show();
    
   hookbox_subscription = _subscription;
   hookbox_subscription.onSubscribed = poker_userlist_change;
   hookbox_subscription.onUnsubscribe = poker_userlist_change;
   hookbox_subscription.onPublish = poker_on_publish;
   
   hookbox_connection.publish(hookbox_channel_id, { message:"who_is_scrum_master" } );
   
   poker_userlist_change(null);
}

function poker_save_estimate()
{
    
    if( current_vote == "" || current_story_id == "")
    {
        alert("You must have a story and a point value selected before saving.");
        return;
    }
    hookbox_connection.publish(hookbox_channel_id, { message:"save_points", story:current_story_id, points:current_vote } );
    
    $.ajax({
        url: poker_ajax_url,
        data: {action:"set_size", story:current_story_id, points:current_vote },
        type: "POST",
        success: function() {
                load_stories_to_size();                        
        }
    });
}

function force_revote()
{
    hookbox_connection.publish(hookbox_channel_id, { message:"reset_votes" } );
}

function retryConnect()
{
    $("#connection_error").show();
    setTimeout("window.location.reload()",3000)
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
    hookbox_connection.onClose = function() { retryConnect(); };
    
    
    $(".save_button").click(function(){
        poker_save_estimate();
    });
    
    $(".reset_button").click(function(){
        force_revote();
    });
    
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
    
   window.onbeforeunload = function() {
      hookbox_connection.disconnect();        
   };

}

function poker_handle_who_scrum_master( args )
{
    if( scrum_master )
    {
        poker_become_scrum_master();
        if( current_story_url != "" )
        {
            hookbox_connection.publish(hookbox_channel_id, {message:"story", story_url:current_story_url} );
        }
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
    current_vote = value;
    hookbox_connection.publish(hookbox_channel_id, {message:"vote", estimate:value} );
    
    $.ajax({
        url: poker_ajax_url,
        data: {action:"stories_with_size", size:value},
        type: "POST",
        success: function(data) {                
            $(".stories_with_size").html(data);           
            $(".size_title").html("Other " + value + " point stories.");
        }
    });
    
}

function calculateBothPoints() { }