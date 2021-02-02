from django.shortcuts import redirect
from django.contrib import messages

from QR2.settings import DEBUG

from .rules import item_is_complete, item_is_complete_socket
from .rules import item_in_game, item_in_game_socket


def render_item_rules(request, item, game):
    """
    Applies rules to an item with a request to be rendered.
    If all the rules are passed, the function will return true and it will not indicate a redirect.
    If one of the rules fail, the function will return false and a redirect.
    Note: This function must always return either True or False and a secondary value either None or
    a redirect respectively!
    """

    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    # If an item has already been completed the user will be redirected back to the game "homepage"
    if item_is_complete(request, item, game) is False:
        return False, redirect('game:gameIndex', gameID=game.gameID)

    # A check to ensure that the requested link is in the given game
    if item_in_game(request, item, game) is False:
        return False, redirect('game:gameIndex', gameID=game.gameID)

    # All rules have been passed
    return True, None


def post_item_rules(request, item, game):
    """
    Applies rules to an item with a request to be posted.
    If all the rules are passed, the function will return true.
    If one of the rules fail, the function will return false.
    """

    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    # If an item has already been completed the user will be redirected back to the game "homepage"
    if item_is_complete(request, item, game) is False:
        return False

    # A check to ensure that the requested link is in the given game
    if item_in_game(request, item, game) is False:
        return False

    # All rules have been passed
    return True


def post_item_rules_socket(item, game):
    """
    Applies rules to an item with a socket request to be posted.
    If all the rules are passed, the function will return true.
    If one of the rules fail, the function will return false.
    """

    # If an item has already been completed the user will be redirected back to the game "homepage"
    if item_is_complete_socket(item, game) is False:
        return False

    # A check to ensure that the requested link is in the given game
    if item_in_game_socket(item, game) is False:
        return False

    # All rules have been passed
    return True