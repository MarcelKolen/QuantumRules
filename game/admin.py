from django.contrib import admin

from .models import Game, GameItemLink, Category

admin.site.register(Game)
admin.site.register(GameItemLink)
admin.site.register(Category)

