
//Imports.
var fs         = require('fs');
var Steam      = require('steam');
var friends    = require('./bot_modules/friends.js');
var logger     = require('./bot_modules/logger.js');
var minimap    = require('minimap');
var SteamTrade = require('steam-trade'); 
var sqlite3    = require("sqlite3").verbose();

// Define command line arguments.
var argv = require('optimist');

// Load config file.
var CONFIG = JSON.parse(fs.readFileSync("config.json"));

// Load dictionary.
var DICT = JSON.parse(fs.readFileSync(CONFIG.dictionary));

// Set admins.
var ADMINS = CONFIG.admins;

if (ADMINS == null) {
  ADMINS = [];
}

// Load modules.
var modules = [];
for (var i = 0; i < CONFIG.modules.length; i++) {
    modules.push(require("./bot_modules/" + CONFIG.modules[i] + ".js"));
}

// Global variables.
var myName = CONFIG.displayName;

var params = {}
params['accountName'] = CONFIG.username
params['password']    = CONFIG.password

// load sentry hash file 
require('fs').existsSync('sentry') ? params['shaSentryfile'] = require('fs').readFileSync('sentry') :  params['authCode'] = '5T529';

// create instances of bot and trade apis and db connection
var bot = new Steam.SteamClient();
var steamTrade = new SteamTrade();
var db = new sqlite3.Database("../icl/sqlite3.db");


var bot_status = 'free'; // busy - when trading
var current_task = '';   // holds current task of the bot
var task_start_time = '';
var actions = [];
var maxnumtries = 3

bot.on('debug', console.log);

// Log in and set name
bot.logOn(params['accountName'],params['password'], params['shaSentryfile'], params['authCode']);

// happens after you log in.
bot.on('webSessionID', function(sessionID) {
	console.log('got a new session ID:', sessionID);
	steamTrade.sessionID = sessionID;
	bot.webLogOn(function(cookies) {
	  console.log('got a new cookie:', cookies);
	  cookies.split(";").forEach(function(cookie) {
	      steamTrade.setCookie(cookie);
	  });
	});
});

bot.on('loggedOn', function() {
	logger.log(DICT.SYSTEM.system_loggedin);
	bot.setPersonaState(Steam.EPersonaState.Online);
	bot.setPersonaName(myName);
});

bot.on('sentry', function(sentry) {
	console.log('Sentry received!');
	require('fs').writeFileSync('sentry', sentry);
});

bot.on('tradeProposed', function(tradeID, otherClient) {
	// we are no longer accepting trades from people
	// we only send trade requests ourselves  
	console.log('tradeProposed, but we do not approve it.');
});

bot.on('sessionStart', function(otherClient) {
	client = otherClient;
	trade_window_items = []
	
	console.log('trading with ' + bot.users[client].playerName);
	steamTrade.open(otherClient, function(){		  
		  if (current_task.type == 'award') {
			  steamTrade.loadInventory(570, 2, function(inv) {
			      inventory = inv;
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
				      
				      if (correct_item == true && correct_rariry == true) {
					      return true;
				      }
				      else {
					      return false;
				      }
			      });      
			      steamTrade.addItems(itemsmatching.slice(0, current_task.amount*2));
			});
		}
		if (current_task.type == 'collect'){
		      console.log('collecting')
		}
	});
});

steamTrade.on('offerChanged', function(added, item) {
	task_start_time = Math.round(+new Date()/1000);
	console.log('===> they ' + (added ? 'added ' : 'removed ') + item.name);
	itemtags = item.tags;
	
	correct_item = false;
	correct_rariry = false;
	
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
	  
	if (!correct_item || !correct_rariry) {
	      message = minimap.map({"itemrarity": item_rarity_value, "itemname": item.name},DICT.BET_RESPONSES.bet_incorrect_item_added);
	      
	      console.log(message);
	      friends.messageUser(client, message, bot);	  
	      return;
	}

	if (added) {
	      trade_window_items.push(item);    
	      message = minimap.map({"itemrarity": item_rarity_value, "itemname": item.name},DICT.BET_RESPONSES.bet_correct_item_added);
	      
	      console.log(message);
	      friends.messageUser(client, message, bot);	  
	}
	if (!added) {
	      var index = trade_window_items.indexOf(item);    
	      trade_window_items.splice(index, 1);
	      
	      message = minimap.map({"itemrarity": item_rarity_value, "itemname": item.name},DICT.BET_RESPONSES.bet_correct_item_removed);	
	      
	      console.log(message);
	      friends.messageUser(client, message, bot);
	      
	}
	
	message = minimap.map({"itemsleft": current_task.amount - trade_window_items.length, "itemrarity": current_task.item_rarity},DICT.BET_RESPONSES.bet_items_left);	
	console.log(message);
	friends.messageUser(client, message, bot);	
});



steamTrade.on('ready', function() {
      // amount of items doesn't match the bet 
      if (current_task.amount == trade_window_items.length && current_task.type =='collect') {
	    steamTrade.ready(function() {
	      console.log('confirming');
	      steamTrade.confirm();
	    });
      }  
      // if all goes through then we are good to go
      if (current_task.type == 'award') {
	      steamTrade.ready(function() {
		      message = minimap.map({"betid": current_task.bet_id}, DICT.BET_RESPONSES.bet_status_valid);
		      console.log(message);
		      friends.messageUser(client, message, bot);
		      
		      steamTrade.confirm();    
	      });
      }
});

steamTrade.on('end', function(result, items) {
      console.log('trade', result.toString());
      bot.removeFriend(current_task.uid);
      if (result.toString() == 'complete') {
	    current_task = '';
	    if (current_task.type == 'collect'){
		  statement = "UPDATE matchmaking_bidder SET status='SUBMITTED' WHERE player_id ="+current_task.player_id+" AND bet_id="+current_task.bet_id;
		  
		  db.run(statement, function(err){
		      if (err) throw err;
		  });
		  
		  console.log('marked as SUBMITTED');
	    }
      }
      if (result == 'failed'){
	console.log('failed');
      }
});

// Respond to messages.
bot.on('message', function(source, message, type, chatter) {

      // Be sure this person is remembered and run friends list name update.
      friends.addFriend(source);
      friends.updateFriendsNames(bot);

      // If the message is blank (blank messages are received from 'is typing').
      if (message == '') return;

      // Save the original full message for later use.
      var original = message;
      message = message.toLowerCase();
      var fromUser = friends.nameOf(source);

      // Log the received message.
      logger.log(minimap.map({"user" : fromUser, "message" : original},DICT.SYSTEM.system_msg_received));

      var input = message.split(" ");
      
      // check if this is an admin function request.
      if (input[0] == "admin") {

	// Authenticate as admin.
	if (isAdmin(source)) {
	      admin(input, source, original, function(resp) {
		  friends.messageUser(source, resp, bot);
	      });
	      return;
	}
	else {
	      friends.messageUser(source, DICT.ERRORS.err_not_admin, bot);
	      return;
	}
      }
      
      // Placing a bet. 
//       if (input[0] == DICT.CMDS.bet) {
// 	    provided_betid = escape(input[1]);
// 	    console.log('User asked to place a bet on: '+provided_betid);
// 	    
// 	    // check if there is a record about this bet in database
// 	    statement = "SELECT id, item_rarity, amount, status FROM matchmaking_bet WHERE id="+provided_betid
// 	    db.all(statement, function(err, rows) {
// 	      
// 		  // throw an error if encountered
// 		  if (err) throw err;
// 		      
// 		  if (rows.length == 0) {
// 		      // bet not found
// 		      console.log(DICT.BET_RESPONSES.bet_not_found);
// 		      friends.messageUser(source, DICT.BET_RESPONSES.bet_not_found, bot);
// 		      return;
// 		  }
// 		  else if (rows.length == 1) {
// 		      // bet is found
// 		      console.log(DICT.BET_RESPONSES.bet_found);
// 		      friends.messageUser(source, DICT.BET_RESPONSES.bet_found, bot);		  
// 		      rows.forEach( function(row) {
// 			  //check the status of this bet
// 			  if (row.status != 'C') {
// 				// if its still open or has other invalid status
// 			      console.log(DICT.BET_RESPONSES.bet_not_closed); 
// 			      friends.messageUser(source, DICT.BET_RESPONSES.bet_not_closed, bot);		  
// 			      return;
// 			  }
// 			  else {
// 			      // bet is found and has a closed status
// 			      console.log(DICT.BET_RESPONSES.bet_status_valid); 
// 			      friends.messageUser(source, DICT.BET_RESPONSES.bet_status_valid, bot);
// 			      message = "Bet is " + row.amount + " " + row.item_rarity;
// 			      friends.messageUser(source, message, bot);
// 			      bet_id = provided_betid;   			   
// 			      bet_itemrarity = row.item_rarity;
// 			      bet_itemcount  = row.amount;
// 			      return;
// 			  }
// 		      });
// 		  }
// 	    });
// 	    return;
// 	}  

//   // Loop through other modules.
//   for (var i = 0; i < modules.length; i++) {
//     if (typeof modules[i].canHandle === 'function') {
//       if (modules[i].canHandle(original)) {
//         modules[i].handle(original, source, bot);
//         return;
//       }
//     }
//   }

      // Default
      friends.messageUser(source, randomResponse(), bot);

});


// Add friends automatically.
bot.on('relationship', function(other, type){
      console.log('friend invite received!');
      if(type == Steam.EFriendRelationship.PendingInvitee) {
	bot.addFriend(other);
	logger.log(minimap.map({"userid" : other}, DICT.SYSTEM.system_added_friend));
	friends.addFriend(other);
	friends.updateFriendsNames(bot);
      }
});


// Responses for unknown commands.
function randomResponse() {
      var responses = DICT.random_responses;
      return responses[Math.floor(Math.random() * responses.length)];
}


// Saves data and exits gracefully.
function shutdown() {
      // close connection to database
      db.close();
      friends.save();
      
      // exit from modules too
      for (var i = 0; i < modules.length; i++) {
	if (typeof modules[i].onExit === 'function') {
	  modules[i].onExit();
	}
      }
      // close process
      process.exit();
}


// Handler for admin functionality.
function admin(input, source, original, callback) {
    //   Quit function
      if (input[1] == "quit") {
	console.log(DICT.ADMIN.quit);
	shutdown();
      }
}

// Returns true if the given ID is an admin.
function isAdmin(source) {
      return ADMINS.indexOf(source) != -1;
}


function readdb() {
    var currentdate = new Date();
    console.log('readdb: ' + currentdate.getHours() + ":" + currentdate.getMinutes() + ":" + currentdate.getSeconds());

    statement_collect = "SELECT item_rarity, amount, uid, nickname, bet.id as bet_id, player_id FROM matchmaking_bet AS bet, matchmaking_bidder AS bidder, matchmaking_player AS player WHERE bet.id = bidder.bet_id AND bet.result = 'NOTDECIDED'  AND bet.status = 'CLOSED'  AND bidder.status = 'COLLECTION' AND player.id = player_id"
    
   
    db.all(statement_collect, function(err, rows) {
	  if (err) throw err;
	    
	  if (rows.length == 0) {
	      console.log(DICT.BET_RESPONSES.no_players_waiting_to_bet);	      
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
		  statement_upd8 = "UPDATE matchmaking_bet SET status='COLLECTING' WHERE id="+row.bet_id 
		  db.run(statement_upd8, function(err) {
			if (err) throw err;
		  });
	      });	      
	  }
    });
    
    statement_award = "SELECT item_rarity, amount, uid, nickname, bet.id as bet_id, player_id FROM matchmaking_bet AS bet, matchmaking_bidder AS bidder, matchmaking_player AS player WHERE bet.id = bidder.bet_id AND bet.result = bidder.side AND bet.status = 'PRIZES' AND bidder.status ='SUBMITTED' AND player.id = player_id"
       
    
    db.all(statement_award, function(err, rows) {
      
	  // throw an error if encountered
	  if (err) throw err;
  
	  if (rows.length == 0) {
	      // bet not found
	      console.log(DICT.BET_RESPONSES.no_players_waiting_for_prizes);
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
		  statement_upd8 = "UPDATE matchmaking_bidder SET status='PRIZES' WHERE player_id="+row.player_id	    
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
setInterval(work, work_interval);