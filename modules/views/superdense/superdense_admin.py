from django.shortcuts import render, redirect
from django.contrib import messages

from modules.forms import SuperDenseForm
from modules.models import SuperDense
from QR2.settings import DEBUG


# !!! Mandatory Method !!!
def render_adding_in_category(request, typeID, gameID, categoryID):
    """
    Render a template which shows both a form to pick an existin item and a form to add a new item
    """
    template_name = 'modules/superdenseModule/admin/add_in_category.html'

    # Populate form with POST data for errorhandling
    form = SuperDenseForm(request.POST or None)

    context = {'all_module_items': SuperDense.objects.order_by('name'),
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
    template_name = 'modules/superdenseModule/admin/add.html'

    # Populate form with POST data for errorhandling
    form = SuperDenseForm(request.POST or None)

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

    template_name = 'modules/superdenseModule/admin/edit.html'

    try:
       superdense_item = SuperDense.objects.get(ID=itemID)
    except SuperDense.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Super Dense Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')

    # Populate form with POST data and database instances
    form = SuperDenseForm(request.POST or None, instance=superdense_item)

    context = {
        'name': superdense_item.name,
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

    form = SuperDenseForm(request.POST)

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
        form = SuperDenseForm(request.POST, instance=SuperDense.objects.get(ID=itemID))
    except SuperDense.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Superdense Item!')
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
        superdense_item = SuperDense.objects.get(ID=itemID)
    except SuperDense.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Superdense Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')
    superdense_item.delete()
    return True

# !!! Mandatory Method !!!
def reset(linkID):
    """
    Reset is used in case that the module's database is alterable by user input.
    :linkID: Can be used to only reset the components that are linked to a game that is being reset.
    """
    return True
