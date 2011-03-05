/**
 * jQuery confirmation box plugin
 * @author Michał Bielawski <d3x@burek.it>
 * @name jQuery confirm()
 * @license WTFPL (http://sam.zoy.org/wtfpl/)
 * @modified Daniel Patterson <dbp@riseup.net>
 */
(function($) {
    var defaults = {
	question: "Are you sure?",
	yes: "Yes",
	no: "No"
    };
    $.fn.extend({
    confirm: function(question, yes, no) {
      if(typeof(question) == "undefined")
	  question = defaults.question;
      if(typeof(yes) == "undefined")
	  yes = defaults.yes;
      if(typeof(no) == "undefined")
	  no = defaults.no;
      return this.each(function() {
	      $(this).click(function(e) {
      e.preventDefault();
      jQuery.facebox('<div id="jquery-confirm"></div>');
      $("#jquery-confirm").append($('<h1>', {text: question}).
			   after($('<button>').append(
                           $(this).clone(true).removeAttr("class").text(yes).unbind('click')))
                           .after($('<button>').click(function() {
				       $(document).trigger('close.facebox');}).text(no)))})})}})})(jQuery);
