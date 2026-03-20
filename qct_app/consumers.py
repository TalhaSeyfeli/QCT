import json
from channels.generic.websocket import AsyncWebsocketConsumer

# ODA İZLEME SÖZLÜĞÜ (RAM üzerinde tutulur)
# Hangi odada anlık olarak kaç kişi olduğunu takip eden global güvenlik değişkenimiz.
ROOM_CONNECTIONS = {}

# YENİ: Başarıyla biten ve tamamen öldürülen linklerin kara listesi
COMPLETED_ROOMS = set()

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL'den oda ID'sini al (Örn: ws://domain.com/ws/room/1234/)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'room_{self.room_name}'

        # Başlangıçta kimsenin bileti onaylı değil
        self.is_approved = False

        # Önce bağlantıyı (Handshake) kabul etmeliyiz ki
        # JavaScript'e 4003 özel kapatma kodunu başarıyla iletebilelim!
        await self.accept()

        # YENİ: LİNK ÖLÜM KONTROLÜ - Bu oda daha önce bitirilmiş mi?
        if self.room_group_name in COMPLETED_ROOMS:
            print(f"💀 ÖLÜ LİNK UYARISI: {self.room_group_name} linki daha önce kullanılmış ve imha edilmiş.")
            # 4004 (Not Found / Expired) koduyla anında reddet!
            await self.close(code=4004)
            return

        # --- 1. KRİTİK GÜVENLİK KONTROLÜ: Odadaki mevcut kişi sayısını kontrol et ---
        current_users = ROOM_CONNECTIONS.get(self.room_group_name, 0)

        if current_users >= 2:
            # ODA DOLU: 3. kişiyi anında reddet! (Man-in-the-Middle engellemesi)
            print(f"🔒 SİBER GÜVENLİK UYARISI: {self.room_group_name} odasına 3. bir cihaz girmeye çalıştı. Erişim reddedildi.")
            # Bağlantıyı kabul etmeden 4003 (Yasaklı) koduyla direkt kapat
            await self.close(code=4003) 
            return

        # --- 2. ODA MÜSAİT: Kişi sayısını artır ---
        ROOM_CONNECTIONS[self.room_group_name] = current_users + 1

        # Cihazı içeri aldık, biletini onaylıyoruz
        self.is_approved = True

        # Cihazı WebSocket grubuna (odaya) ekle
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
    
        print(f"✅ Odaya girildi: {self.room_group_name}. Mevcut kişi sayısı: {ROOM_CONNECTIONS[self.room_group_name]}")

    async def disconnect(self, close_code):
        if getattr(self, 'is_approved', False) and hasattr(self, 'room_group_name') and self.room_group_name in ROOM_CONNECTIONS:
            ROOM_CONNECTIONS[self.room_group_name] -= 1
            print(f"🚪 Odadan çıkıldı: {self.room_group_name}. Kalan kişi: {ROOM_CONNECTIONS[self.room_group_name]}")

            if ROOM_CONNECTIONS[self.room_group_name] <= 0:
                del ROOM_CONNECTIONS[self.room_group_name]
                print(f"🗑️ Oda tamamen boşaldı ve RAM'den silindi: {self.room_group_name}")

        # Cihaz odadan çıkınca veya bağlantı kopunca gruptan sil
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Cihazdan bir WebRTC paketi (offer, answer, ice) geldiğinde tetiklenir
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # YENİ: KAMİKAZE PROTOKOLÜ VEYA NORMAL BİTİŞ!
        if data.get('type') in ['transfer_complete', 'kill_room']:
            # Odayı anında kara listeye al
            COMPLETED_ROOMS.add(self.room_group_name)
            sebep = "BAŞARILI" if data.get('type') == 'transfer_complete' else "BAĞLANTI KOPTU"
            print(f"🔥 LİNK İMHA EDİLDİ ({sebep}): {self.room_group_name} odası kara listeye alındı.")

            # Eğer koptuğu için imha edildiyse, odada kalan DİĞER KİŞİYE "Oda Öldü" sinyali gönder
            if data.get('type') == 'kill_room':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'signaling_message',
                        'message': {'type': 'room_killed'},
                        'sender_channel_name': self.channel_name
                    }
                )
            return # İşlemi burada kes, devam etme

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'signaling_message',
                'message': data,
                'sender_channel_name': self.channel_name
            }
        )

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