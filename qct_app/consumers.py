import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL'den oda ID'sini al (Örn: ws://domain.com/ws/room/1234/)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'room_{self.room_name}'

        # Cihazı WebSocket grubuna (odaya) ekle
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Bağlantıyı kabul et
        await self.accept()

    async def disconnect(self, close_code):
        # Cihaz odadan çıkınca veya bağlantı kopunca gruptan sil
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Cihazdan bir WebRTC paketi (offer, answer, ice) geldiğinde tetiklenir
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Gelen veriyi odadaki HERKESE gönder (kendisi hariç - bunu aşağıda filtreleyeceğiz)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signaling_message',
                'message': data,
                'sender_channel_name': self.channel_name # Mesajı kimin attığını ekliyoruz
            }
        )

    # Gruptan gelen mesajı yakalayıp istemciye (frontend'e) ileten fonksiyon
    async def signaling_message(self, event):
        message = event['message']
        sender = event['sender_channel_name']

        # Kendi gönderdiğimiz WebRTC paketini kendimize geri göndermeyi engelliyoruz
        if self.channel_name != sender:
            await self.send(text_data=json.dumps(message))