from django.shortcuts import render, redirect
from django.contrib import messages

from game.models import GameItemLink, Category


def basic_module_render(request, gameID, itemID, template_name=None, render_error=None):
    """
    Renders basic module
    """
    if render_error is None:
        error_message = 'module'
        debug_message = 'a module item'
    else:
        error_message = render_error
        debug_message = render_error

    if template_name is None:
        messages.add_message(request, messages.ERROR,
                             f'Er ging iets fout tijdens het openen van een {error_message} item!')
        messages.add_message(request, messages.DEBUG,
                             f'The <i>\'template_name\'</i> was not set <i>\'(None)\'</i> in the render_module method of {debug_message}')
        return redirect('game:gameIndex', gameID=gameID)

    # Fetch GameItemLink. The GameItemLink will be used to render out all the components on the template.
    try:
        item = GameItemLink.objects.get(gameItemLinkID=itemID)
    except GameItemLink.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             f'Er ging iets fout tijdens het openen van een {error_message} item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'GameItemLink.DoesNotExist\'</i> occurred on id <i>\'{itemID}\'</i> in the render_module method of {debug_message}')
        return redirect('game:gameIndex', gameID=gameID)

    # Game and categories need to be loaded for general components such as the scorebar
    game = item.game

    categories = Category.objects.filter(game=game)

    context = {'item': item, 'game': game, 'categories': categories}
    return render(request, template_name, context)