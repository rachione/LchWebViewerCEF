import json
from transfer.server import Server as TransferServer
from clientCore import Client


ServerConfig = 'config/server.json'


if __name__ == '__main__':

    transferServer = TransferServer(ServerConfig)
    client = Client(transferServer)
    client.start()
    client.update()
