from django.shortcuts import render

def send_view(request):
    return render(request, 'qct_app/send.html')

def receive_view(request, room_uuid):
    # room_uuid'yi URL'den yakalayıp şablona (template) gönderiyoruz
    context = {'room_uuid': room_uuid}
    return render(request, 'qct_app/receive.html', context)