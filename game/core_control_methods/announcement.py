from django.shortcuts import redirect
from django.contrib import messages

from game.forms import AnnouncementForm
from game.core_control_methods.backend_socket_messenger import make_announcement
from QR2.settings import DEBUG


def make_general_announcement(request_data, on_success, on_fail):
    if DEBUG is True:
        messages.set_level(request_data, messages.DEBUG)

    if 'gameID' in request_data.POST:
        gameID = request_data.POST['gameID']
        announcementForm = AnnouncementForm(request_data.POST)

        if announcementForm.is_valid():
            title = announcementForm.cleaned_data['title']
            message = announcementForm.cleaned_data['message']

            if title == "":
                title = "Aankondiging!"

            # Send message from the form to the make_announcement which will distribute the
            # message to all connected sockets.
            make_announcement(gameID, title, message)
        else:
            messages.add_message(request_data, messages.ERROR,
                                 'Er ging iets fout tijdens het versturen van een bericht!')
            return redirect(on_fail, gameID=gameID)

        return redirect(on_success, gameID=gameID)
    else:
        # Problems with ID fetching
        messages.add_message(request_data, messages.ERROR,
                             'Er ging iets fout tijdens het versturen van een bericht!')

        if 'gameID' not in request_data.POST:
            messages.add_message(request_data, messages.DEBUG,
                                 '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
        return redirect('game:adminpanelGames')