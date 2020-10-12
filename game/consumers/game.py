import asyncio
import json
from channels.exceptions import StopConsumer
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from game.models import Game


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        """
        Gets called when a websocket first connects
        """
        print('Connected', event)

        # Fetch game object and ID from the routing url
        gameID = self.scope['url_route']['kwargs']['gameID']
        game = await self.get_game_object(gameID)

        if game is not None:
            self.game_socket_room = f"game_socket_room_{game.gameID}"

            print(self.game_socket_room)

            try:
                await self.channel_layer.group_add(
                    self.game_socket_room,
                    self.channel_name
                )

                await self.accept()
            except ConnectionRefusedError:
                print('Error: Layer connection refused')
                print('Disconnected', self.game_socket_room, event)
                await self.close(1011)
                return
        else:
            print('Error: requested game does not exist')
            print('Disconnected', self.game_socket_room, event)
            await self.close(1011)
            return

    async def websocket_receive(self, event):
        """
        Gets called when a websocket send a message to the server
        """
        print('Received', event)

    async def websocket_disconnect(self, event):
        """
        Gets called when a websocket disconnects
        """
        print('Disconnected', self.game_socket_room, event)

        try:
            await self.channel_layer.group_discard(
                self.game_socket_room,
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
        print('send', event)
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
