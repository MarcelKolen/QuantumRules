from game.models import GameItemLink


def fetch_module_object(itemID):
    """
    Fetches the related module item object from the model/database of the related module.
    It does this by using the GameItemLink object fetched from the itemID parameter. This GameItemLink
    contains the correct related object.

    If the item does not exist, it will return false

    If the item does exist, it will return true and it returns the Module object and the GameItemLink object.
    """
    try:
        item = GameItemLink.objects.get(gameItemLinkID=itemID)
    except GameItemLink.DoesNotExist:
        return False, None, None

    return True, item.module_item_content(), item
