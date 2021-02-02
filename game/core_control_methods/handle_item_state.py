from django.shortcuts import redirect

from game.models import GameItemLink
from game.core_control_methods.backend_socket_messenger import item_complete, item_wrong, update_item, category_complete, game_complete, item_force_reload

def item_not_satisfied(itemID):
    """
    Called when an input for an item is not satisfactory.
    It adds a wrong answer to the counter and checks whether the item should still be running.
    """
    item = GameItemLink.objects.get(gameItemLinkID=itemID)

    # If a client(s) are lagging behind, send them the reload push message in order to make them reload
    if item.gameItemStateCompleted is True:
        item_force_reload(item.gameItemLinkID)
        return

    item.gameItemStateGivenWrongNInput += 1
    item.save()

    # If the maximum number of attempts is set to 0, players have the opportunity
    # to give as many (wrong) answers as they like.
    # Else, it will check whether the amount of given wrong answers does not exceed the threshold.
    if not item.maxNumAttempts == 0 and item.gameItemStateGivenWrongNInput >= item.maxNumAttempts:
        item.gameItemStateCompleted = True
        item.save()
        item_wrong(item.gameItemLinkID, reload=True)
        return

    item_wrong(item.gameItemLinkID)


def item_satisfied(itemID):
    """
    Called when an input for an item is satisfactory.
    It calculates the right score given when the item is completed and it closes the item by setting
    the gameItemStateCompleted flag to true
    """
    item = GameItemLink.objects.get(gameItemLinkID=itemID)

    # If a client(s) are lagging behind, send them the reload push message in order to make them reload
    if item.gameItemStateCompleted is True:
        item_force_reload(item.gameItemLinkID)
        return

    item.gameItemStateCompleted = True

    # Calculate the obtained score by subtracting the penalties. Note that a given score can never be lower than 0
    if item.faultPenalty * item.gameItemStateGivenWrongNInput < 0:
        item.obtainedScore = 0
    else:
        item.obtainedScore = item.maxScore - item.faultPenalty * item.gameItemStateGivenWrongNInput

    # Keep track of how many correct answers have been given
    item.gameItemStateGivenNInput += 1
    item.save()

    # Update score for the corresponding category
    category = item.category
    category.obtainedCategoryScore += item.obtainedScore
    category.save()

    # Send update triggers to connected sockets
    update_item(item.gameItemLinkID)
    item_complete(item.gameItemLinkID)
    if category.is_completed():
        category_complete(category.categoryID)
    if item.game.is_completed():
        game_complete(item.game.gameID)
