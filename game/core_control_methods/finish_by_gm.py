from django.shortcuts import redirect
from django.contrib import messages

from game.models import Game, GameItemLink
from game.core_control_methods.backend_socket_messenger import item_complete_by_GM, update_item, game_complete, category_complete
from QR2.settings import DEBUG

def finish_by_gm(request, on_success, on_fail):
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    if 'gameID' in request.POST and 'itemID' in request.POST and 'score' in request.POST:
        try:
            game = Game.objects.get(gameID=request.POST['gameID'])
            item = GameItemLink.objects.get(gameItemLinkID=request.POST['itemID'])
        except Game.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 'Er ging iets fout tijdens het afsluiten van een game item!')
            messages.add_message(request, messages.DEBUG,
                                 f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{request.POST["gameID"]}\'</i>')
            return redirect('game:adminpanelGames')
        except GameItemLink.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 'Er ging iets fout tijdens het afsluiten van een game item!')
            messages.add_message(request, messages.DEBUG,
                                 f'The exception <i>\'GameItemLink.DoesNotExist\'</i> occurred on id <i>\'{request.POST["itemID"]}\'</i>')
            return redirect(on_fail, gameID=request.POST['gameID'])

        if item.gameItemStateCompleted:
            messages.add_message(request, messages.WARNING,
                                 'Deze gameItem is al afgesloten!')
            return redirect(on_fail, gameID=request.POST['gameID'])

        if item.game != game:
            messages.add_message(request, messages.ERROR,
                                 'Deze gameItem zit niet in dit spel!')
            messages.add_message(request, messages.DEBUG,
                                 f'<i>\'GameItemLink\'</i> with id <i>\'{request.POST["itemID"]}\'</i> was not Game with id <i>\'{request.POST["gameID"]}\'</i>. Check whether the post form contains the correct IDs!')
            return redirect(on_fail, gameID=request.POST['gameID'])

        # Check whether the item needs to be continued by the Gamemaster and assign a given score
        if item.gameItemContinueByGM is False:
            messages.add_message(request, messages.ERROR,
                                 'Deze gameItem mag niet worden afgesloten door de gamemaster!')
            messages.add_message(request, messages.DEBUG,
                                 f'<i>\'GameItemLink\'</i> with id <i>\'{request.POST["itemID"]}\'</i> is not allowed to be finished by the gamemaster. Check whether the post form contains the correct IDs!')
            return redirect(on_fail, gameID=request.POST['gameID'])

        # Fetch score
        maxPossibleScore = item.maxScore
        givenScore = int(request.POST['score'])

        # Cap maximum possible score to the max score of the given GameItemLink
        if maxPossibleScore >= givenScore >= 0:
            item.obtainedScore = givenScore
        else:
            item.obtainedScore = item.maxScore

        # Finish game by updating flags
        item.gameItemStateVisited = True
        item.gameItemStateCompleted = True

        item.save()

        # Update category score
        category = item.category
        category.obtainedCategoryScore += item.obtainedScore

        category.save()

        # Send socket messages to connected clients
        item_complete_by_GM(item.gameItemLinkID, givenScore, maxPossibleScore)
        update_item(item.gameItemLinkID)
        if category.is_completed():
            category_complete(category.categoryID)
        if item.game.is_completed():
            game_complete(item.game.gameID)

        messages.add_message(request, messages.SUCCESS,
                             'Item is succesvol afgesloten!')
        return redirect(on_success, gameID=request.POST['gameID'])
    else:
        # Problems with ID fetching
        messages.add_message(request, messages.ERROR,
                             'Er ging iets fout tijdens het afsluiten van een game item!')

        if 'gameID' not in request.POST:
            messages.add_message(request, messages.DEBUG,
                                 '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
        if 'categoryID' not in request.POST:
            messages.add_message(request, messages.DEBUG,
                                 '<i>\'categoryID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
        if 'score' not in request.POST:
            messages.add_message(request, messages.DEBUG,
                                 '<i>\'score\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
        return redirect('game:adminpanelModules')