$('.typeahead').typeahead({
    source: function (query, process) {
        return $.get('/profile/search/'+query, function (data) {
            return process(data.userlist);
        });
    }
});

$(function() {

  $.extend($.tablesorter.themes.bootstrap, {
    // these classes are added to the table. To see other table classes available,
    // look here: http://twitter.github.com/bootstrap/base-css.html#tables
    table      : 'table table-bordered table-condensed',
    header     : 'bootstrap-header', // give the header a gradient background
    footerRow  : '',
    footerCells: '',
    icons      : '', // add "icon-white" to make them white; this icon class is added to the <i> in the header
    sortNone   : 'bootstrap-icon-unsorted',
    sortAsc    : 'icon-chevron-up',
    sortDesc   : 'icon-chevron-down',
    active     : '', // applied when column is sorted
    hover      : '', // use custom css here - bootstrap class may not override it
    filterRow  : '', // filter row class
    even       : '', // odd row zebra striping
    odd        : ''  // even row zebra striping
  });

  // call the tablesorter plugin and apply the uitheme widget
  $("#myTable").tablesorter({
    // this will apply the bootstrap theme if "uitheme" widget is included
    // the widgetOptions.uitheme is no longer required to be set
    theme : "bootstrap",

    widthFixed: true,

    headerTemplate : '{content} {icon}', // new in v2.7. Needed to add the bootstrap icon!

    // widget code contained in the jquery.tablesorter.widgets.js file
    // use the zebra stripe widget if you plan on hiding any rows (filter widget)
    widgets : [ "uitheme", "filter", "zebra" ],

    widgetOptions : {
      // using the default zebra striping class name, so it actually isn't included in the theme variable above
      // this is ONLY needed for bootstrap theming if you are using the filter widget, because rows are hidden
      zebra : ["even", "odd"],

      // reset filters button
      filter_reset : ".reset"

      // set the uitheme widget to use the bootstrap theme class names
      // this is no longer required, if theme is set
      // ,uitheme : "bootstrap"

    }
  })
  .tablesorterPager({

    // target the pager markup - see the HTML block below
    container: $(".pager"),

    // target the pager page select dropdown - choose a page
    cssGoto  : ".pagenum",

    // remove rows from the table to speed up the sort of large tables.
    // setting this to false, only hides the non-visible rows; needed if you plan to add/remove rows with the pager enabled.
    removeRows: false,

    // output string - default is '{page}/{totalPages}';
    // possible variables: {page}, {totalPages}, {filteredPages}, {startRow}, {endRow}, {filteredRows} and {totalRows}
    output: '{startRow} - {endRow} / {filteredRows} ({totalRows})'

  });

});


// Allow tooltips on span classes
jQuery(function ($) {
    $("span").tooltip();
});

// Destroys modals as soon as they are hidden
 $("[data-toggle=modal]").click(function(ev) {
    ev.preventDefault();
    // load the url and show modal on success
    $( $(this).attr('data-target') + " .modal-body").load($(this).attr("href"), function() { 
         $($(this).attr('data-target')).modal("show"); 
    });
});
 
window.setTimeout(function() {
    $(".alert-message").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove(); 
    });
}, 5000); 

/*



$( document ).ajaxStart(function() {
    $( "#loading" ).show(500);
    $( "#placeholder" ).hide(500);
    
});

$( document ).ajaxStop(function() {
    $( "#loading" ).hide(500);
    $( "#placeholder" ).show(500);
});
*/







/*

function winnerside(side, bet_id) {
  var pass=prompt("Enter password: ", "????"); 
  if (pass!=null && pass!="") {
//     alert(pass);
    window.location = "/bets/decide_bet/"+bet_id+"/"+side+"/"+pass;  
  }
}

function overlay() {
	el = document.getElementById("overlay");
	el.style.visibility = (el.style.visibility == "visible") ? "hidden" : "visible";
}*/

// function recalculateexp(){
// 	document.getElementById("exp").innerHTML = '?';
// 	$.ajax({
// 	    type: "GET",
// 	    url: "/ajax/recalculateexp",
// 
// 	    async: true,    /* If set to non-async, browser shows page as "Loading.." */
// 	    cache: false,
// 	    timeout: 90000, /* Timeout in ms */
// 	    dataType: 'json',
// 	    
// 	    success: function(data)
// 	    {   
// 		document.getElementById("exp").innerHTML = data.exp;
// 	    }    
// 	}); 
// }

// function timedRefresh(timeoutPeriod){
//       setTimeout("location.reload(true);", timeoutPeriod);
// }











/*
<!--<script type="text/javascript">
   function getmatch(){
        $.ajax({
            type: "GET",
            url: "/matchmaking/getmatch",

            async: true,  /* If set to non-async, browser shows page as "Loading.." */
//             cache: false,
//             timeout:5000, /* Timeout in ms */
// 
//             success: function(data)
//             {
// 		if (data["HTTPRESPONSE"] != 1)
// 		{
// 		    alert("your lobby"+data["lobby"]); 
// 		}
// 		else
// 		{
// 		    alert("no ready yes, polling again");            
// 		    setTimeout(waitForMsg, 5000);
// 		}
//             }
//         });
//     };
// 
//    function startsearch(){
// 
//         setTimeout(getmatch, 5000)        
//     };*/

    
// $.ajax({
//     type: "GET",
//     url: "/matchmaking/getchannelsinfo",
// 
//     async: true,  /* If set to non-async, browser shows page as "Loading.." */
//     cache: false,
//     timeout: 30000, /* Timeout in ms */
//     dataType: 'json',
//     
//     success: function(data)
//     {	   
// 	  for (var i=0;i<data.length;i++)
// 	  { 
// 		var div = document.createElement('div');
// 		document.getElementById("channelsinfo").innerHTML = "";
// 	  }
//     }    
// });    
    
// </script>  
