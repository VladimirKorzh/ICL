
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
// var db = new sqlite3.Database("../icl/sqlite3.db");
var db = new sqlite3.Database("../../ICL/icl/sqlite3.db");
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

// structure that holds actions that we need to execute.
var actions = [];
var current_task  = '';
var time_lastping = '';

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
  time_lastping = new Date().getTime() / 1000;
  // variable to hold other client info 
  client = otherClient;   
  
  console.log('sessionStart with', otherClient);
  
  msg = 'Hello, I am here to '+current_task.type;
  
  if (current_task.type == 'Award') {
    msg = msg+ ': '+current_task.amount*2+' '+current_task.rarity
  }
  if (current_task.type == 'Collect') {
    msg = msg+ ': '+current_task.amount+' '+current_task.rarity
  }
  
  bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);  
  console.log(msg);
  
  // structure to hold items offered by trade partner
  trade_window_items = []  
  
  steamTrade.open(otherClient, function(){		  
    if (current_task.type == 'Award') {
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
			if ( tag.name == current_task.rarity ) {
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
  if (current_task.type == 'Collect'){
    // if our task is to collect items than we simply wait for the user
    // to place them in the trade window and react accordingly
    console.log('Collecting');
  }
  });
});


steamTrade.on('offerChanged', function(added, item) {
    console.log('offerChanged ' + (added ? 'added ' : 'removed ') + item.name);
    time_lastping = new Date().getTime() / 1000;
    
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
		if ( tag.name == current_task.rarity ){		      
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
    
    if (items_left == 0) {
	msg = 'Press ready.'
	bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);
    }
});


// This function gets called when the user presses the ready button
// here we check that the deal is valid.
steamTrade.on('ready', function() {
      // check if the amount of items does match the bet 
      // in case if we are collecting items
      if (current_task.type =='Collect') {
	  if (current_task.amount == trade_window_items.length) {
	    console.log('Checks passed. Finishing trade.');
	  }
	  else {
	    console.log('Amount of items does not match the collect required amount');
	    return;
	  }
      }

      // if we are awarding a person, than we have already placed the right amount of items
      // in the trade window in the sessionStart callback
      if (current_task.type == 'Award') {
	  console.log('Checks passed. Finishing trade.');
      }
      
      // if we got to here then all the checks are fine
      steamTrade.ready(function() {
	console.log('confirming');
	steamTrade.confirm( function (){
	  console.log("Pressing 'Make Trade' button.");	  
	});
      });            
});

// this function gets called after the trade is finished
// result variable is supposed to hold the string representing
// the status of the trade.
steamTrade.on('end', function(result, items) {
      console.log('End trade event', result);
      if (result === 'complete') {	
	    // marking the transaction in db
	    statement = "UPDATE betting_bidder SET status='OK' WHERE bet_id="+current_task.bet_id+" AND player_id="+current_task.player_id; 
	    
	    db.run(statement, function(err){
		if (err) throw err;
	    });
	    
	    // empty the task
	    current_task = '';  
	    time_lastping = '';
	    keep_or_remove(client);
      }     
});

// DON'T Respond to messages at all. Simply ignore them 
bot.on('message', function(source, message, type, chatter) {
    console.log('We have received a message.');
});

// Add friends automatically.
bot.on('relationship', function(other, type){  
//       console.log('Bot relationship:', other, type);
      if(type == Steam.EFriendRelationship.PendingInvitee) {
	console.log('friend invite received!',other);
	bot.addFriend(other);
	
	check_db(other);
      }
});

// make sure we clean after ourselves
process.on( 'SIGINT', function() {
  console.log( "\nGracefully shutting down from  SIGINT (Crtl-C)" )
  
  // close connection to database
  db.close();
  process.exit( )
});

function check_db(uid) {
  console.log('Checking for tasks related to ', uid);  
  // returns all bidders that are not OK, which means they are waiting
  // either for collection or awarding.
  
  statement = "SELECT player.id as id FROM matchmaking_player as player WHERE player.uid="+uid;
  player_id = 0;
  
  db.each(statement, function(err, row, player_id){
      if (err) throw err;
//       console.log(row.id);      
      player_id = row.id; 

      statement = "SELECT bidder.status, bet.amount, bet.rarity, bet.id as bet_id FROM betting_bidder as bidder, betting_bet as bet WHERE bidder.player_id="+player_id+" AND bet.id = bidder.bet_id AND bidder.status != 'OK'";
      
//       console.log(statement);
      db.all(statement, function (err, rows) {
	  if (err) throw err;
	      
	  if (rows.length == 0) {
	    console.log('nothing has been found');
	    return;
	  }
	  else {
	    rows.forEach( function(row) {
	      console.log('found', row);
	      actions.push({"type":  row.status,
			    "amount": row.amount,
			    "rarity": row.rarity,
			    "uid":    uid,
			    "bet_id": row.bet_id,
			    "player_id": player_id
			  });
	    }); // end for each row that we've found
	  } // end if found rows
      keep_or_remove(uid);	
      }); // end db.all    
  }); // end for each player_id row
} // end check_db

function keep_or_remove(uid) {
  // this function is used to determine if there are any other tasks
  // related to the provided user. In case if there are none, it 
  // removes the user from friend list.
  found_other_tasks = false;
  for (var i=0; i<actions.length; i++) {    
    action = actions[i];
//  console.log('Actionlist',i,action)
    if (action.uid == uid){
      found_other_tasks = true;
    } 
  } // end for 
  
  if (!found_other_tasks) {
    console.log('tasks not found. Removing friend');
    bot.removeFriend(uid);     
    return;
  } 
  console.log('more tasks found. Keeping this friend');
} // end function


function tick(){
  if (time_lastping != '' && current_task != '') {
      time_now = new Date().getTime() / 1000;      
      if ((time_now - time_lastping) > 60) {
	console.log('task takes too much time, cancelling it');
	console.log(current_task);
	bot.removeFriend(current_task.uid);
	current_task = '';
      }
  }
  
  // if we don't have any current tasks
  if (current_task == '') {
      // if there are no other tasks to do
      // just IDLE
      if (actions.length == 0) return;
      
      // if we have some, then take the task
      current_task = actions.pop();
      bot.trade(current_task.uid);
      console.log('Throwing trade request')
      time_lastping = new Date().getTime() / 1000;
  }
}

// Setup speed of tick function.
setInterval(tick, 1000);