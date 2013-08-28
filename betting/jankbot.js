
// Import modules that we are using
var fs         = require('fs');
var Steam      = require('steam');
var minimap    = require('minimap');
var SteamTrade = require('steam-trade'); 
var sqlite3    = require("sqlite3").verbose();

// Declare important variables that define the connection
var USERNAME = 'korzhkorzhkorzh'
var PASSWORD = '228121389'
var DISPLAY_NAME = 'ICL.bot'
var DICTIONARY_FILE = 'english.json'

// create instances of bot and trade APIs 
// setup db connection as well
var db = new sqlite3.Database("../icl/sqlite3.db");
var bot = new Steam.SteamClient();
var steamTrade = new SteamTrade();

// Login setup
// load sentry hash file, which confirm that this is a valid
// login to steam. Same is done by real steam client
// in case if there is no sentry file, use the provided email password
var params = {}
require('fs').existsSync('sentry') ? params['shaSentryfile'] = require('fs').readFileSync('sentry') :  params['authCode'] = '5T529';
params['accountName'] = USERNAME
params['password']    = PASSWORD


//////////////////////////////////////////////
var bot_status = 'free'; // busy - when trading
var current_task = '';   // holds current task of the bot
var task_start_time = '';
var actions = [];
var maxnumtries = 3
//////////////////////////////////////////////

bot.on('debug', console.log);

// Log in
bot.logOn(params['accountName'],params['password'], params['shaSentryfile'], params['authCode']);

// Right after we logged on, we setup the bots name
// and Online status
bot.on('loggedOn', function() {
	console.log('loggedOn');
	bot.setPersonaState(Steam.EPersonaState.Online);
	bot.setPersonaName(DISPLAY_NAME);
});


// Perform a web login and save session ID
// which is used in trade APIs
bot.on('webSessionID', function(sessionID) {
	console.log('Got a new session ID:', sessionID);
	steamTrade.sessionID = sessionID;
	bot.webLogOn(function(cookies) {
	  console.log('got a new cookie:', cookies);
	  cookies.split(";").forEach(function(cookie) {
	      steamTrade.setCookie(cookie);
	  });
	});
});

// If the login was performed using an email password
// save the sentry file for next time
bot.on('sentry', function(sentry) {
	console.log('Sentry received!');
	require('fs').writeFileSync('sentry', sentry);
});


// we do not accept trades from people
// we only send trade requests ourselves  
bot.on('tradeProposed', function(tradeID, otherClient) {
	console.log('tradeProposed, but we do not approve it.');
});

// Gets called when trade window appears on the screen
// Here we place items that award to the player
bot.on('sessionStart', function(otherClient) {
  
  msg = 'Hello, I am here to '+current_task.type+ ': '+current_task.amount+' '+current_task.item_rarity
  bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);  
  
  // variable to hold other client info 
  client = otherClient; 
  
  // structure to hold items offered by trade partner
  trade_window_items = []  
  
  console.log('sessionStart with', otherClient);

  steamTrade.open(otherClient, function(){		  
    if (current_task.type == 'award') {
      console.log('Awarding player');
      steamTrade.loadInventory(570, 2, function(inv) {      
	  // find items that match our award
	  itemsmatching = inv.filter(function(item) { 
	      tags=item.tags;
	      
	      correct_item   = false;
	      correct_rariry = false;
	      
	      tags.forEach(function(tag){  
		  if (tag.category_name == 'Type') {
			if (tag.internal_name == 'DOTA_WearableType_Wearable') {
			    correct_item = true;
			}
		  }
		  if (tag.category_name == 'Rarity') {
			if ( tag.name == current_task.item_rarity ) {
			  correct_rariry = true;
			}
		  }
	      });
	      
	      // return true tells filter funciton that this item
	      // matches our needs.
	      if (correct_item == true && correct_rariry == true) {
		      return true;
	      }
	      else {
		      return false;
	      }
	    });      
	    
	    // make sure that we double the bet amout
	    // FIX for the times when bot gave back only your bet
	    steamTrade.addItems(itemsmatching.slice(0, current_task.amount*2));
    });
  }
  if (current_task.type == 'collect'){
    // if our task is to collect items than we simply wait for the user
    // to place them in the trade window and react accordingly
    console.log('Collecting');
  }
  });
});


steamTrade.on('offerChanged', function(added, item) {
    console.log('offerChanged ' + (added ? 'added ' : 'removed ') + item.name);
        
    itemtags = item.tags;
    correct_item = false;
    correct_rariry = false;
    
    // check the item's info to figure out if it is valuable and
    // if it matches our needs
    itemtags.forEach(function(tag){      
	  if (tag.category_name == 'Type') {
		if (tag.internal_name == 'DOTA_WearableType_Wearable') {
		    correct_item = true;
		}
	  }    
	  if (tag.category_name == 'Rarity') {
		if ( tag.name == current_task.item_rarity ){		      
		  correct_rariry = true;
		}
		item_rarity_value = tag.name;
	  }
    });
      
    // prepare the common part of the message
    message = item_rarity_value + ' ' + item.name;
    
    if (!correct_item || !correct_rariry) {	      
      msg = message + ' is not accepted. Wrong Rarity or Item Type.';
      console.log(msg);
      bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);
      return;
    }

    // if the user has added a valid item. 
    if (added) {
      trade_window_items.push(item);    	      
      msg = message + ' is accepted.';
      console.log(msg);
      bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);
    }
    
    // if the user has removed a valid item
    if (!added) {
      // find that item in our structure and remove it
      var index = trade_window_items.indexOf(item);    
      trade_window_items.splice(index, 1);
      
      msg = message + ' was accepted. But you have removed it.';
      console.log(msg);
      bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);
    }
    items_left = current_task.amount - trade_window_items.length
    msg = 'Items left to add: ' + items_left;
    console.log(msg);
    bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);
});


// This function gets called when the user presses the ready button
// here we check that the deal is valid.
steamTrade.on('ready', function() {
      // check if the amount of items does match the bet 
      // in case if we are collecting items
      if (current_task.amount == trade_window_items.length && current_task.type =='collect') {
	  steamTrade.ready(function() {
	    console.log('confirming');
	    steamTrade.confirm();
	  });
      }  

      // if we are awarding a person, than we have already placed the right amount of items
      // in the trade window in the sessionStart callback
      if (current_task.type == 'award') {
	  steamTrade.ready(function() {
	    console.log('confirming');
	    steamTrade.confirm();
	  });
      }
});

// this function gets called after the trade is finished
// result variable is supposed to hold the string representing
// the status of the trade.
steamTrade.on('end', function(result, items) {

      if (result === 'complete') {    // TODO
	    current_task = '';
	    if (current_task.type == 'collect') {
		  statement = "UPDATE betting_bidder SET status='SUBMITTED' WHERE player_id ="+current_task.player_id+" AND bet_id="+current_task.bet_id;
		  
		  db.run(statement, function(err){
		      if (err) throw err;
		  });
		  
		  console.log('marked as SUBMITTED');
	    }
	    if (current_task.type == 'award') {  // TODO
		statement = "UPDATE betting_bidder SET status='AWARDED' WHERE player_id="+current_task.player_id+" AND bet_id="+current_task.bet_id;
		db.run(statement, function(err){
		  if (err) throw err;
		  console.log('FUCKING SHIT IS HERE');
		});			
		console.log('marked as AWARDED');
	    }
	    
      }

      // Since steam has a limitation on the amount of friend one might have
      // we have to remove people from friends list after each transaction
      bot.removeFriend(current_task.uid);     
});

// DON'T Respond to messages at all. Simply ignore them 
bot.on('message', function(source, message, type, chatter) {
    console.log('We have received a message.');
});

// Add friends automatically.
bot.on('relationship', function(other, type){  
      console.log('Bot friends:', bot.friends);
      if(type == Steam.EFriendRelationship.PendingInvitee) {
	console.log('friend invite received!');
	bot.addFriend(other);
      }
});

// make sure we clean after ourselves
process.on( 'SIGINT', function() {
  console.log( "\nGracefully shutting down from  SIGINT (Crtl-C)" )
  
  // close connection to database
  db.close();
  process.exit( )
})



/*


function readdb() {
    var currentdate = new Date();
    console.log('readdb: ' + currentdate.getHours() + ":" + currentdate.getMinutes() + ":" + currentdate.getSeconds());

    statement_collect = "SELECT item_rarity, amount, uid, nickname, bet.id as bet_id, player_id FROM betting_bet AS bet, betting_bidder AS bidder, matchmaking_player AS player WHERE bet.id = bidder.bet_id AND bet.result = 'NOTDECIDED'  AND bet.status = 'CLOSED'  AND bidder.status = 'COLLECTION' AND player.id = player_id"
    
   
    db.all(statement_collect, function(err, rows) {
	  if (err) throw err;
	    
	  if (rows.length == 0) {
	      return;
	  }
	  else {
	      console.log('found new ppl to collect');
	      // read info and append to actions 
	      rows.forEach( function(row) {
		  actions.push({"type": 'collect',
			       "item_rarity":  row.item_rarity,
				"amount":      row.amount,
				"nickname":    row.nickname,
				"uid":         row.uid,
				"bet_id":      row.bet_id,
				"player_id":   row.player_id,
				"tries":       maxnumtries
				});
		  
		  // mark the row as being processed 
		  statement_upd8 = "UPDATE betting_bet SET status='COLLECTING' WHERE id="+row.bet_id 
		  db.run(statement_upd8, function(err) {
			if (err) throw err;
		  });
	      });	      
	  }
    });
    
    statement_award = "SELECT item_rarity, amount, uid, nickname, bet.id as bet_id, player_id FROM betting_bet AS bet, betting_bidder AS bidder, matchmaking_player AS player WHERE bet.id = bidder.bet_id AND bet.result = bidder.side AND bet.status = 'PRIZES' AND bidder.status ='SUBMITTED' AND player.id = player_id"
       
    
    db.all(statement_award, function(err, rows) {
      
	  // throw an error if encountered
	  if (err) throw err;
  
	  if (rows.length == 0) {
	      // bet not found
	      return;
	  }
	  else {		    
	      console.log('found new ppl to award');
	      rows.forEach( function(row) {
		  actions.push({"type": 'award',
			       "item_rarity":  row.item_rarity,
				"amount":      row.amount,
				"nickname":    row.nickname,
				"uid":         row.uid,
				"bet_id":      row.bet_id,
				"player_id":   row.player_id,
				"tries":       maxnumtries
				});
		  
		  // mark the row as being processed 
		  statement_upd8 = "UPDATE betting_bidder SET status='PRIZES' WHERE player_id="+row.player_id	    
		  db.run(statement_upd8, function(err) {
			if (err) throw err;
		  });
	      });
	  }
    });
    console.log('Actions: ', actions);   
    console.log('current_task:', current_task);
} // end refresh function


function work(){
      var current_time = Math.round(+new Date()/1000);
      if (current_task == ''){
	  if (actions.length == 0) return;
	  
	  current_task = actions.pop();
	  if (current_task.tries > 0) {
	    current_task.tries -= 1;
	    console.log('Started task ' + current_task.type + ' ' + current_task.nickname+' '+current_task.tries);
	    bot.trade(current_task.uid);
	    task_start_time = Math.round(+new Date()/1000);
	  }
	  else {
	    current_task = '';
	    work();
	  }
      }
      else if (current_time - task_start_time > 20) {
	  console.log('Task time expired')
	  bot.cancelTrade(current_task.uid);
// 	  SteamTrade.cancel();
	  current_task.tries -= 1;
	  actions.push(current_task);
	  current_task = '';
	  work();
      }
}

update_interval = 10000;
work_interval   = 8000;
setInterval(readdb, update_interval);
setInterval(work, work_interval);*/