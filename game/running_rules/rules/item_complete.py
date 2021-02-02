from django.contrib import messages


def item_is_complete(request, item, game):
    """
    Verify that an item is still accessible and hasn't been completed already.
    """

    if item.gameItemStateCompleted is True:
        messages.add_message(request, messages.INFO,
                             f'{item.gameItemLinkName} is afgesloten!')
        return False
    return True


def item_is_complete_socket(item, game):
    """
    Verify that an item is still accessible and hasn't been completed already.
    """

    if item.gameItemStateCompleted is True:
        return False
    return True