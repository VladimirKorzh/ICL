playerlist = []
teamA = []
teamB = []

# playerlist has to contain only 20 players at most
# or maybe only ten, to make sure that there
# would not be players who waited to play but 
# didn't end up getting picked
# this makes up to making a decision between
# for different supports

class Team():
  def __init__():
    self.players = []
    self.captain = None

  def set_captain(self, player):
    self.captain = player
    
  def captain_pick_player(self, playerslist):
    # inform the captain that he has to pick
    # one player for the role that he lacks
    # done via the WebPage side
    self.players.append(playerslist[3])
        
class FullCM_mode():
  def __init__(self, available_players_list):
    teamA = Team()
    teamB = Team()
    self.available_players_list = available_players_list

  def captains_vote(self):
    top = sorted(self.available_players_list, key=lambda player: player['exp'], reverse=True)[:5]
    # used in order to let people choose who
    # gets to be their captain. Only top Exp
    # players get to actually be captains.
    self.available_players_list.remove(self.teamA.captain)
    self.available_players_list.remove(self.teamB.captain)    

  def save_results(self):
    # gets the winner of the match and ajusts the ratings

  def start_flow():
    captains_vote()
    
    for i in range(1,11):
	if i%2 == 0:
	  teamA.captain_pick_player(self.available_players_list)
	else:
	  teamB.captain_pick_player(self.available_players_list)
	  
    self.save_results()