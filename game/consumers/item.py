import json
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from game.models import GameItemLink, Game
from game.running_rules import post_item_rules_socket


class ItemConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        """
        Gets called when a websocket first connects
        """
        print("Connected", event)

        # Fetch item object and ID from the routing url
        itemID = self.scope['url_route']['kwargs']['itemID']
        item = await self.get_item_object(itemID)

        if item is not None:
            self.item_socket_room = f"item_socket_room_{item.gameItemLinkID}"

            try:
                await self.channel_layer.group_add(
                    self.item_socket_room,
                    self.channel_name
                )

                await self.accept()
            except ConnectionRefusedError:
                print('Error: Layer connection refused')
                print('Disconnected', self.item_socket_room, event)
                await self.close(1011)
                return
        else:
            print('Error: requested item does not exist')
            print('Disconnected', self.item_socket_room, event)
            await self.close(1011)
            return

    async def websocket_receive(self, event):
        """
        Gets called when a websocket send a message to the server
        """
        print("Received", event)

        # Recieve data (text) portion from websocket input
        websocket_input_data = event.get('text', None)

        if websocket_input_data is not None:
            # Convert raw json string to a list of dictionaries
            raw_json_data = json.loads(websocket_input_data)

            event_tag = raw_json_data.get('event', None)
            data_tag = raw_json_data.get('data', None)

            processed_input_data = {}
            if data_tag is not None:
                # Convert list of dictionaries into a single level dictionary
                for item in raw_json_data['data']:
                    dict_item_name = item['name']
                    dict_item_value = item['value']
                    # If a value is passed more than once under the same input name, convert the dictionary entry
                    # from a singular entry into a list of entries
                    if dict_item_name in processed_input_data:
                        multi_val_list = []
                        if isinstance(processed_input_data[dict_item_name], list):
                            for i in processed_input_data[dict_item_name]:
                                multi_val_list.append(i)
                        else:
                            multi_val_list.append(processed_input_data[dict_item_name])
                        multi_val_list.append(dict_item_value)
                        processed_input_data[dict_item_name] = multi_val_list
                    else:
                        processed_input_data[dict_item_name] = dict_item_value

            if event_tag is not None and event_tag == 'post':
                    itemID = processed_input_data.get('itemID', None)
                    gameID = processed_input_data.get('gameID', None)

                    if itemID is not None and gameID is not None:
                        item = await self.get_item_object(itemID)
                        game = await self.get_game_object(gameID)

                        if item is not None and game is not None:
                            if await self.post_item_rules(item, game) is True:
                                if item.module_item_handlers is not False:
                                    # Send socket input to module input handler for processing
                                    if await self.handle_socket_input(item, processed_input_data, None, event) is True:
                                        await self.send_json({
                                            'type': 'websocket.send',
                                            'event': 'input_succes',
                                        })
                                        return
                                    else:
                                        await self.send_json({
                                            'type': 'websocket.send',
                                            'event': 'input_fail',
                                        })
                                        return
                            else:
                                await self.send_json({
                                    'type': 'websocket.send',
                                    'event': 'running_error',
                                })
                        else:
                            await self.send_json({
                                'type': 'websocket.send',
                                'event': 'input_error',
                            })

    async def websocket_disconnect(self, event):
        """
        Gets called when a websocket disconnects
        """
        print("Disconnected", self.item_socket_room, event)

        try:
            await self.channel_layer.group_discard(
                self.item_socket_room,
                self.channel_name
            )
        except ConnectionRefusedError:
            print('Error: Layer connection refused')

        try:
            await self.disconnect(event['code'])
        except ConnectionRefusedError:
            print('Error: No clean disconnect')
        raise StopConsumer()

    async def websocket_send(self, event):
        print("send", event)
        await self.send_json(event)

    @database_sync_to_async
    def get_game_object(self, gameID):
        """
        VERY IMPORTANT NOTE: Always un-async database connections by using @database_sync_to_async in order to
        prevent database overloading with too many async requests.

        Fetch Game object from the database.
        """
        try:
            return Game.objects.get(gameID=gameID)
        except Game.DoesNotExist:
            print('DB Error: Requested Game does not exist')
            return None

    @database_sync_to_async
    def get_item_object(self, itemID):
        """
        VERY IMPORTANT NOTE: Always un-async database connections by using @database_sync_to_async in order to
        prevent database overloading with too many async requests.

        Fetch GameItemLink object from the database.
        """
        try:
            return GameItemLink.objects.get(gameItemLinkID=itemID)
        except GameItemLink.DoesNotExist:
            print('DB Error: Requested GameItemLink does not exist')
            return None

    @sync_to_async
    def handle_socket_input(self, item, processed_input_data, raw_request_data=None, raw_socket_data=None):
        """
        Call input handler from a module and return its result.
        The input handler is a synchronous method and needs to be converted to an async method
        hence the @sync_to_async decorator.
        """
        return item.module_item_handlers().handle_input(processed_input_data, item.game.gameID,
                                                        item.gameItemLinkID, raw_request_data, raw_socket_data)

    @sync_to_async
    def post_item_rules(self, item, game):
        """
        Call item rule handler to see if the item is still valid and accessible.
        The input handler is a synchronous method and needs to be converted to an async method
        hence the @sync_to_async decorator.
        """
        return post_item_rules_socket(item, game)
