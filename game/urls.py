from django.urls import path

from . import views

app_name = 'game'
urlpatterns = [
    path('', views.GamesIndexView.as_view(), name='index'),
    path('tag/', views.game_tag_entry, name='tag'),
    path('<int:gameID>/', views.game_items_index, name='gameIndex'),
    path('<int:gameID>/item/<int:itemID>/post/', views.module_item_post, name='modulePost'),
    path('<int:gameID>/render/<int:ID>/<str:is_cat>/', views.render_item, name='renderItem'),

# Adminpanel
    path('adminpanel/', views.adminpanel, name='adminpanel'),

    path('adminpanel/gamemaster/index/', views.GameMaster.Get_All.as_view(), name='gamemasterIndex'),
    path('adminpanel/gamemaster/panel/<int:gameID>/', views.GameMaster.GameMasterPanel.as_view(), name='gamemasterPanel'),
    path('adminpanel/gamemaster/Announce/', views.GameMaster.Announcement.as_view(), name='gamemasterPanelAnnounce'),
    path('adminpanel/gamemaster/finishbygm/', views.GameMaster.finishItemByGM.as_view(), name='gamemasterPanelFinishByGM'),
    path('adminpanel/games/Announce/', views.Games.Announcement.as_view(), name='makeAnnouncement'),
    path('adminpanel/games/', views.Games.Get_All.as_view(), name='adminpanelGames'),
    path('adminpanel/games/add/', views.Games.Add.as_view(), name='adminpanelGamesAdd'),
    path('adminpanel/games/delete/', views.Games.Delete.as_view(), name='adminpanelGamesDelete'),
    path('adminpanel/games/duplicate/', views.Games.Duplicate.as_view(), name='adminpanelGamesDuplicate'),
    path('adminpanel/games/<int:gameID>/', views.Games.Edit.as_view(), name='adminpanelGamesEdit'),
    path('adminpanel/games/publish/', views.Publish.Publish.as_view(), name='adminpanelGamesEditPublish'),
    path('adminpanel/games/item/finishbygm/', views.Games.finishItemByGM.as_view(), name='adminpanelItemFinishByGM'),
    path('adminpanel/games/<int:gameID>/category/<int:categoryID>/', views.Categories.Edit.as_view(), name='adminpanelGamesEditCategory'),
    path('adminpanel/categories/add/', views.Categories.Add.as_view(), name='adminpanelCategoriesAdd'),
    path('adminpanel/categories/delete/', views.Categories.Delete.as_view(), name='adminpanelCategoriesDelete'),
    path('adminpanel/categories/addItemConstruct', views.Items.AddInCategoryUrlScrubber.as_view(), name='adminpanelCategoriesAddItemConstruct'),
    path('adminpanel/categories/addItem/<str:typeID>/<int:categoryID>/<int:gameID>/', views.Items.AddInCategory.as_view(), name='adminpanelCategoriesAddItem'),
    path('adminpanel/categories/addExistingItem/', views.Items.AddExistingItemToCategory.as_view(), name='adminpanelCategoriesAddExistingItem'),
    path('adminpanel/modules/', views.AllItems.as_view(), name='adminpanelModules'),
    path('adminpanel/modules/<int:itemID>/', views.Items.EditItem.as_view(), name='adminpanelModulesEdit'),
    path('adminpanel/modules/addConstruct', views.Items.AddUrlScrubber.as_view(), name='adminpanelModulesAddItemConstruct'),
    path('adminpanel/modules/add/<str:typeID>/', views.Items.AddItem.as_view(), name='adminpanelModulesAddItem'),
    path('adminpanel/modules/delete/<int:itemID>/', views.Items.DeleteItem.as_view(), name='adminpanelModulesDelete'),

]
