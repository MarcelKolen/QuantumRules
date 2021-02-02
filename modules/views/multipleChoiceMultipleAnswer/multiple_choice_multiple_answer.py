from game.models import GameItemLink
from game.core_control_methods import handle_item_state
from modules.models import MultipleChoiceMultipleAnswerChoices
from modules.base import basic_module_render, fetch_module_object


# !!! Mandatory Method !!!
def render_module(request, gameID, itemID):
    """
    Called by render_item in game/views/main_views.py

    Renders multiple choice multiple answer item
    """

    # Parameters are the request (straight pass through!), the gameID and itemID (straight pass through!),
    # optional content which can be custom defined, the template location and the (verbose) module name.
    return basic_module_render(request, gameID, itemID, {},
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
        # Fetch module object (multiple choice multiple answer in this case) and fetch the
        # gameItemLink object (optional). The result of this fetch is stored as a tuple in fetch_res. The first
        # ([0]) element contains the boolean success result (True or False), the second ([1]) element the module
        # object and the third ([2]) object is the gameItemLink object.
        if not (fetch_res := fetch_module_object(itemID))[0]:
            return False

        # Fetch all required answers and convert user input into given answers objects
        all_required_answers = fetch_res[1].related_choices_content().filter(correct_answer=True)
        all_given_answers = MultipleChoiceMultipleAnswerChoices.objects.filter(ID__in=input['mcAnswer'])

        # All required answers must be given, therefor both querysets need to be equal.
        # Note that the order of elements does not matter in Python sets. (so [3,1,2] == [1,2,3] -> (true)).
        if set(all_given_answers) == set(all_required_answers):
            handle_item_state.item_satisfied(itemID)
            return True
        handle_item_state.item_not_satisfied(itemID)
    return False
