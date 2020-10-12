from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from game.models import Category, GameItemLink
from game.forms import Prime_Add_Item_Form
from game.core_control_methods.in_group import in_group_on_class
from modules.models import AllModuleItems
from modules.module_manager import *
from QR2.settings import DEBUG


class AllItems(LoginRequiredMixin, View):
    """
    Get all module items of all types
    """
    template_name = "game/gameAdminpanel/all_items.html"

    @in_group_on_class(groups=['gameCreator'])
    def get(self, request):
        all_module_items = AllModuleItems.objects.all().order_by('type')

        all_choices = item_type_choices_as_dict()

        all_types = {}

        # Fetch only all the type of existing items. Module types which do not have any items yet will not be picked up!
        for item in all_module_items:
            if item.type not in all_types and item.type in all_choices:
                all_types.update({item.type: all_choices[item.type]})

        context = {
            'all_module_types': all_types,
            'all_module_items': all_module_items,
            'prime_item_form': Prime_Add_Item_Form()
        }

        return render(request, self.template_name, context)


class Items:
    class AddExistingItemToCategory(LoginRequiredMixin, View):
        """
        Add an existing module item to a game by constructing a GameItemLink
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'gameID' in request.POST and 'categoryID' in request.POST and 'typeID' in request.POST and 'itemID' in request.POST:
                # Fetch module of given type and with given ID
                try:
                    module = AllModuleItems.objects.get(fkID=request.POST['itemID'], type=request.POST['typeID'])
                except AllModuleItems.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het toevoegen van een item aan een categorie.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'AllModuleItems.DoesNotExist\'</i> occurred on id <i>\'{request.POST["itemID"]}\'</i>')
                    return redirect('game:adminpanelGames')

                # Create new GameItemLink to link a module to a game
                item = GameItemLink(gameItemLinkName=module.module_item_content().name)

                item.module = module

                try:
                    item.category = Category.objects.get(categoryID=request.POST['categoryID'])
                except Category.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het toevoegen van een item aan een categorie.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Category.DoesNotExist\'</i> occurred on id <i>\'{request.POST["categoryID"]}\'</i>')
                    return redirect('game:adminpanelGames')

                item.game = item.category.game

                item.save()

                messages.add_message(request, messages.SUCCESS,
                                     f'Item <i>\'{item.gameItemLinkName}\'</i> is succesvol toegevoegd!')
                return redirect('game:adminpanelGamesEditCategory', gameID=request.POST['gameID'],
                                categoryID=request.POST['categoryID'])
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het afsluiten van een game item!')

                if 'gameID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                if 'categoryID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'categoryID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                if 'typeID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'typeID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                if 'itemID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'itemID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelGames')

    class AddInCategoryUrlScrubber(LoginRequiredMixin, View):
        """
        Convert url generated from formdata into a valid redirect
        """

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'item_type' in request.GET and 'categoryID' in request.GET and 'gameID' in request.GET:
                return redirect('game:adminpanelCategoriesAddItem', typeID=request.GET['item_type'],
                                categoryID=request.GET['categoryID'], gameID=request.GET['gameID'])
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een game item!')

                if 'gameID' not in request.GET:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'gameID\'</i> is not in <i>\'request.GET\'</i>. Check your constructed form and post method.')
                if 'categoryID' not in request.GET:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'categoryID\'</i> is not in <i>\'request.GET\'</i>. Check your constructed form and post method.')
                if 'item_type' not in request.GET:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'typeID\'</i> is not in <i>\'request.GET\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelGames')

    class AddInCategory(LoginRequiredMixin, View):
        """
        Add new item in a category.
        All the existing items will be rendered and a new item form depending on the type will be rendered
        """

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request, typeID, categoryID, gameID):
            """
            Construct rendered page with the use of a module handler
            """

            # Fetch module
            handler = select_module(typeID, False, True)

            # Check if handler is valid
            if handler[0] is False:
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een game item!')
                return redirect('game:adminpanelGamesEdit', gameID=gameID)  # Error

            # Use handlers to related to module types to render the adding form
            return handler[1].render_adding_in_category(request, typeID, gameID, categoryID)

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request, typeID, categoryID, gameID):
            """
            Add a new module item of a given type. Add the new item to a register of all items as well.
            When item has been constructed, add a new GameItemLink to the category containing the correct (new) item.
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'typeID' in request.POST and 'gameID' in request.POST and 'categoryID' in request.POST:
                # Fetch module
                handler = select_module(request.POST['typeID'], False, True)

                # Check if handler is valid
                if handler[0] is False:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het toevoegen van een game item!')
                    return redirect('game:adminpanelGamesEditCategory', gameID=request.POST['gameID'],
                                    categoryID=request.POST['categoryID'])

                # Try to add a new item
                module_item = handler[1].add(request)

                if module_item[0] is False:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het toevoegen van een game item!')
                    self.get(request, typeID, categoryID, gameID)

                # Add new module item to register for all items
                module = AllModuleItems(type=request.POST['typeID'], fkID=module_item[1].ID)
                module.save()

                # Add new GameItemLink, link the new module item to it and link to a category.
                item = GameItemLink(gameItemLinkName=module.module_item_content().name)

                item.module = module

                try:
                    item.category = Category.objects.get(categoryID=request.POST['categoryID'])
                except Category.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het toevoegen van een game item!')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Category.DoesNotExist\'</i> occurred on id <i>\'{request.POST["categoryID"]}\'</i>')
                    return redirect('game:adminpanelCategoriesAddItem', typeID=request.POST['typeID'],
                                    categoryID=request.POST['categoryID'], gameID=request.POST['gameID'])

                item.game = item.category.game

                item.save()

                messages.add_message(request, messages.SUCCESS,
                                     f'Item <i>\'{item.gameItemLinkName}\'</i> is succesvol toegevoegd!')

                return redirect('game:adminpanelGamesEditCategory', gameID=request.POST['gameID'],
                                categoryID=request.POST['categoryID'])

            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een game item!')

                if 'gameID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                if 'categoryID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'categoryID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                if 'typeID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'typeID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelGames')

    class EditItem(LoginRequiredMixin, View):
        """
        Edit an existing module item
        """

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request, itemID):
            """
            Construct rendered page with the use of a module handler
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            # Fetch module
            try:
                item = AllModuleItems.objects.get(id=itemID)
            except AllModuleItems.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het aanpassen van een module item!')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'AllModuleItems.DoesNotExist\'</i> occurred on id <i>\'{itemID}\'</i>')
                return redirect('game:adminpanelCategoriesAddItem', typeID=request.POST['typeID'],
                                categoryID=request.POST['categoryID'], gameID=request.POST['gameID'])

            # Fetch module handlers
            handler = item.module_item_handlers(admin=True)

            if handler is False:
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het aanpassen van een module item!')
                return redirect('game:adminpanelModules')  # Error

            return handler.render_edit(request, item.type, item.fkID)

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request, itemID):
            """
            Edit a module item of a certain type given by the module items register.
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'itemID' in request.POST:
                # Fetch module
                try:
                    item = AllModuleItems.objects.get(id=itemID)
                except AllModuleItems.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het aanpassen van een module item!')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'AllModuleItems.DoesNotExist\'</i> occurred on id <i>\'{itemID}\'</i>')
                    return redirect('game:adminpanelCategoriesAddItem', typeID=request.POST['typeID'],
                                    categoryID=request.POST['categoryID'], gameID=request.POST['gameID'])

                handler = item.module_item_handlers(admin=True)

                if handler is False:
                    return redirect('game:adminpanelModules')

                # Module item could not be edited (e.g. form validation error)
                if handler.edit(request, item.fkID) is False:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het aanpassen van een module item!')
                    return self.get(request, item.id)

                messages.add_message(request, messages.SUCCESS, 'Item is succesvol aangepast!')

                return redirect('game:adminpanelModules')

            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een game item!')

                if 'itemID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'itemID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')

                return redirect('game:adminpanelModules')  # Error

    class AddUrlScrubber(LoginRequiredMixin, View):
        """
        Convert url generated from formdata into a valid redirect
        """

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'item_type' in request.GET:
                return redirect('game:adminpanelModulesAddItem', typeID=request.GET['item_type'])
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een module item!')

                if 'item_type' not in request.GET:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'item_type\'</i> is not in <i>\'request.GET\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelModules')

    class AddItem(LoginRequiredMixin, View):
        """
        Add new module item.
        """

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request, typeID):
            """
            Construct rendered page with the use of a module handler
            """

            # Fetch module handler
            handler = select_module(typeID, False, True)

            if handler is False:
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een module item!')
                return redirect('game:adminpanelModules')  # Error

            return handler[1].render_adding(request, typeID)

        def post(self, request, typeID):
            """
            Add new module item and add new item to the module items registry
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'typeID' in request.POST:

                # Fetch module handler
                handler = select_module(typeID, False, True)

                if handler is False:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het toevoegen van een module item!')
                    return redirect('game:adminpanelModules')  # Error

                # Pass input to module add method and create new item
                module_item = handler[1].add(request)

                if module_item[0] is False:
                    messages.add_message(request, messages.ERROR,
                                         'Er ging iets fout tijdens het toevoegen van een module item!')
                    return self.get(request, typeID)

                # Add new item to the module items registry
                AllModuleItems(type=request.POST['typeID'], fkID=module_item[1].ID).save()

                messages.add_message(request, messages.SUCCESS, 'Nieuw item is succesvol toegevoegd!')

                return redirect('game:adminpanelModules')

            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een module item!')

                if 'typeID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'typeID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelModules')

    class DeleteItem(LoginRequiredMixin, View):
        """
        Delete a module item and remove registry entry
        """

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request, itemID):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            try:
                item = AllModuleItems.objects.get(id=itemID)
            except AllModuleItems.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het verwijderen van een module item!')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'AllModuleItems.DoesNotExist\'</i> occurred on id <i>\'{itemID}\'</i>')
                return redirect('game:adminpanelModules')

            # A module may only be remove if it is not used in any active (published) games!
            delete_is_safe = True

            all_related_game_item_links = GameItemLink.objects.filter(module=item)

            all_related_published_games = []

            # Go through all found link items to see if they are related to published game
            for link in all_related_game_item_links:
                if link.game.published is True:
                    all_related_published_games.append(link.game)
                    delete_is_safe = False

            if delete_is_safe is False:
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het verwijderen van een module item!')
                error_message = 'Een module item kan niet worden verwijderd zolang <strong>gepubliceerde</strong> spellen de module gebruiken.<br>' \
                                'De-publiceer de volgende spellen voordat deze module item verwijderd kan worden:<br>' \
                                '<ul>'
                for game in all_related_published_games:
                    error_message += f'<li><i>\'{game.gameName}\'</i> met id <i>\'{game.gameID}\'</i></li>'
                error_message += '</ul>'
                messages.add_message(request, messages.INFO, error_message)
                return redirect('game:adminpanelModules')  # Error

            # Fetch handler
            handler = item.module_item_handlers(admin=True)

            if handler is False:
                return redirect('game:adminpanelModules')  # Error

            # Module could not be deleted
            if handler.delete(request, item.fkID) is False:
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het verwijderen van een module item!')
                return redirect('game:adminpanelModules')  # Error

            if all_related_game_item_links.count() > 0:
                warning_message = 'Een aantal links uit games zijn verwijderd. Deze zijn verwijderd omdat ze verbonden waren met de verwijderde module item.<br>' \
                                  'Verwijderde links:<br>' \
                                  '<ul>'
                for link in all_related_game_item_links:
                    warning_message += f'<li>Link met ID <i>\'{link.gameItemLinkID}\'</i> is verwijderd uit het spel <i>\'{link.game.gameName}\'</i> in de categorie <i>\'{link.category.categoryName}\'</i></li>'
                warning_message += '</ul>'
                messages.add_message(request, messages.WARNING, warning_message)

            # Delete registry entry. Related GameItemLink objects will be cascaded!
            item.delete()

            messages.add_message(request, messages.SUCCESS, 'Item is succesvol verwijderd!')

            return redirect('game:adminpanelModules')
