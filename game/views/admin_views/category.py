from django.shortcuts import render, redirect
from django.views import View
from django.forms import modelformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from game.models import Category, Game, GameItemLink
from game.forms import CatergoryFormEdit, GameItemLinkFormEdit, Prime_Add_Item_Form
from game.core_control_methods.in_group import in_group_on_class
from QR2.settings import DEBUG


class Categories:
    def order_items(categoryID):
        """
        Order Items according to their chain order
        """
        try:
            category = Category.objects.get(categoryID=categoryID)
        except Category.DoesNotExist:
            return False

        counter = 0

        # Order items by the set item order, this ensures correct linking
        try:
            items = GameItemLink.objects.filter(category=category).order_by('itemOrder')
        except GameItemLink.DoesNotExist:
            return False

        # Set category first item used for linked item traversal
        category.firstItem = items.first()
        category.save()

        # Passed item orders is used to check whether there are duplicate orders which is not allowed.
        passedItemOrders = [items.first().itemOrder]

        # Past item is used to set the next item of the previous item which is used for linked item traversal
        pastItem = items.first()
        pastItem.itemOrder = counter
        pastItem.save()

        # 'pop' first item as it has been dealt with
        items = items.exclude(gameItemLinkID=items.first().gameItemLinkID)

        counter += 1

        # Go through list of ordered items to construct the linked traversal
        for item in items:
            if item.itemOrder in passedItemOrders:
                return False

            pastItem.nextItem = item
            pastItem.save()
            pastItem = item

            passedItemOrders.append(item.itemOrder)
            item.itemOrder = counter
            item.save()

            counter += 1

        return True

    class Edit(LoginRequiredMixin, View):
        """
        Edit categories and the items corresponding to a given category
        """
        template_name = 'game/gameAdminpanel/category_edit.html'

        @in_group_on_class(groups=['gameCreator'])
        def get(self, request, gameID, categoryID):
            """
            Render category and items with corresponding forms.
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            try:
                game = Game.objects.get(gameID=gameID)
                category = Category.objects.get(game=game, categoryID=categoryID)
                gameItems = GameItemLink.objects.filter(game=game, category=category)
            except Game.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er is een fout opgetreden bij het openen van de categorie pagina. Controleer of het spel nog bestaat.')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{gameID}\'</i>')
                return redirect('game:adminpanelGames')
            except Category.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er is een fout opgetreden bij het openen van de categorie pagina. Controleer of de categorie nog bestaat.')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'Category.DoesNotExist\'</i> occurred on id <i>\'{categoryID}\'</i>')
                return redirect('game:adminpanelGamesEdit', gameID=gameID)
            except GameItemLink.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Er is een fout opgetreden bij het openen van de categorie pagina. Controleer of de categorie nog bestaat.')
                messages.add_message(request, messages.DEBUG,
                                     f'The exception <i>\'GameItemLink.DoesNotExist\'</i> occurred on gameID <i>\'{gameID}\'</i> and categoryID <i>\'{categoryID}\'</i>')
                return redirect('game:adminpanelGamesEdit', gameID=gameID)

            categoryForm = CatergoryFormEdit(instance=category)

            # Generate a formset of game item forms. This formset is a collection (set) of multiple forms and can be
            # ingested as such. (Formsets are quite tricky to work with,
            # so be sure to read Django documentation on this!)
            # Note: The individual forms can only be deleted (and therefor the corresponding game item as well) when a
            # game is not published hence the can_delete=not game.published.
            currentItemsFormset = modelformset_factory(GameItemLink, GameItemLinkFormEdit, extra=0,
                                                       can_delete=not game.published)

            # Populate formset with all.
            currentItemsForm = currentItemsFormset(
                queryset=gameItems.order_by('itemOrder'))

            # Prime item form is a form that 'primes' the creation of a new item.
            prime_item_form = Prime_Add_Item_Form()

            for item_form in currentItemsForm:
                item_form.setItemOrderMax(gameItems.count())

            if game.published is True:
                messages.add_message(request, messages.INFO,
                                     'Je moet het spel eerst <i>de-publiceren</i> voordat je aanpassingen kunt maken.')

                categoryForm.disableFields()
                prime_item_form.disableFields()

                for item_form in currentItemsForm:
                    item_form.disableFields()

            if category.chained is False:
                for item_form in currentItemsForm:
                    item_form.disableItemOrder()

            context = {'game': game, 'category': category, 'categoryForm': categoryForm,
                       'currentItemsForm': currentItemsForm,
                       'gameItems': gameItems, 'prime_item_form': prime_item_form}

            return render(request, self.template_name, context)

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request, gameID, categoryID):
            """
            Update the category and gameitems using the form
            """

            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'gameID' in request.POST and 'categoryID' in request.POST:
                try:
                    game = Game.objects.get(gameID=request.POST['gameID'])
                    category = Category.objects.get(categoryID=request.POST['categoryID'])
                except Game.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er is een fout opgetreden bij het aanpassen van de gegeven categorie. Controleer of het spel nog bestaat.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{request.POST["gameID"]}\'</i>')
                    return redirect('game:adminpanelGames')
                except Category.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er is een fout opgetreden bij het aanpassen van de gegeven categorie. Controleer of de categorie nog bestaat.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Category.DoesNotExist\'</i> occurred on id <i>\'{request.POST["categoryID"]}\'</i>')
                    return redirect('game:adminpanelGamesEdit', gameID=request.POST["gameID"])

                if game.published is True:
                    messages.add_message(request, messages.INFO,
                                         'De-publiceer het spel eerst voordat je aanpassingen maakt.')
                    return self.get(request, request.POST['gameID'], request.POST['categoryID'])

                try:
                    gameItems = GameItemLink.objects.filter(game=game, category=category)
                except GameItemLink.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er is een fout opgetreden bij het aanpassen van de gegeven categorie. Controleer of de items nog bestaat.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'GameItemLink.DoesNotExist\'</i> occurred on gameID <i>\'{request.POST["gameID"]}\'</i> and categoryID <i>\'{request.POST["categoryID"]}\'</i>')
                    return redirect('game:adminpanelGamesEdit', gameID=request.POST["gameID"])

                # Generate a formset of game item forms.
                currentItemsFormset = modelformset_factory(GameItemLink, GameItemLinkFormEdit, can_delete=True)

                # Populate form with post data
                currentItemsForm = currentItemsFormset(request.POST, queryset=gameItems)

                # Populate form with post data
                categoryForm = CatergoryFormEdit(request.POST, instance=category)

                all_items_in_cat = GameItemLink.objects.filter(category=category)
                if all_items_in_cat.exists():
                    if categoryForm.is_valid() and currentItemsForm.is_valid():
                        categoryForm.save()
                        currentItemsForm.save()
                    else:
                        for item_form in currentItemsForm:
                            item_form.setItemOrderMax(gameItems.count())

                        messages.add_message(request, messages.ERROR, 'Er is iets fout in de ingevulde velden!')
                        return self.get(request, gameID, categoryID)
                else:
                    if categoryForm.is_valid():
                        categoryForm.save()
                    else:
                        messages.add_message(request, messages.ERROR, 'Er is iets fout in de ingevulde velden!')
                        return self.get(request, gameID, categoryID)

                # Order Items according to their chain order and check for anomalies
                if category.chained is True:
                    if not Categories.order_items(category.categoryID):
                        # If there is a problem in the ordering of items, remove all the links and set the order to 0
                        category.firstItem = None
                        category.save()

                        items = GameItemLink.objects.filter(category=category)
                        items.update(itemOrder=0, nextItem=None)

                        messages.add_message(request, messages.ERROR, 'De items zijn niet correct geordend!')
                        return self.get(request, gameID, categoryID)

                # Category and Items succesfully edited
                messages.add_message(request, messages.SUCCESS,
                                     'Categorie en items zijn succesvol aangepast.')
                return redirect('game:adminpanelGamesEditCategory', gameID=game.gameID, categoryID=category.categoryID)
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het aanpassen van een categorie/game item!')

                if 'gameID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                if 'categoryID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'categoryID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelGamesEditCategory', gameID=gameID, categoryID=categoryID)

    class Add(LoginRequiredMixin, View):
        """
        Add new category
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'gameID' in request.POST:
                try:
                    game = Game.objects.get(gameID=request.POST['gameID'])
                except Game.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er is een fout opgetreden bij het toevoegen van een categorie. Controleer of het spel nog bestaat.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{request.POST["gameID"]}\'</i>')
                    return redirect('game:adminpanelGames')

                if game.published is True:
                    messages.add_message(request, messages.ERROR,
                                         'Categoriën kunnen niet aan een Game toegevoegd worden als deze Game gepubliceerd is.')
                    messages.add_message(request, messages.INFO,
                                         'Je moet het spel eerst <i>de-publiceren</i> voordat je aanpassingen kunt maken.')
                    return redirect('game:adminpanelGamesEdit', gameID=request.POST['gameID'])

                if 'newCategoryName' in request.POST:
                    category = Category(categoryName=request.POST['newCategoryName'])
                    category.game = Game.objects.get(gameID=request.POST['gameID'])
                    category.save()
                    return redirect('game:adminpanelGamesEditCategory', gameID=game.gameID,
                                    categoryID=category.categoryID)

            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het toevoegen van een categorie!')

                if 'gameID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                return redirect('game:adminpanelGames')

    class Delete(LoginRequiredMixin, View):
        """
        Delete category
        """

        @in_group_on_class(groups=['gameCreator'])
        def post(self, request):
            if DEBUG is True:
                messages.set_level(request, messages.DEBUG)

            if 'gameID' in request.POST and 'categoryID' in request.POST:
                try:
                    game = Game.objects.get(gameID=request.POST['gameID'])
                    if game.published is True:
                        messages.add_message(request, messages.INFO,
                                             'De-publiceer het spel eerst voordat je aanpassingen maakt.')
                        return redirect('game:adminpanelGamesEdit', gameID=game.gameID)

                    category = Category.objects.get(categoryID=request.POST['categoryID'])
                    category.delete()
                except Game.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er is een fout opgetreden bij het verwijderen van een categorie. Controleer of het spel nog bestaat.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Game.DoesNotExist\'</i> occurred on id <i>\'{request.POST["gameID"]}\'</i>')
                    return redirect('game:adminpanelGames')
                except Category.DoesNotExist:
                    messages.add_message(request, messages.ERROR,
                                         'Er is een fout opgetreden bij het verwijderen van een categorie. Controleer of de categorie nog bestaat.')
                    messages.add_message(request, messages.DEBUG,
                                         f'The exception <i>\'Category.DoesNotExist\'</i> occurred on id <i>\'{request.POST["categoryID"]}\'</i>')
                    return redirect('game:adminpanelGamesEdit', gameID=request.POST["gameID"])
            else:
                # Problems with ID fetching
                messages.add_message(request, messages.ERROR,
                                     'Er ging iets fout tijdens het verwijderen van een categorie!')

                if 'categoryID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'categoryID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                if 'gameID' not in request.POST:
                    messages.add_message(request, messages.DEBUG,
                                         '<i>\'gameID\'</i> is not in <i>\'request.POST\'</i>. Check your constructed form and post method.')
                else:
                    return redirect('game:adminpanelGamesEdit', gameID=request.POST['gameID'])
                return redirect('game:adminpanelGames')
