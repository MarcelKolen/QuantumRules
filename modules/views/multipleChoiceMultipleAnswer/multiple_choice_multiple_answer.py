from game.models import GameItemLink
from game.core_control_methods import handle_item_state
from modules.models import MultipleChoiceMultipleAnswerChoices
from modules.base import basic_module_render


# !!! Mandatory Method !!!
def render_module(request, gameID, itemID):
    """
    Called by render_item in game/views/main_views.py

    Renders multiple choice multiple answer item
    """

    return basic_module_render(request, gameID, itemID,
                               'modules/multipleChoiceMultipleAnswerModule/multiple_choice_multiple_answer.html',
                               'Mutliple Choice Multiple Answer')

# !!! Mandatory Method !!!
def handle_input(input, gameID, itemID, raw_request_data=None, raw_socket_data=None):
    """
    Called by module_item_post in game/views/main_views.py for HTTP requests
    OR
    Called by handle_socket_input in game/consumers/item.py for WS messages

    :input: is a processed dictionary of all the datafields in a postform. HTTP and WS inputs will be the
    same and can be treated the exact same way!
    :raw_request_data: is the raw request input from a HTTP request (not just the POST data, all the data). This can be
    used if :input: is not sufficient. Not recommended!
    :raw_socket_data: is the raw event input from a WS message (not just the formdata data, all the data). This can be
    used if :input: is not sufficient. Not recommended! Note that this input is probably stringified and it needs to
    be parsed/processed beforehand!

    Multiple answers can be given by the user, these are stored in 'mcAnswer'. All possible correct answers need to
    be selected (so get all correct out of all instead of one out of all).
    """
    if 'mcAnswer' in input:
        # Fetch item
        try:
            item = GameItemLink.objects.get(gameItemLinkID=itemID)
        except GameItemLink.DoesNotExist:
            return False

        # Fetch user input
        all_given_answers_input = input['mcAnswer']

        # Fetch all required answers and convert user input into given answers objects
        all_required_answers = MultipleChoiceMultipleAnswerChoices.objects.filter(
            related_question=item.module_item_content(), correct_answer=True)
        all_given_answers = MultipleChoiceMultipleAnswerChoices.objects.filter(ID__in=all_given_answers_input)

        # All required answers must be given, therefor both querysets need to be equal
        if list(all_given_answers) == list(all_required_answers):
            handle_item_state.item_satisfied(itemID)
            return True
        handle_item_state.item_not_satisfied(itemID)
    return False
