from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from game.models import Category, Game, GameItemLink
from game.core_control_methods.in_group import in_group_on_class
from QR2.settings import DEBUG

class Publish:
    class Publish(LoginRequiredMixin, View):

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'id' in request.POST:
                game = Game.objects.get(gameID=request.POST['id'])

                # If the game is published you only need to toggle the published flag which will take the game 'offline'
                if game.published is True:
                    game.published = False
                    game.save()
                    messages.add_message(request, messages.SUCCESS,
                                         f'Het spel <i>\'{game.gameName}\'</i> is succesvol ge-de-publiceerd')
                    return redirect('game:adminpanelGamesEdit', gameID=game.gameID)
                # If the game is not published all components need to reset (of userinput) before publishing.
                # For each chained category the chain integrity is checked.
                elif game.published is False:
                    allCategories = Category.objects.filter(game=game)

                    if allCategories:
                        for category in allCategories:
                            allItemsInCategory = GameItemLink.objects.filter(game=game, category=category)

                            # If a category is chained the chain integrity needs to be checked
                            if category.chained is True:
                                if category.firstItem is None:
                                    messages.add_message(request, messages.ERROR,
                                                         f'Er ging iets fout tijdens het publiceren van een Game! Controleer de item volgorde van <i>\'{category.categoryName}\'</i>.')
                                    messages.add_message(request, messages.DEBUG,
                                                         f'The first item from category with id <i>\'{category.categoryID}\'</i> is missing!')
                                    return redirect('game:adminpanelGamesEdit', gameID=request.POST['id'])  # error

                                counter = 1

                                item = category.firstItem
                                passedItems = [item.gameItemLinkID]

                                # Check whether all items in a category are sequentially linked
                                while not item.nextItem is None:
                                    # Check for loop in the items
                                    if item.nextItem.gameItemLinkID in passedItems:
                                        messages.add_message(request, messages.ERROR,
                                                             f'Er ging iets fout tijdens het publiceren van een Game! Controleer de item volgorde van <i>\'{category.categoryName}\'</i> er zit mogelijk een loop (cyclus) in.')
                                        return redirect('game:adminpanelGamesEdit', gameID=request.POST['id'])  # error
                                    item = item.nextItem
                                    passedItems.append(item.gameItemLinkID)
                                    counter += 1

                                # Check whether all items in a chained category are chained
                                if not counter == allItemsInCategory.count():
                                    messages.add_message(request, messages.ERROR,
                                                         f'Er ging iets fout tijdens het publiceren van een Game! Controleer de item volgorde van <i>\'{category.categoryName}\'</i> een van de items wordt mogelijk niet bereikt.')
                                    messages.add_message(request, messages.DEBUG,
                                                         f'The number of chained items in category with id <i>\'{category.categoryID}\'</i> do not match up with the total number of items in the category!')
                                    return redirect('game:adminpanelGamesEdit', gameID=request.POST['id'])  # error

                            # Setup maximum score for each category
                            category.reset()
                            for item in allItemsInCategory:
                                category.maxCategoryScore += item.maxScore

                            category.save()

                    allItems = GameItemLink.objects.filter(game=game)

                    # Reset all items in a game
                    for item in allItems:
                        item.reset()
                        item.save()

                    game.published = True
                    game.save()

                    messages.add_message(request, messages.SUCCESS,
                                         f'Het spel <i>\'{game.gameName}\'</i> is succesvol gepubliceerd')
                    return redirect('game:adminpanelGamesEdit', gameID=request.POST['id'])
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het publiceren van een Game!')

                messages.add_message(request, messages.DEBUG,
                                     '<i>\'id\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')

                return redirect('game:adminpanelGames')
