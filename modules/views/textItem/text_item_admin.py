from django.shortcuts import render, redirect
from django.contrib import messages

from modules.forms import TextItemForm
from modules.models import TextItem
from QR2.settings import DEBUG


# !!! Mandatory Method !!!
def render_adding_in_category(request, typeID, gameID, categoryID):
    """
    Render a template which shows both a form to pick an existin item and a form to add a new item
    """
    template_name = 'modules/textmodule/admin/add_in_category.html'

    # Populate form with POST data for errorhandling
    form = TextItemForm(request.POST or None)

    context = {'all_module_items': TextItem.objects.order_by('name'),
               'typeID': typeID,
               'gameID': gameID,
               'categoryID': categoryID,
               'form': form,
               }

    return render(request, template_name, context)


# !!! Mandatory Method !!!
def render_adding(request, typeID):
    """
    Render a template which shows a form to add a new item
    """
    template_name = 'modules/textmodule/admin/add.html'

    # Populate form with POST data for errorhandling
    form = TextItemForm(request.POST or None)

    context = {
        'typeID': typeID,
        'form': form,
    }

    return render(request, template_name, context)


# !!! Mandatory Method !!!
def render_edit(request, typeID, itemID):
    """
    Fetch existing item and render a form containing its current data
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    template_name = 'modules/textmodule/admin/edit.html'

    try:
        text_item = TextItem.objects.get(ID=itemID)
    except TextItem.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Text Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')

    # Populate form with POST data and database instances
    form = TextItemForm(request.POST or None, instance=text_item)

    context = {
        'name': text_item.name,
        'typeID': typeID,
        'itemID': itemID,
        'form': form,
    }

    return render(request, template_name, context)


# !!! Mandatory Method !!!
def add(request):
    """
    Add new item and return its new ID
    """
    form = TextItemForm(request.POST)

    if form.is_valid():
        new_item = form.save()
        return True, new_item
    return False, None


# !!! Mandatory Method !!!
def edit(request, itemID):
    """
    Edit existing item
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    # Populate form with postdata for formvalidation and saving
    try:
        form = TextItemForm(request.POST, instance=TextItem.objects.get(ID=itemID))
    except TextItem.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Text Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')

    if form.is_valid():
        form.save()
        return True
    return False


# !!! Mandatory Method !!!
def delete(request, itemID):
    """
    Delete existing item. Deleting an item will cascade to the module item registry and GameItemLinks
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    try:
        text_item = TextItem.objects.get(ID=itemID)
    except TextItem.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Text Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')
    text_item.delete()
    return True


# !!! Mandatory Method !!!
def reset(linkID):
    """
    Reset is used in case that the module's database is alterable by user input.
    :linkID: Can be used to only reset the components that are linked to a game that is being reset.
    """
    return True
