from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from game.models import Category, Game, GameItemLink
from game.forms import GameForm, AnnouncementForm
from game.core_control_methods.backend_socket_messenger import item_complete_by_GM, make_announcement, update_item, game_complete, category_complete
from game.core_control_methods.announcement import make_general_announcement
from game.core_control_methods.finish_by_gm import finish_by_gm
from game.core_control_methods.in_group import in_group, in_group_on_class
from QR2.settings import DEBUG


class Games:
    class Announcement(LoginRequiredMixin, View):
        """
        Get announcement from the announcement form and pass on to a socket_message distribution method.
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):
            return make_general_announcement(request, 'game:adminpanelGamesEdit', 'game:adminpanelGamesEdit')


    class Add(LoginRequiredMixin, View):
        """
        Attempts to add a new game item. This game is completely void of any items/categories/settings
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'newGameName' in request.POST:
                game = Game(gameName=request.POST['newGameName'])
                game.save()
                return redirect('game:adminpanelGames')
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout bij het toevoegen van een Game!')

                if 'gameID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelGames')

    class Delete(LoginRequiredMixin, View):
        """
        Attempts to delete an existing game item.
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'id' in request.POST:
                try:
                    game = Game.objects.get(gameID=request.POST['id'])
                except Game.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er is een fout opgetreden bij het verwijderen van een Game. Controleer of het spel nog bestaat.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id {request.POST["id"]}')
                    return redirect('game:adminpanelGames')

                # A game may only be removed when it is not published
                if game.published is True:
                    messages.add_message(request, messages.INFO,
                                         'De-publiceer het spel eerst voordat je aanpassingen maakt.')
                    return redirect('game:adminpanelGames')

                messages.add_message(request, messages.SUCCESS,
                                     'Game is succesvol verwijderd.')
                game.delete()
                return redirect('game:adminpanelGames')
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout bij het verwijderen van een Game!')

                messages.add_message(request, messages.DEBUG,
                                     '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelGames')

    class Get_All(LoginRequiredMixin, View):
        """
        Obtain a list of all the current active and inactive games
        """
        template_name = 'game/gameAdminpanel/games.html'

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request):
            games = Game.objects.order_by('publicationDate')

            context = {'games': games}

            return render(request, self.template_name, context)

    class Edit(LoginRequiredMixin, View):
        """
        Edit the settings of a game. Categories and items are also displayed.
        """
        template_name = 'game/gameAdminpanel/games_edit.html'

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request, gameID):
            """
            Render the game form and display the categories/game items
            """

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
            gameForm = GameForm(request.POST or None, instance=game)

            announcementForm = AnnouncementForm()

            # Disable the fields of the forms when the game is published
            if game.published is True:
                gameForm.disableFields()

            context = {'game': game, 'gameItems': gameItems, 'categories': categories,
                    'gameForm': gameForm, 'announcementForm': announcementForm}

            return render(request, self.template_name, context)

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request, gameID):
            """
            Update the game using the form
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'id' in request.POST:
                game = Game.objects.get(gameID=request.POST['id'])

                # Populate form with post data
                gamePostForm = GameForm(request.POST, instance=game)

                # Check whether the given form is valid
                if gamePostForm.is_valid():
                    gamePostForm.save()
                    return redirect('game:adminpanelGamesEdit', gameID=request.POST['id'])
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

                return redirect('game:adminpanelGamesEdit', gameID=gameID)

    class finishItemByGM(LoginRequiredMixin, View):
        """
        Advance a game item as gamemaster. The gamemaster is able to assign a score to an item between 0 and
        the max possible score.
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):
            return finish_by_gm(request, 'game:adminpanelGamesEdit', 'game:adminpanelGamesEdit')


    class Duplicate(LoginRequiredMixin, View):
        """
        Duplicates a given Game including GameItemLinks and Categories. The duplicated game object has the
        same name as the old one with addition to the "Kopie" postfix.
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'id' in request.POST:
                try:
                    new_game = Game.objects.get(gameID=request.POST['id'])
                except Game.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens afsluiten van een game item!')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{request.POST["gameID"]}\'</i>')
                    return redirect('game:adminpanelGames')

                categories = Category.objects.filter(game=new_game)

                original_name = new_game.gameName

                # Remove ID of current object to force a new database entry at .save()
                new_game.gameID = None
                new_game.gameName += ' Kopie'
                
                if new_game.accessThroughTag or new_game.accessTag is not None:
                    new_game.accessTag += ' Kopie'

                # Ensure that the game is not published
                new_game.published = False

                # Add new entry to database
                new_game.save()

                # Duplicate categories of original game and transfer to new game
                if categories:
                    for new_category in categories:
                        # Fetch all items related to a given category
                        all_items = GameItemLink.objects.filter(category=new_category)

                        new_category.firstItem = None
                        new_category.game = new_game
                        new_category.categoryID = None

                        # Reset depends on the categoryID so always reset after saving to prevent sending None to reset
                        # The double save is required to push the reset data to the database
                        new_category.save()
                        new_category.reset()
                        new_category.save()

                        if all_items:
                            for new_item in all_items:
                                new_item.nextItem = None
                                new_item.game = new_game
                                new_item.category = new_category
                                new_item.gameItemLinkID = None

                                # Reset depends on the gameItemlinkID so always reset after saving to prevent sending None to reset
                                # The double save is required to push the reset data to the database
                                new_item.save()
                                new_item.reset()
                                new_item.save()

                messages.add_message(request, messages.SUCCESS, f'Het spel <i>\'{original_name}\'</i> is succesvol gedupliceerd')
                return redirect('game:adminpanelGames')
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het dupliceren van een Game!')

                messages.add_message(request, messages.DEBUG,
                                     '<i>\'id\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')

                return redirect('game:adminpanelGames')
