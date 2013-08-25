
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

var actions_collect = [];
var actions_award   = [];

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
	console.log('tradeProposed, but we do not approve it.');
//	bot.respondToTrade(tradeID, true);
	// we are no longer accepting trades from people
	// we only send trade requests ourselves
});

bot.on('sessionStart', function(otherClient) {
	client = otherClient;
	
	// variables that hold the information about current bet
	bet_id  = 0;
	bet_itemrarity = '';
	bet_itemcount  = 0;
	
	trade_window_items = []
	
	console.log('trading with ' + bot.users[client].playerName);
	steamTrade.open(otherClient);
	
	steamTrade.loadInventory(570, 2, function(inv) {
	  inventory = inv;
	});
});


steamTrade.on('offerChanged', function(added, item) {
	console.log('===> they ' + (added ? 'added ' : 'removed ') + item.name);
	itemtags = item.tags;
	correct_item = false;
	correct_rariry = false;
	
	itemtags.forEach(function(tag){      
	      if (tag.category_name == 'Type') {
		    console.log('Type:' + tag.internal_name);
		    if (tag.internal_name == 'DOTA_WearableType_Wearable') {
			correct_item = true;
		    }
	      }    
	      if (tag.category_name == 'Rarity') {
		    console.log('Rarity:' + tag.name);
		    if ( tag.name == bet_itemrarity ){		      
		      correct_rariry = true;
		    }
	      }		
	      if (tag.category_name == 'Hero') {
		    console.log('Hero:' + tag.name);
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
	
	message = minimap.map({"itemsleft": bet_itemcount - trade_window_items.length, "itemrarity": bet_itemrarity},DICT.BET_RESPONSES.bet_items_left);	
	console.log(message);
	friends.messageUser(client, message, bot);	
});



steamTrade.on('ready', function() {
      // amount of items doesn't match the bet 
      if (bet_itemcount != trade_window_items.length) {
	    message = minimap.map({"itemcount": trade_window_items.length, "bet_itemcount": bet_itemcount},DICT.BET_RESPONSES.bet_invalid_itemcount);
	    console.log(message);
	    friends.messageUser(client, message, bot);
      }  
      else {
	    // if all goes through then we are good to go
	    steamTrade.ready(function() {
	      message = minimap.map({"betid": bet_id}, DICT.BET_RESPONSES.bet_status_valid);
	      console.log(message);
	      friends.messageUser(client, message, bot);
	      steamTrade.confirm();	     
	    });
      }
});

steamTrade.on('end', function(result) {
      console.log('trade', result);
  //  TODO Write result to database      
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
/*
function readdb() {
    console.log('DEBUG',actions_collect);
    if (actions_collect.length == 0 && actions_award.length == 0) {
	  // MONSTER SQL SELECT that returns players that are waiting to place their bet
	  statement_collect = "SELECT matchmaking_bet.item_rarity as ir, matchmaking_bet.amount as am, matchmaking_player.uid as uid FROM matchmaking_bet INNER JOIN matchmaking_bidder, matchmaking_player ON matchmaking_bet.id = matchmaking_bidder.bet_id AND matchmaking_bidder.status = 'WAITING' AND matchmaking_bidder.id = matchmaking_player.id";
     
	  db.all(statement_collect, function(err, rows) {
		// throw an error if encountered
		if (err) throw err;
		    
		if (closed_bets_rows.length == 0) {
		    // bet not found
		    console.log(DICT.BET_RESPONSES.no_players_waiting_to_bet);
		    return;
		}
		else {
		    rows.forEach( function(row) {
			actions_collect.push({"item_rarity": row.ir, "amount": row.am, "uid": row.uid});
		    });
		}
	  });
	  
	  // MONSTER statement that returns players that wait for their prizes
	  statement_award = "SELECT matchmaking_bet.item_rarity, matchmaking_bet.amount, matchmaking_player.uid FROM matchmaking_bet INNER JOIN matchmaking_bidder, matchmaking_player ON matchmaking_bet.id = matchmaking_bidder.bet_id AND matchmaking_bidder.status = 'SUBMITTED' AND matchmaking_bet.result = matchmaking_bidder.side";
	  
	  db.all(statement_award, function(err, rows) {
		// throw an error if encountered
		if (err) throw err;
		    
		if (closed_bets_rows.length == 0) {
		    // bet not found
		    console.log(DICT.BET_RESPONSES.no_players_waiting_for_prizes);
		    return;
		}
		else {
		    rows.forEach( function(row){
			actions_award.push({"item_rarity": row.ir, "amount": row.am, "uid": row.uid});
		    });
		}
	  });
    }
} // end refresh function

update_interval = 5000;
setInterval(readdb(), update_interval);*/