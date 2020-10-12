from django.shortcuts import render, redirect
from django.forms import modelformset_factory, formset_factory
from django.contrib import messages

from modules.forms import MultipleChoiceForm, MultipleChoiceChoicesForm
from modules.models import MultipleChoice, MultipleChoiceChoices
from QR2.settings import DEBUG


# !!! Mandatory Method !!!
def render_adding_in_category(request, typeID, gameID, categoryID):
    """
    Render a template which shows both a form to pick an existin item and a form to add a new item
    """
    template_name = 'modules/multipleChoiceModule/admin/add_in_category.html'

    choices_formset = formset_factory(MultipleChoiceChoicesForm, extra=1)

    # Populate form with POST data for errorhandling
    form = MultipleChoiceForm(request.POST or None)
    form_choices = choices_formset(request.POST or None)

    context = {'all_module_items': MultipleChoice.objects.order_by('name'),
               'typeID': typeID,
               'gameID': gameID,
               'categoryID': categoryID,
               'form': form,
               'form_choices': form_choices,
               }

    return render(request, template_name, context)


# !!! Mandatory Method !!!
def render_adding(request, typeID):
    """
    Render a template which shows a form to add a new item
    """
    template_name = 'modules/multipleChoiceModule/admin/add.html'

    choices_formset = formset_factory(MultipleChoiceChoicesForm, extra=1)

    # Populate form with POST data for errorhandling
    form = MultipleChoiceForm(request.POST or None)
    form_choices = choices_formset(request.POST or None)

    context = {
        'typeID': typeID,
        'form': form,
        'form_choices': form_choices,
    }

    return render(request, template_name, context)


# !!! Mandatory Method !!!
def render_edit(request, typeID, itemID):
    """
    Fetch existing item and render a form containing its current data
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    template_name = 'modules/multipleChoiceModule/admin/edit.html'

    try:
        multiplechoice_item = MultipleChoice.objects.get(ID=itemID)
    except MultipleChoice.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Multiple Choice Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')

    choices_formset = modelformset_factory(MultipleChoiceChoices, MultipleChoiceChoicesForm, extra=1, can_delete=True)

    # Populate form with POST data and database instances
    form = MultipleChoiceForm(request.POST or None, instance=multiplechoice_item)
    form_choices = choices_formset(request.POST or None, queryset=MultipleChoiceChoices.objects.filter(related_question=multiplechoice_item))

    context = {
        'name': multiplechoice_item.name,
        'typeID': typeID,
        'itemID': itemID,
        'form': form,
        'form_choices': form_choices,
    }

    return render(request, template_name, context)


# !!! Mandatory Method !!!
def add(request):
    """
    Add new item and return its new ID
    """
    choices_formset = modelformset_factory(MultipleChoiceChoices, MultipleChoiceChoicesForm, extra=1)

    form = MultipleChoiceForm(request.POST)
    form_choices = choices_formset(request.POST)

    if form.is_valid():
        if form_choices.is_valid():
            atleast_one_correct = False

            # Check if at least one of the provided possible answers is flagged as a correct answer
            for choice in form_choices:
                if choice.cleaned_data['correct_answer'] is True:
                    atleast_one_correct = True
                    break

            # If there is at least one valid answer possibility, add the new item
            if atleast_one_correct is True:
                new_item = form.save()
                choice_instance = form_choices.save(commit=False)
                marked_for_delete = form_choices.deleted_forms

                for choice in choice_instance:
                    choice.related_question = new_item
                    choice.save()

                for delete_form in marked_for_delete:
                    delete_object = delete_form.save(commit=False)
                    if delete_object.ID is not None:
                        delete_object.delete()

                return True, new_item

            messages.add_message(request, messages.ERROR, 'Tenminste één antwoord moet een correct antwoord zijn!')
    return False, None


# !!! Mandatory Method !!!
def edit(request, itemID):
    """
    Edit existing item
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    try:
        multiplechoice_item = MultipleChoice.objects.get(ID=itemID)
    except MultipleChoice.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Multiple Choice Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')

    choices_formset = modelformset_factory(MultipleChoiceChoices, MultipleChoiceChoicesForm, can_delete=True)

    form = MultipleChoiceForm(request.POST, instance=multiplechoice_item)
    form_choices = choices_formset(request.POST, queryset=MultipleChoiceChoices.objects.filter(related_question=multiplechoice_item))

    if form.is_valid():
        if form_choices.is_valid():
            atleast_one_correct = False

            # Check if at least one of the provided possible answers is flagged as a correct answer
            for choice in form_choices:
                if choice.cleaned_data['correct_answer'] is True:
                    atleast_one_correct = True
                    break

            # If there is at least one valid answer possibility, add the new item
            if atleast_one_correct is True:
                item = form.save()
                choice_instance = form_choices.save(commit=False)
                marked_for_delete = form_choices.deleted_forms

                for choice in choice_instance:
                    choice.related_question = item
                    choice.save()

                for delete_form in marked_for_delete:
                    delete_object = delete_form.save(commit=False)
                    if delete_object.ID is not None:
                        delete_object.delete()

                return True

            messages.add_message(request, messages.ERROR, 'Tenminste één antwoord moet een correct antwoord zijn!')
    return False


# !!! Mandatory Method !!!
def delete(request, itemID):
    """
    Delete existing item. Deleting an item will cascade to the module item registry and GameItemLinks
    """
    if DEBUG is True:
        messages.set_level(request, messages.DEBUG)

    try:
        multiplechoice_item = MultipleChoice.objects.get(ID=itemID)
    except MultipleChoice.DoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Er is een fout opgetreden aanpassen van een Multiple Choice  Item!')
        messages.add_message(request, messages.DEBUG,
                             f'The exception <i>\'TextItem.DoesNotExist\'</i> occurred on id {itemID}')
        return redirect('game:adminpanelModules')
    multiplechoice_item.delete()
    return True

# !!! Mandatory Method !!!
def reset(linkID):
    """
    Reset is used in case that the module's database is alterable by user input.
    :linkID: Can be used to only reset the components that are linked to a game that is being reset.
    """
    return True
