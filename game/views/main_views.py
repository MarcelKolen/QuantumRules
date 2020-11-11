from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import datetime
from django.views import generic
from django.db.models import Q
from django.contrib import messages

from game.models import Game, GameItemLink, Category
from game.core_control_methods.backend_socket_messenger import update_item
from game.running_rules import render_item_rules, post_item_rules
from QR2.settings import DEBUG


class GamesIndexView(generic.ListView):
    """
    List all the active games
    """
    template_name = 'game/index.html'
    context_object_name = 'activeGameList'

    def get_queryset(self):
        currentDateTime = datetime.now()
        now_plus_30mins = currentDateTime + timedelta(minutes=30)
        now_minus_30mins = currentDateTime - timedelta(minutes=30)

        if self.request.user.is_authenticated and self.request.user.is_staff:
            games = Game.objects.all()
        else:
            # Only display games that are both open and published and also are within a certain given time range (provided that it is time dependant)
            games = Game.objects.filter(published=True, accessThroughTag=False).filter(
                Q(noDateNorTime=True) | Q(noDateNorTime=False, startDateTime__lte=now_plus_30mins.astimezone(),
                                      endDateTime__gte=now_minus_30mins.astimezone()))

        return games.order_by('-publicationDate')


def is_game_accessable(request, gameID):
    """
    Check whether a game should still be accessible
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    # For game debugging, gamemasters should be able to always join a game
    if request.user.is_authenticated and request.user.is_staff:
        return True

    try:
        game = Game.objects.get(gameID=gameID)
    except Game.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Het spel is niet gevonden!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{request.POST["id"]}\'</i>')
        return False

    # Game needs to be both open en published
    if game.published is False:
        return False

    currentDateTime = datetime.now()
    now_plus_30mins = currentDateTime + timedelta(minutes=30)
    now_minus_30mins = currentDateTime - timedelta(minutes=30)

    # Check whether game is still within time
    if game.noDateNorTime is False:
        if game.startDateTime >= now_plus_30mins.astimezone() or now_minus_30mins.astimezone() >= game.endDateTime:
            return False

    return True


def is_game_running(request, gameID):
    """
    Check whether a game should still be accessible
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    # For game debugging, gamemasters should be able to always join a game
    if request.user.is_authenticated and request.user.is_staff:
        return True

    try:
        game = Game.objects.get(gameID=gameID)
    except Game.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Het spel is niet gevonden!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{request.POST["id"]}\'</i>')
        return False

    # Game needs to be both open en published
    if game.published is False or game.open is False:
        return False

    currentDateTime = datetime.now()

    # Check whether game is still within time
    if game.noDateNorTime is False:
        if game.startDateTime >= currentDateTime.astimezone() or currentDateTime.astimezone() >= game.endDateTime:
            return False

    return True


def game_tag_entry(request):
    if request.method == 'POST':
        if 'gameTag' in request.POST:
            try:
                game = Game.objects.get(accessTag=request.POST['gameTag'])
            except Game.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Het spel is niet gevonden!')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'Game.DoesNotExist\'</i> occurred on accessTag <i>\'{request.POST["gameTag"]}\'</i>')
                return redirect('game:index')

            return redirect('game:gameIndex', gameID=game.gameID)
        else:
            # Problems with ID fetching
            messages.add_message(request, messages.ERROR,
                                 'Er ging iets mis met het invoeren van de gametag!')

            messages.add_message(request, messages.DEBUG,
                                 '<i>\'gameTag\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')

            return redirect('game:index')
    else:
        messages.add_message(request, messages.WARNING,
                             'Er ging iets mis met het invoeren van de gametag!')
        return redirect('game:index')

def game_items_index(request, gameID):
    if is_game_accessable(request, gameID) is False:
        messages.add_message(request, messages.INFO,
                             'Het spel is afgelopen!')
        return redirect('game:index')

    game_is_running = True
    if is_game_running(request, gameID) is False:
        game_is_running = False

    template_name = 'game/game_content.html'

    # Try to fetch game object. If failed throw a 404.
    game = get_object_or_404(Game, gameID=gameID)

    items = GameItemLink.objects.filter(game=game).order_by('itemOrder')
    categories = Category.objects.filter(game=game)

    context = {'items': items, 'categories': categories, 'game': game, 'game_is_running': game_is_running}
    return render(request, template_name, context)


def render_item(request, gameID, ID, is_cat):
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    if is_game_accessable(request, gameID) is False:
        messages.add_message(request, messages.INFO,
                             'Het spel is afgelopen!')
        return redirect('game:index')

    if is_game_running(request, gameID) is False:
        return redirect('game:gameIndex', gameID=gameID)

    # Try to fetch game object. If failed throw a 404.
    game = get_object_or_404(Game, gameID=gameID)

    if game.is_completed():
        messages.add_message(request, messages.INFO,
                             f'Alle onderdelen van <i>\'{game.gameName}\'</i> zijn afgesloten!')

    # Check what the given ID is meant for.
    # In case of 'cat', the ID is for a category and the item to be rendered is found by traversing the category.
    # In case of 'item', the ID is for a GameItemLink and the item to be rendered is found in the link itself.
    if is_cat == 'cat':
        try:
            category = Category.objects.get(categoryID=ID)
        except Category.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 'Er is een fout opgetreden bij het openen van een onderdeel!')
            messages.add_message(request, messages.DEBUG,
                                 f'The exception <i>\'Category.DoesNotExist\'</i> occurred on id {ID}')
            return redirect('game:gameIndex', gameID=gameID)

        if category.is_completed():
            messages.add_message(request, messages.INFO,
                                 f'{category.categoryName} is afgesloten!')
            return redirect('game:gameIndex', gameID=gameID)

        # A given category must be chained
        if category.chained is False:
            messages.add_message(request, messages.ERROR,
                                 'Er is een fout opgetreden bij het openen van een onderdeel!')
            messages.add_message(request, messages.DEBUG,
                                 f'The <i>\'Category\'</i> with id {ID} is not chained however the render_item method was initiated as a chained category render.')
            return redirect('game:gameIndex', gameID=gameID)

        # Look for the first valid item in the category chain
        item = category.firstItem

        while item is not None and item.gameItemStateCompleted:
            item = item.nextItem

        if item is None:
            messages.add_message(request, messages.ERROR,
                                 'Er is een fout opgetreden bij het openen van een onderdeel!')
            messages.add_message(request, messages.DEBUG,
                                 f'The <i>\'Category\'</i> with id {ID} is not chained however the render_item method was initiated as a chained category render.')
            return redirect('game:gameIndex', gameID=gameID)
    elif is_cat == 'item':
        try:
            item = GameItemLink.objects.get(gameItemLinkID=ID)
        except GameItemLink.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 'Er is een fout opgetreden bij het openen van een onderdeel!')
            messages.add_message(request, messages.DEBUG,
                                 f'The exception <i>\'GameItemLink.DoesNotExist\'</i> occurred on id {ID}')
            return redirect('game:gameIndex', gameID=gameID)

        if item.category.chained is True:
            messages.add_message(request, messages.ERROR,
                                 'Er is een fout opgetreden bij het openen van een onderdeel!')
            messages.add_message(request, messages.DEBUG,
                                 f'The <i>\'GameItemLink\'</i> with id {ID} is not chained however the render_item method was initiated as a chained category render.')
            return redirect('game:gameIndex', gameID=gameID)
    else:
        return redirect('game:gameIndex', gameID=gameID)

    # Apply all rules and checks to a found game item
    res = render_item_rules(request, item, game)
    if res[0] is False:
        return res[1]

    # Set item states and push status to all connected clients
    item.gameItemStateVisited = True
    item.save()
    update_item(item.gameItemLinkID)

    # Render item module
    if item.module_item_handlers is False:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden bij het openen van een onderdeel!')
        messages.add_message(request, messages.DEBUG,
                             f'The <i>\'module\'</i> associated with the <i>\'GameItemLink\'</i> with id {item.gameItemLinkID} didn\'t return a render.')
        return redirect('game:gameIndex', gameID=gameID)
    else:
        return item.module_item_handlers().render_module(request, item.game.gameID, item.gameItemLinkID)


def module_item_post(request, gameID, itemID):
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    if is_game_accessable(request, gameID) is False:
        messages.add_message(request, messages.INFO,
                             'Het spel is afgelopen!')
        return redirect('game:index')

    if is_game_running(request, gameID) is False:
        return redirect('game:gameIndex', gameID=gameID)

    if request.method == 'POST':
        if 'gameID' in request.POST and 'itemID' in request.POST:
            # Fetch item to post data to
            try:
                item = GameItemLink.objects.get(gameItemLinkID=request.POST['itemID'])
                game = Game.objects.get(gameID=request.POST['gameID'])
            except GameItemLink.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er is een fout opgetreden bij het versturen van een antwoord!')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'GameItemLink.DoesNotExist\'</i> occurred on id {request.POST["itemID"]}')
                return redirect('game:gameIndex', gameID=request.POST['gameID'])
            except Game.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er is een fout opgetreden bij het versturen van een antwoord!')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id {request.POST["gameID"]}')
                return redirect('game:gameIndex', gameID=request.POST['gameID'])

            # Apply all rules and checks to a found game item
            if post_item_rules(request, item, game) is False:
                return redirect('game:gameIndex', gameID=request.POST['gameID'])

            # Attempt to send the post data to the input handler connected to the item
            if item.module_item_handlers is not False:
                # The input to the input handler is the POST data in a request. The post data is processed into a
                # dictionary per standard. The request data must also be send to leave the option open for
                # raw input processing.

                # Because the POST data from request gets put in as a dictionary of lists, and the system only expects
                # a list when an input contains more than 1 elements, we have to convert the input back to strings
                # except for when a list makes sense.
                post_input = dict(request.POST)

                for key, value in post_input.items():
                    if len(value) == 1:
                        post_input[key] = value[0]

                item_satisfied = item.module_item_handlers().handle_input(post_input, item.game.gameID, item.gameItemLinkID, request, None)
            else:
                messages.add_message(request, messages.ERROR,
                                     'Er is een fout opgetreden bij het versturen van een antwoord!')
                messages.add_message(request, messages.DEBUG,
                                     'A problem occurred with fetching the module handlers')
                return redirect('game:gameIndex', gameID=gameID)

            # Handle item status
            if item_satisfied:
                if item.category.chained:
                    return redirect('game:renderItem', gameID=gameID, ID=item.category.categoryID, is_cat="cat")
                else:
                    return redirect('game:gameIndex', gameID=gameID)
            else:
                messages.add_message(request, messages.WARNING, 'Het gegeven antwoord is fout!')
                if item.category.chained:
                    return redirect('game:renderItem', gameID=gameID, ID=item.category.categoryID, is_cat="cat")
                else:
                    return redirect('game:renderItem', gameID=gameID, ID=itemID, is_cat="item")
        else:
            # Problems with ID fetching
            messages.add_message(request, messages.ERROR,
                                 'Er ging iets fout tijdens het afsluiten van een game item!')

            if 'gameID' not in request.POST:
                messages.add_message(request, messages.DEBUG,
                                     '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
            if 'itemID' not in request.POST:
                messages.add_message(request, messages.DEBUG,
                                     '<i>\'itemID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')

            return redirect('game:gameIndex', gameID=gameID)

    elif request.method == 'GET':
        return redirect('game:gameIndex', gameID=gameID)
