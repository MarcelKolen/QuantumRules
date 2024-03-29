from game.models import GameItemLink
from game.core_control_methods import handle_item_state
from modules.models import MultipleChoiceChoices
from modules.base import basic_module_render, fetch_module_object


# !!! Mandatory Method !!!
def render_module(request, gameID, itemID):
    """
    Called by render_item in game/views/main_views.py

    Renders multiple choice item
    """

    # Parameters are the request (straight pass through!), the gameID and itemID (straight pass through!),
    # optional content which can be custom defined, the template location and the (verbose) module name.
    return basic_module_render(request, gameID, itemID, {}, 'modules/multipleChoiceModule/multiple_choice.html',
                               'Multiple Choice')


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

    One answer can be given by the user, this is stored in 'mcAnswer'. There can be multiple correct answers, but only
    one needs correct answer needs to be given.
    """
    if 'mcAnswer' in input:
        # Fetch module object (multiple choice multiple answer in this case) and fetch the
        # gameItemLink object (optional). The result of this fetch is stored as a tuple in fetch_res. The first
        # ([0]) element contains the boolean success result (True or False), the second ([1]) element the module
        # object and the third ([2]) object is the gameItemLink object.
        if not (fetch_res := fetch_module_object(itemID))[0]:
            return False

        # Fetch all possible answers
        all_possible_answers = fetch_res[1].related_choices_content().filter(correct_answer=True)

        # Check to see if the user input (answer ID) is in the set of all the possible answers
        if all_possible_answers.filter(ID=input['mcAnswer']).exists():
            handle_item_state.item_satisfied(itemID)
            return True
        handle_item_state.item_not_satisfied(itemID)
    return False
