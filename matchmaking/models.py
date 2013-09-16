from django.db import models

class PlayerInventory(models.Model):
    # used to store items for betting and tournaments
    common   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    uncommon = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rare     = models.DecimalField(max_digits=5, decimal_places=2, default=0)

class PlayerRating(models.Model):
    # total games on this account
    total_games = models.PositiveSmallIntegerField(default=0)
    
    # total amount of games for the past 28 days
    month_games = models.PositiveSmallIntegerField(default=0)
    
    # calculated skill experience
    skillrating = models.PositiveSmallIntegerField(default=0)
    
    # amount of games in each skill rating
    veryhigh    = models.PositiveSmallIntegerField(default=0)
    high        = models.PositiveSmallIntegerField(default=0)
    normal      = models.PositiveSmallIntegerField(default=0)
    
    # extra games per month
    extra_pts = models.PositiveSmallIntegerField(default=0)  

    # total rating from matches
    matches_pts = models.PositiveSmallIntegerField(default=0)
    
    # last time when this table was refreshed
    last_updated = models.DateTimeField(auto_now=True)        
    
class Player(models.Model):
    # general player information that we get from valve
    uid      = models.CharField(max_length=40)
    nickname = models.CharField(max_length=80)
    
    # a nickname that could be used in mumble
    mumble_nickname = models.CharField(max_length=80)
    avatar          = models.CharField(max_length=120)

    # player defined roles   # 0 - Not set
    # 1 - Carry      # 2 - SoloMid
    # 3 - Offlane    # 4,5 - Support
    pri_role = models.PositiveSmallIntegerField(default=0)
    alt_role = models.PositiveSmallIntegerField(default=0)

    # pointers to various information structures
    inventory = models.ForeignKey(PlayerInventory)
    rating    = models.ForeignKey(PlayerRating)

    
class BotRequest(models.Model):
    # player that requested interraction
    player = models.ForeignKey(Player)
    
    # Interraction type # 1 - Reward  # 0 - Collect
    action = models.PositiveSmallIntegerField(default=0)
    
    # Are we done? 
    status = models.BooleanField(default=False)
    
    # how many items does the person want to cash
    common = models.PositiveSmallIntegerField(default=0)
    uncommon = models.PositiveSmallIntegerField(default=0)
    rare = models.PositiveSmallIntegerField(default=0)
    
    # when was that request finished
    last_updated = models.DateTimeField(auto_now=True)
     
class ValveApiCounts(models.Model):
    # A class that holds the information about the amount
    # of api calls that the application has made each day
    date    = models.DateField()
    amount  = models.PositiveIntegerField()



    
    
#class Tournament(models.Model):
    ## a model that represents a tournament in db.
    ## it holds all the information about the tournament,
    ## its type and other meta information. 
    
    ## date\time of tournament start
    #datetime = models.DateTimeField()

    ## is the tournament free to enter
    #entrycommon   = models.PositiveSmallIntegerField(default=0)
    #entryuncommon = models.PositiveSmallIntegerField(default=0)
    #entryrare     = models.PositiveSmallIntegerField(default=0)    
    
#class TournamentTeam(models.Model):
    ## temporary team for the tournament
    #tournament = models.ForeignKey(Tournament)


 
#class PlayerParticipant(models.Model):
    ## holds the information about the player-tournament relationships
    ## basically holds all the registered players for tournament.
    #player = models.ForeignKey(Player)  
    #tournament = models.ForeignKey(Tournament)
    
    ## auto created team for this player or a set of players
    ## for this particular tournament
    #team = models.ForeignKey(TournamentTeam)
    
    ## registration date\time
    #last_updated = models.DateTimeField(auto_now=True)  
 

 
#class Match(models.Model):
    ## a model that represents a match
    ## it is responsible for holding passwords and pointers
    ## to the teams.
    
    ## which tournament does this match belong to
    #tournament = models.ForeignKey(Tournament, null=True)
    
    ## round this match belongs to
    #round = models.PositiveSmallIntegerField(default=0)
      
    ## who won the match # 0 - Not decided
    ## 1 - Side A won the match # 2 - Side B won the match
    #result = models.PositiveSmallIntegerField(default=0)
        
    ## which teams participate in this match
    #sidea = models.ForeignKey(TournamentTeam)
    #sideb = models.ForeignKey(TournamentTeam)
    
    ## started?
    #started = models.BooleanField(default=False)
    
    ## lobby password
    #lobbypass = models.PositiveSmallIntegerField(default=0)
    
    ## passwords for both sides
    #sideapass = models.PositiveSmallIntegerField(default=0)
    #sidebpass = models.PositiveSmallIntegerField(default=0)  
    
    ## time this record was last modified, for rating purposes
    #last_updated = models.DateTimeField(auto_now=True)
    
    ## description for Show matches etc. if manually created
    #description = models.CharField(max_length=140,default="")
 
#class PlayerBet(models.Model):
    ## which player made the bet
    #player = models.ForeignKey(Player)
    
    ## which match is he betting on
    #match = models.ForeignKey(Match)
      
    #common   = models.PositiveSmallIntegerField(default=0)
    #uncommon = models.PositiveSmallIntegerField(default=0)
    #rare     = models.PositiveSmallIntegerField(default=0)

 
 
 
 
 
 

  
      