from channels.generic.websocket import WebsocketConsumer
import json

map = {}

class CherryConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        id = self.scope["client"][0] + ":" + str(self.scope["client"][1])
        map[id] = {}

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        #print(text_data)
        text_data_json = json.loads(text_data)

        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
        print(self.scope["client"])

    def receive(self, bytes_data):
        print(bytes_data)
        filename = self.scope["client"][0] + ":" + str(self.scope["client"][1]) + ":" + "file.txt"
        with open(filename,'wb') as file:
            file.write(bytes_data)

