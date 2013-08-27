

$( document ).ajaxStart(function() {
    $( "#loading" ).show(500);
    $( "#placeholder" ).hide(500);
    
});

$( document ).ajaxStop(function() {
    $( "#loading" ).hide(500);
    $( "#placeholder" ).show(500);
});


function searchbet() {
  window.location = "/bets/show/"+document.getElementById("bet_id").value;
}

function cancelbet(bet_id) {
  window.location = "/bets/cancelbet/"+bet_id;
}

function deletebet(bet_id) {
  window.location = "/bets/deletebet/"+bet_id;
}

function takeside(side, bet_id) {
  if (side == 'a') window.location = "/bets/takesidea/"+bet_id;
  if (side == 'b') window.location = "/bets/takesideb/"+bet_id;
}

function closebetting(bet_id) {
  window.location = "/bets/closebetting/"+bet_id;  
}

function winnerside(side, bet_id) {
var retVal = prompt("Enter passwd: ", "0000");  
  if (side == 'a') window.location = "/bets/winnersidea/"+bet_id+"/"+retVal;  
  if (side == 'b') window.location = "/bets/winnersideb/"+bet_id+"/"+retVal;  
}

function recalculateexp(){
	document.getElementById("exp").innerHTML = '?';
	$.ajax({
	    type: "GET",
	    url: "/ajax/recalculateexp",

	    async: true,    /* If set to non-async, browser shows page as "Loading.." */
	    cache: false,
	    timeout: 90000, /* Timeout in ms */
	    dataType: 'json',
	    
	    success: function(data)
	    {   
		document.getElementById("exp").innerHTML = data.exp;
	    }    
	}); 
}

function timedRefresh(timeoutPeriod){
      setTimeout("location.reload(true);", timeoutPeriod);
}

  
$(function() {
      /* For zebra striping */
      $("table tr:nth-child(odd)").addClass("odd-row");
      /* For cell text alignment */
      $("table td:first-child, table th:first-child").addClass("first");
      /* For removing the last border */
      $("table td:last-child, table th:last-child").addClass("last");
});











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
