from django.contrib import messages


def item_in_game(request, item, game):
    """
    Verify that a given item is actually in the provided game. This is to prevent cross game item fetching.
    """

    if item.game.gameID is not game.gameID:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden bij het openen van een onderdeel!')
        messages.add_message(request, messages.DEBUG,
                             f'The <i>\'GameItemLink\'</i> with id <i>\'{item.gameItemLinkID}\'</i> and game id <i>\'{item.game.gameID}\'</i> is not linked to the provided game with id <i>\'{game.gameID}\'</i>.')
        return False
    return True


def item_in_game_socket(item, game):
    """
    Verify that a given item is actually in the provided game. This is to prevent cross game item fetching.
    """

    if item.game.gameID is not game.gameID:
        return False
    return True
