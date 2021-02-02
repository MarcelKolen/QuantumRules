from django.shortcuts import render, redirect
from django.contrib import messages

from game.models import GameItemLink, Category


def basic_module_render(request, gameID, itemID, optionalContext, template_name=None, verbose_module_name=None):
    """
    Renders the template of a module, which is provided in template name. It does error handling and it provided debug/
    status feedback to the endusers.
    :param request: Incoming request from the Django Server
    :param gameID: ID of a game object
    :param itemID: ID of a GameItemLink object
    :param optionalContext: Custom context which can be appended to the page context dictionary
    :param template_name: Name of the template to render
    :param verbose_module_name: Name of the module (this is used to convey [error] messages).
    :return:
    """
    if verbose_module_name is None:
        error_message = 'module'
        debug_message = 'a module item'
    else:
        error_message = verbose_module_name
        debug_message = verbose_module_name

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

    # Merge optionalContext from caller into base context.
    context = {'item': item, 'game': game, 'categories': categories, **optionalContext}
    return render(request, template_name, context)
