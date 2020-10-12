from channels import layers
from asgiref.sync import async_to_sync

from game.models import GameItemLink, Game, Category


def update_item(itemID):
    """
    Update item status (notVisited, visited, completed)
    Send socket message to all clients connected to the same gameID socket_room.
    """

    # Fetch GameItemLink and Game objects
    try:
        item = GameItemLink.objects.get(gameItemLinkID=itemID)
        game = item.game
    except GameItemLink.DoesNotExist:
        print('DB Error: Requested GameItemLink does not exist')
        return False
    except Game.DoesNotExist:
        print('DB Error: Requested Game does not exist')
        return False

    # Construct socket_room tag
    game_socket_room = f"game_socket_room_{game.gameID}"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send item status to all connected sockets
    try:
        # Item is visited and not completed
        if item.gameItemStateVisited and not item.gameItemStateCompleted:
            async_to_sync(channel_layer.group_send)(game_socket_room,
                                                    {'type': 'websocket.send', 'event': 'updateItem', 'itemID': itemID,
                                                     'status': 'visited'})
        # Item has been completed
        elif item.gameItemStateCompleted:
            async_to_sync(channel_layer.group_send)(game_socket_room,
                                                    {'type': 'websocket.send', 'event': 'updateItem', 'itemID': itemID,
                                                     'status': 'completed'})
        # Item is not visited neither completed
        else:
            async_to_sync(channel_layer.group_send)(game_socket_room,
                                                    {'type': 'websocket.send', 'event': 'updateItem', 'itemID': itemID,
                                                     'status': 'notVisited'})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False


def game_complete(gameID):
    """
    Send pushmessage tot all to all connected sockets that the game has ended.
    Send socket message to all clients connected to the same gameID socket_room.
    """

    # Fetch Game object
    try:
        game = Game.objects.get(gameID=gameID)
    except Game.DoesNotExist:
        print('DB Error: Requested Game does not exist')
        return False

    # Construct socket_room tag
    game_socket_room = f"game_socket_room_{game.gameID}"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send game completed status to all connected sockets
    try:
        async_to_sync(channel_layer.group_send)(game_socket_room,
                                                {'type': 'websocket.send', 'event': 'gameComplete',
                                                 'obtainedScore': game.obtained_score(), 'maxScore': game.max_score()})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False


def category_complete(categoryID):
    """
    Send status of a completed category to all connected clients.
    Send socket message to all clients connected to the same gameID socket_room.
    """

    # Fetch Category and Game objects
    try:
        category = Category.objects.get(categoryID=categoryID)
        gameID = category.game.gameID
    except Category.DoesNotExist:
        print('DB Error: Requested Category does not exist')
        return False
    except Game.DoesNotExist:
        print('DB Error: Requested Game does not exist')
        return False

    # Construct socket_room tag
    game_socket_room = f"game_socket_room_{gameID}"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send category completed status to all connected sockets
    try:
        async_to_sync(channel_layer.group_send)(game_socket_room,
                                                {'type': 'websocket.send', 'event': 'categoryComplete',
                                                 'categoryID': categoryID})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False


def make_announcement(gameID, title, body):
    """
    Send a pushmessage to all connected clients containing a given title and body element
    Send socket message to all clients connected to the same gameID socket_room.
    """

    # Construct socket_room tag
    game_socket_room = f"game_socket_room_{gameID}"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send pushmessage to all connected sockets
    try:
        async_to_sync(channel_layer.group_send)(game_socket_room,
                                                {'type': 'websocket.send', 'event': 'generalAnnouncement',
                                                 'generalAnnouncementTitle': title, 'generalAnnouncementBody': body})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False


def item_complete(itemID):
    """
    Send a pushmessage to all connected clients stating that the item has been completed.
    Send socket message to all clients connected to the same itemID socket_room.
    """

    # Construct socket_room tag
    item_socket_room = f"item_socket_room_{itemID}"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send pushmessage to all connected sockets
    try:
        async_to_sync(channel_layer.group_send)(item_socket_room,
                                                {'type': 'websocket.send', 'event': 'itemComplete'})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False

    # Update score for all connected clients
    return update_score(itemID)


def item_complete_by_GM(itemID, score, max_score):
    """
    Send a pushmessage to all connected clients stating that the item has been completed by the gamemaster.
    Send socket message to all clients connected to the same itemID socket_room.
    """

    # Construct socket_room tag
    item_socket_room = f"item_socket_room_{itemID}"

    # Construct score percentage for inside the message
    score_percentage = round((score / max_score) * 100, 0)
    score = f"{score_percentage}%"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send pushmessage to all connected sockets
    try:
        async_to_sync(channel_layer.group_send)(item_socket_room,
                                                {'type': 'websocket.send', 'event': 'itemCompleteByGM', 'score': score})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False

    # Update score for all connected clients
    return update_score(itemID)


def update_score(itemID):
    """
    Send a new score to all connected clients to dynamically update the scorebar.
    Send socket message to all clients connected to the same gameID socket_room.
    """

    # Fetch GameItemLink, Category and Game objects
    try:
        item = GameItemLink.objects.get(gameItemLinkID=itemID)
        category = item.category
        game = item.game
    except GameItemLink.DoesNotExist:
        print('DB Error: Requested GameItemLink does not exist')
        return False
    except Category.DoesNotExist:
        print('DB Error: Requested Category does not exist')
        return False
    except Game.DoesNotExist:
        print('DB Error: Requested Game does not exist')
        return False

    if category.maxCategoryScore > 0:
        # Fetch new score data
        new_category_score = category.obtainedCategoryScore
        max_category_score = category.maxCategoryScore

        # Construct socket_room tag
        game_socket_room = f"game_socket_room_{game.gameID}"

        # Fetch the channel_layers used for group socket messaging
        channel_layer = layers.get_channel_layer()

        # Send new score data to all connected sockets
        try:
            async_to_sync(channel_layer.group_send)(game_socket_room,
                                                    {
                                                        'type': 'websocket.send',
                                                        'event': 'scoreUpdate',
                                                        'category': f'{category.categoryID}',
                                                        'currentScore': f'{new_category_score}',
                                                        'maxScore': f'{max_category_score}'
                                                    })
        except ConnectionRefusedError:
            print('Error: Layer connection refused')
            return False


def item_force_reload(itemID):
    """
    Forcefully reload connected clients.
    Send socket message to all clients connected to the same itemID socket_room.
    """

    # Construct socket_room tag
    item_socket_room = f"item_socket_room_{itemID}"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send pushmessage to all connected sockets
    try:
        async_to_sync(channel_layer.group_send)(item_socket_room,
                                                {'type': 'websocket.send', 'event': 'force_reload'})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False


def item_wrong(itemID, reload=False):
    """
    Send a pushmessage to all connected clients stating that the item has been answered incorrectly.
    If the number of chances have been exhausted, the user should be redirected back to the main page (reload=True)
    Send socket message to all clients connected to the same itemID socket_room.
    """

    # Construct socket_room tag
    item_socket_room = f"item_socket_room_{itemID}"

    # Fetch the channel_layers used for group socket messaging
    channel_layer = layers.get_channel_layer()

    # Send pushmessage to all connected sockets
    try:
        async_to_sync(channel_layer.group_send)(item_socket_room,
                                                {'type': 'websocket.send', 'event': 'wrong', 'reload': str(reload)})
    except ConnectionRefusedError:
        print('Error: Layer connection refused')
        return False

    # If reload is false, so if users should stay on the same page, send a hint if there is one.
    if reload is False:
        send_hint(itemID)


def send_hint(itemID):
    """
    Send hint content data to all connected clients only if an item has hints and if the item is eligible for a hint
    Send socket message to all clients connected to the same itemID socket_room.
    """

    # Fetch a GameItemLink object
    try:
        item = GameItemLink.objects.get(gameItemLinkID=itemID)
    except GameItemLink.DoesNotExist:
        print('DB Error: Requested GameItemLink does not exist')
        return False

    # Only send a hint if there has been at least one (or more) wrong answers given.
    if item.gameItemStateGivenWrongNInput > 0:
        # Fetch module content. Returns False in case of an error
        module = item.module_item_content()

        # Only send hint if given module has a hint
        if module is not False and module.has_hint is True:
            # Construct socket_room tag
            item_socket_room = f"item_socket_room_{itemID}"

            # Fetch the channel_layers used for group socket messaging
            channel_layer = layers.get_channel_layer()

            # Send hint to all connected sockets
            try:
                async_to_sync(channel_layer.group_send)(item_socket_room,
                                                        {
                                                            'type': 'websocket.send',
                                                            'event': 'hint',
                                                            'hint_data': f'{module.hint_content}'
                                                        })
            except ConnectionRefusedError:
                print('Error: Layer connection refused')
                return False
