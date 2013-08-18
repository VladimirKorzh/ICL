from django.contrib import admin
from matchmaking.models import Player, Lobby, Search

admin.site.register(Lobby)
admin.site.register(Player)
admin.site.register(Search)
