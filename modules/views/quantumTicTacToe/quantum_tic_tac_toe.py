from game.core_control_methods import handle_item_state
from modules.base import basic_module_render


# !!! Mandatory Method !!!
def render_module(request, gameID, itemID):
    """
    Called by render_item in game/views/main_views.py

    Renders Quantum Tic Tac Toe item
    """

    return basic_module_render(request, gameID, itemID,
                               'modules/quantumTicTacToeModule/quantum_tic_tac_toe_module.html',
                               'Quantum Tic Tac Toe')

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

    Text items do not have any user input other than pressing a button to go to the next part, so the item will always be satisfied.
    """
    handle_item_state.item_satisfied(itemID)
    return True
