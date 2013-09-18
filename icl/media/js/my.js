$('.typeahead').typeahead({
    source: function (query, process) {
        return $.get('/profile/search/'+query, function (data) {
            return process(data.userlist);
        });
    }
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
