(function($) {

	$.fn.tagit = function(options) {

		var el = this;

		const BACKSPACE		= 8;
		const ENTER			= 13;
		const SPACE			= 32;
		const COMMA			= 44;

        var input_field = $(options.input_field);

        
		// add the tagit CSS class.
		el.addClass("tagit");

		// create the input field.
		var html_input_field = "<li class=\"tagit-new\"><input class=\"tagit-input\" type=\"text\" /></li>\n";
		el.html (html_input_field);

		tag_input		= el.children(".tagit-new").children(".tagit-input");

		$(this).click(function(e){
			if (e.target.tagName == 'A') {
				// Removes a tag when the little 'x' is clicked.
				// Event is binded to the UL, otherwise a new tag (LI > A) wouldn't have this event attached to it.
				$(e.target).parent().remove();
			}
			else {
				// Sets the focus() to the input field, if the user clicks anywhere inside the UL.
				// This is needed because the input field needs to be of a small size.
				tag_input.focus();
			}
			serializeTags();
		});

		tag_input.keypress(function(event){
			if (event.which == BACKSPACE) {
				if (tag_input.val() == "") {
					// When backspace is pressed, the last tag is deleted.
					$(el).children(".tagit-choice:last").remove();
				}
			}
			// Comma/Space/Enter are all valid delimiters for new tags.
			else if (event.which == COMMA || event.which == SPACE || event.which == ENTER) {
				event.preventDefault();

				var typed = tag_input.val();
				typed = typed.replace(/,+$/,"");
				typed = typed.trim();

				if (typed != "") {
					if (is_new (typed)) {
						create_choice (typed);
					}
					// Cleaning the input.
					tag_input.val("");
				}
			}
			serializeTags();
		});

         tag_input.autocomplete({
         minLength: 0,
         source: options.availableTags, 
         select: function(event,ui){
             if (is_new (ui.item.value)) {
                 create_choice (ui.item.value);
             }
             // Cleaning the input.
             tag_input.val("");        
             // Preventing the tag input to be update with the chosen value.
             return false;
         }
        }).data( "autocomplete" )._renderItem = function( ul, item ) {
            if( item.desc )
            {
         			return $( "<li></li>" )
         				.data( "item.autocomplete", item )
         				.append( "<a><b>" + item.label + "</b><br><i>" + item.desc + "</i></a>" )
         				.appendTo( ul );
         	}
         	else
         	{
     			return $( "<li></li>" )
     				.data( "item.autocomplete", item )
     				.append( "<a><b>" + item.label + "</b></a>" )
     				.appendTo( ul );         	    
         	}
        };

        $(tag_input).focus( function() { tag_input.autocomplete( "search", "" ); });
        
        
        function serializeTags()
        {
            var new_value = "";
            this.tag_input.parents("ul").children(".tagit-choice").each(function(i){
				n = $(this).children("input").val();
				if( new_value.trim().length > 0)
				{
				    new_value = new_value + ","
				}
				if( n.trim().length > 0)
				{
				    new_value = new_value + n
			    }
			})
            input_field.val(new_value);
        }

		function is_new (value){
			var is_new = true;
			this.tag_input.parents("ul").children(".tagit-choice").each(function(i){
				n = $(this).children("input").val();
				if (value == n) {
					is_new = false;
				}
			})
			return is_new;
		}
		function create_choice (value){
		    if( value.trim() == "")
		    {
		        return;
		    }
			var el = "";
			el  = "<li class=\"tagit-choice\">\n";
			el += value + "\n";
			el += "<a class=\"tagit-close\">x</a>\n";
			el += "<input type=\"hidden\" style=\"display:none;\" value=\""+value+"\" name=\"item[tags][]\">\n";
			el += "</li>\n";
			var li_search_tags = this.tag_input.parent();
			$(el).insertBefore (li_search_tags);
			this.tag_input.val("");
			serializeTags();
		}
		
		var current_vals = input_field.val().split(',');		
		var current_val;
		for( current_val=0 ; current_val< current_vals.length ; current_val++ )
		{		    
		    create_choice(current_vals[current_val]);
		}
		input_field.hide();
        
	};

	String.prototype.trim = function() {
		return this.replace(/^\s+|\s+$/g,"");
	};

})(jQuery);
