from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def adminpanel(request):
    template_name = 'game/gameAdminpanel/index.html'

    return render(request, template_name)
