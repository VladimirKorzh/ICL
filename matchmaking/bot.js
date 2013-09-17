
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

// DON'T Respond to messages at all. Simply ignore them 
bot.on('message', function(source, message, type, chatter) {
    console.log('We have received a message:', message);
});

// Add friends automatically.
bot.on('relationship', function(other, type){  
      if(type == Steam.EFriendRelationship.PendingInvitee) {
            console.log('friend invite received!',other);
            bot.addFriend(other);
            
            // check if we have any requests from this guy
            check_request(other);
      }
});

// make sure we clean after ourselves
process.on( 'SIGINT', function() {
  console.log( "\nGracefully shutting down from  SIGINT (Crtl-C)" )
  
  // close connection to database
  db.close();
  process.exit( )
});














function acceptable(item, rarity) { 
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
            if ( tag.name == rarity) {
              correct_rariry = true;
            }
          }
      });
      
      is_tradable = item.tradable;
      
      // return true tells filter funciton that this item
      // matches our needs.
      if (correct_item == true && correct_rariry == true && is_tradable == true) {
          return true;
      }
      else {
          return false;
      }
}

// Gets called when trade window appears on the screen
// Here we place items that award to the player
bot.on('sessionStart', function(otherClient) {
    time_lastping = new Date().getTime() / 1000;
    // variable to hold other client info 
    client = otherClient;   
    console.log('sessionStart with', otherClient);

    // structure to hold items offered by trade partner
    their_offer = [];  
    our_proposition = [];
    
    steamTrade.open(otherClient, function(){
        if (current_task.action == 1) {
            console.log('Giving items back to the player');
            steamTrade.loadInventory(570, 2, function(inv) {      
                // find items that match 
                rare     = inv.filter(function(item){ return acceptable(item, "Rare") });   
                common   = inv.filter(function(item){ return acceptable(item, "Common") });
                uncommon = inv.filter(function(item){ return acceptable(item, "Uncommon") });
                
                our_proposition = our_proposition.concat( rare.slice(0, current_task.rare) );
                our_proposition = our_proposition.concat( uncommon.slice(0,current_task.uncommon) );
                our_proposition = our_proposition.concat( common.slice(0, current_task.common) );
                
                steamTrade.addItems(our_proposition);
            });
        }   
        
        if (current_task.type == 0){
            // if our task is to collect items than we simply wait for the user
            // to place them in the trade window and react accordingly
            console.log('Collecting items from player');
        }
    });
    
    if ('undefined' === typeof current_task.player_id) {
      steamTrade.cancel();
      return;
    }    
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
          if ( tag.name == "Rare"  || tag.name == "Common"  || tag.name == "Uncommon" ){   
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
        their_offer.push(item);    	      
        msg = message + ' is accepted.';
        console.log(msg);
        bot.sendMessage(client, msg, Steam.EChatEntryType.ChatMsg);
    }
    
    // if the user has removed a valid item
    if (!added) {
        // find that item in our structure and remove it
        var index = their_offer.indexOf(item);    
        their_offer.splice(index, 1);
    }
});


// This function gets called when the user presses the ready button
// here we check that the deal is valid.
steamTrade.on('ready', function() {      
      time_lastping = new Date().getTime() / 1000;  
      steamTrade.ready(function() {
          console.log('confirming');
          time_lastping = new Date().getTime() / 1000;
          steamTrade.confirm( function (){
              console.log("Pressing 'Make Trade' button.");	  
              time_lastping = new Date().getTime() / 1000;
          });
      });            
});




// this function gets called after the trade is finished
// result variable is supposed to hold the string representing
// the status of the trade.
steamTrade.on('end', function(result, items) {
    time_lastping = new Date().getTime() / 1000;
    console.log('End trade event', result);
       
    if (result === 'complete') {
      
      // marking the transaction in db
      statement = "UPDATE matchmaking_botrequest SET status=1 WHERE player_id="+current_task.player_id; 
      
      db.run(statement, function(err){
        if (err) throw err;
      });
      console.log('db updated');
      
      if (current_task.action == 0) {
          rare     = their_offer.filter(function(item){ return acceptable(item, "Rare") });   
          common   = their_offer.filter(function(item){ return acceptable(item, "Common") });
          uncommon = their_offer.filter(function(item){ return acceptable(item, "Uncommon") });      
          
          console.log('rare:', rare.length);
          console.log('common:', common.length);
          console.log('uncommon:', uncommon.length);
          
          
          statement = "UPDATE matchmaking_inventory SET common = common+"+common.length+" WHERE id="+current_task.inv_id;
          
          db.run(statement, function(err){
            if (err) throw err;
          });          

          statement = "UPDATE matchmaking_inventory SET uncommon = uncommon+"+uncommon.length+" WHERE id="+current_task.inv_id;
          
          db.run(statement, function(err){
            if (err) throw err;
          });          
                    
          statement = "UPDATE matchmaking_inventory SET rare = rare+"+rare.length+" WHERE id="+current_task.inv_id;
          
          db.run(statement, function(err){
            if (err) throw err;
          });          
                    
          console.log('inventory values updated');
      }
      
      if (current_task.action == 1) {
          rare     = our_proposition.filter(function(item){ return acceptable(item, "Rare") });   
          common   = our_proposition.filter(function(item){ return acceptable(item, "Common") });
          uncommon = our_proposition.filter(function(item){ return acceptable(item, "Uncommon") });      
          
          console.log('rare:', rare.length);
          console.log('common:', common.length);
          console.log('uncommon:', uncommon.length);        
        
          statement = "UPDATE matchmaking_inventory SET common = common-"+common.length+" WHERE id="+current_task.inv_id;
          
          db.run(statement, function(err){
            if (err) throw err;
          });          

          statement = "UPDATE matchmaking_inventory SET uncommon = uncommon-"+uncommon.length+" WHERE id="+current_task.inv_id;
          
          db.run(statement, function(err){
            if (err) throw err;
          });          
                    
          statement = "UPDATE matchmaking_inventory SET rare = rare-"+rare.length+" WHERE id="+current_task.inv_id;
          
          db.run(statement, function(err){
            if (err) throw err;
          });          
                    
          console.log('inventory values updated');          
      }
      
        
      keep_or_remove(current_task.uid)
      // empty the task
      current_task = '';  
      time_lastping = '';
    }     
});

function check_request(uid){
    console.log('Checking for user request', uid);
    
    // find this player in database
    statement = "SELECT player.id as id FROM matchmaking_player as player WHERE player.uid="+uid;
    player_id = 0;
    
    db.each(statement, function(err, row){
        if (err) throw err;  
        player_id = row.id; 
        statement = "SELECT player.id as player_id, request.common as common, request.uncommon as uncommon, request.rare as rare, request.action as action, inventory.id as inv_id FROM matchmaking_botrequest as request, matchmaking_inventory AS inventory, matchmaking_player as player WHERE request.player_id="+player_id+" AND player.id="+player_id+" AND request.status = 0 AND inventory.id = player.inventory_id";

        
        db.all(statement, function (err, rows) {
            if (err) throw err;

            if (rows.length == 0) {
                console.log('Request not found');
            }
            else {
                rows.forEach( function(request) {
                    console.log('Request found', request);
                    actions.push({         
                                "uid":       uid,
                                "player_id": request.player_id,
                                "inv_id":    request.inv_id,
                                "action":    request.action,
                                "rare":      request.rare,
                                "common":    request.common,
                                "uncommon":  request.uncommon                         
                                });          
              }); // end for each row that we've found    
            } // end if found rows 
            keep_or_remove(uid);
        }); // end db.all           
        
    }); // end for each player_id row  
} // end check_request

function keep_or_remove(uid) {
  // this function is used to determine if there are any requests
  // related to the provided user. In case if there are none, it 
  // removes the user from friend list.
  console.log('keep_or_remove', uid);
  
  found_other_tasks = false;
  for (var i=0; i<actions.length; i++) {    
    action = actions[i];
    if (action.uid == uid){
      found_other_tasks = true;
    } 
  } // end for 
  
  if (!found_other_tasks) {
    console.log('Request not found. Removing friend');
    bot.removeFriend(uid);     
    return;
  } 
  console.log('Keeping this friend');
} // end function






function tick(){
  if (time_lastping != '' && current_task != '') {
      time_now = new Date().getTime() / 1000;      
      if ((time_now - time_lastping) > 30) {
          console.log('task takes too much time, cancelling it');
          steamTrade.cancel();
          keep_or_remove(current_task.uid);
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
      console.log('current_task', current_task);
      bot.trade(current_task.uid);
      time_lastping = new Date().getTime() / 1000;
  }
}

// Setup speed of tick function.
setInterval(tick, 1000);