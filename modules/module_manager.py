class ItemTypes:
    TEXT_ITEM = 'TI'
    MULTIPLE_CHOICE = 'MC'
    MULTIPLE_CHOICE_MULTIPLE_ANSWER = 'MA'

    ITEM_TYPE_CHOICES = [
        (TEXT_ITEM, 'Text Item'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (MULTIPLE_CHOICE_MULTIPLE_ANSWER, 'Multiple Choice multiple answer'),
    ]


def item_type_choices_as_dict():
    choices_as_dict = {}
    for choices in ItemTypes.ITEM_TYPE_CHOICES:
        choices_as_dict.update({choices[0]: choices[1]})
    return choices_as_dict


def select_module(item_type, as_model=False, as_admin=False):
    if item_type == ItemTypes.TEXT_ITEM:
        if as_model is True:
            from modules.models import TextItem as module
        else:
            if as_admin is True:
                import modules.views.textItem.text_item_admin as module
            else:
                import modules.views.textItem.text_item as module

    elif item_type == ItemTypes.MULTIPLE_CHOICE:
        if as_model is True:
            from modules.models import MultipleChoice as module
        else:
            if as_admin is True:
                import modules.views.multipleChoice.multiple_choice_admin as module
            else:
                import modules.views.multipleChoice.multiple_choice as module

    elif item_type == ItemTypes.MULTIPLE_CHOICE_MULTIPLE_ANSWER:
        if as_model is True:
            from modules.models import MultipleChoiceMultipleAnswer as module
        else:
            if as_admin is True:
                import modules.views.multipleChoiceMultipleAnswer.multiple_choice_multiple_answer_admin as module
            else:
                import modules.views.multipleChoiceMultipleAnswer.multiple_choice_multiple_answer as module

    else:
        return False, None
    return True, module