from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from game.models import Category, Game, GameItemLink
from game.forms import GameMasterForm_Game, AnnouncementForm
from game.core_control_methods.announcement import make_general_announcement
from game.core_control_methods.finish_by_gm import finish_by_gm
from game.core_control_methods.in_group import in_group_on_class
from QR2.settings import DEBUG


class GameMaster:
    class Get_All(LoginRequiredMixin, View):
        """
        Obtain a list of all the current active and inactive games
        """
        template_name = 'game/gameAdminpanel/game_master_index.html'

        @in_group_on_class(groups=['gameMaster'])
        def get(self, request):
            games = Game.objects.filter(published=True).order_by('publicationDate')

            context = {'games': games}

            return render(request, self.template_name, context)

    class Announcement(LoginRequiredMixin, View):
        """
        Get announcement from the announcement form and pass on to a socket_message distribution method.
        """

        @in_group_on_class(groups=['gameMaster'])
        def post(self, request):
            return make_general_announcement(request, 'game:gamemasterPanel', 'game:gamemasterPanel')

    class finishItemByGM(LoginRequiredMixin, View):
        """
        Advance a game item as gamemaster. The gamemaster is able to assign a score to an item between 0 and
        the max possible score.
        """

        @in_group_on_class(groups=['gameMaster'])
        def post(self, request):
            return finish_by_gm(request, 'game:gamemasterPanel', 'game:gamemasterPanel')

    class GameMasterPanel(LoginRequiredMixin, View):
        template_name = 'game/gameAdminpanel/games_master_panel.html'

        @in_group_on_class(groups=['gameMaster'])
        def get(self, request, gameID):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            try:
                game = Game.objects.get(gameID=gameID)
                gameItems = GameItemLink.objects.filter(game=game).order_by('itemOrder')
                categories = Category.objects.filter(game=game)
            except Game.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er is een fout opgetreden bij het openen van het spel. Controleer of het spel nog bestaat.')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{gameID}\'</i>')
                return redirect('game:adminpanelGames')

            # Con struct the forms
            gameForm = GameMasterForm_Game(instance=game)

            if game.noDateNorTime:
                gameForm.disableFields()

            announcementForm = AnnouncementForm()

            context = {
                'game': game,
                'gameItems': gameItems,
                'categories': categories,
                'gameForm': gameForm,
                'announcementForm': announcementForm
            }

            return render(request, self.template_name, context)

        @in_group_on_class(groups=['gameMaster'])
        def post(self, request, gameID):
            """
            Update the game using the form
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'id' in request.POST:
                game = Game.objects.get(gameID=request.POST['id'])

                # Populate form with post data
                gamePostForm = GameMasterForm_Game(request.POST, instance=game)

                # Check whether the given form is valid
                if gamePostForm.is_valid():
                    gamePostForm.save()
                    return redirect('game:gamemasterPanel', gameID=request.POST['id'])
                else:
                    messages.add_message(request, messages.ERROR,
                                         'Er is iets fout in de ingevulde velden!')
                    return self.get(request, gameID)

            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het aanpassen van het spel!')

                messages.add_message(request, messages.DEBUG,
                                     '<i>\'id\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')

                return redirect('game:gamemasterPanel', gameID=gameID)