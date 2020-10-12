# QuantumRules
An online quiz and escape room development framework

The QuantumRules framework was developed with expandability in mind. Future development with this framework should allow new development teams to quickly implement new features.

To accomplish this, the framework has been designed with modularity in mind. It contains a lot of pre-fabd features that help programmers to quickly and independently develop new components without further knowledge about the framework. In this README.md a quick overview will be given on what is needed to develop the software and how you develop within the given framework.

# Getting started
To get started, a few steps need to be taken beforehand. Because this framework is based on a few packages and 3rd party systems, you'll need to set those up before development can start.
1. Create a new virtualenvironment with venv.
2. Install all the dependencies from **requirements.txt**. The dependencies have been created with python pip and you should be able to fetch all the requirements by feeding pip the **requirements.txt** file.
3. Install the in memory datastructure system *REDIS*. The REDIS API is used for group layered socket communications.
  - Windows users should install *Memurai*. *Memurai* is fully compatible with the REDIS API
4. In **QR2/settings.py** make sure that `DEBUG` is set to `True`. Make sure that the database is set to the default development database under `DATABASES` ***NEVER develop on a live database!***. Make sure that under `CHANNEL_LAYERS` you set the `hosts` to your local redis server (often localhost or *127.0.0.1*)
5. From **QR2** run ```python manage.py makemigrations```. This will generate a database initiation.
6. From **QR2** run ```python manage.py migrate```. This will construct all necessary database structures
7. You have to create a superuser to be able to do testing on the admin side. To do this run ```python manage.py createsuperuser```. For correctly setting up multiple users, please refer to the section about **users**
8. From **QR2** run ```python manage.py runserver```
9. Enjoy developing!

# Users
In this framework we use the standard *Django* user and authentication framework. In order to add a new user you first need to have a superuser. Refer to the getting started guide above as to how you add a superuser. Launch the server with the ```runserver``` command and go to */admin* and navigate to the user (gebruiker) database page. There you will find an option to add a new user. Fill in the details and add the user.

## Permissions
Within this framework, several usertypes exist. The frontend users (using frontend not in development terms but in userspace terms), are essentially the players of the game and they join games without any accounts. The backend is the admin side and you can only access it with a django account. In the backend there are three roles to be distinguished: *superuser*, *game creator* and *game master*. The superuser can do everything, including accessing the */admin* site. The *game creator* and *game master* can create and change games and run games respectively. For most endusers, it is not advised to use the *superuser* option because of the non safe */admin* environment. Instead, most endusers should be non *superuser* accounts that will be added to permission **groups**. The *game creator* will be in the group **gameCreator** and the *game master* will be in the group **gameMaster**. Note that these groups are used internally in the code and are therefor **MANDATORY** groups. In production, these two groups should always be present!

## Groups
To add groups, including the two mandatory groups, navigate go to */admin* and navigate to the group (groepen) database page. There you will find the option to add new groups. You can also add permissions to these groups, but that option is not used within this framework.

### Adding groups to users
To add a group to a user go to */admin* and navigate to the user (gebruiker) database page. Select a user and from within the user page, add an existing group to the user and save.

## More information
For more information about the way users, groups and authentication works, please refer to the official django manual.

# Developing a new module
Developing a new module is not that difficult. The modules are housed within the **modules** folder. To add a new module, you will have to do four (optionally  five) things:
## Adding a new module
1. Within **modules/models** create a new folder, preferably with the name of your new module. Within this folder, add an `__init__.py` file and a new model file. In this new folder, e.g. **modules/models/mathProblems** you can house multiple different model files. You can construct your models almost exactly the way you like. Your main model should adhere to some standards with respect to field naming which are the following:
  *    ```ID = models.AutoField(primary_key=True)```
  *    ```name = models.CharField(max_length=100)```
  *    ```has_hint = models.BooleanField(default=False)```
  *    ```hint_content = models.TextField(null=True, blank=True)```
  *    ```video_link = models.CharField(max_length=300, null=True, blank=True)```

  *    ```publicationDate = models.DateTimeField(auto_now_add=True)```
  *    ```lastChangedDate = models.DateTimeField(auto_now=True)```
You could change these fields, but it is not recommended! Within these model files you can construct any database you want. You can even link GameItemLink objects (used to point to a module within a game) in your model since these are provided in standard input. Once you have created your new models for you module, don't forget to make your migrations and migrate the new models to the database. *Do not forget to populate your `__init__.py` files*
2. Within **modules/views** create a new folder, preferably with the name of your new module. Within this folder, add an `__init__.py` file a frontend view file and a backend admin view file. These views will handle the rendering of your module, they will handle user input and they will handle database management on a admin level. These view files are a bit more strictly constructed and should adhere to a stricter naming convention in terms of method naming. For the frontend:
  * ```def render_module(request, gameID, itemID):```
  * ```def handle_input(input, gameID, itemID, raw_request_data=None, raw_socket_data=None):```
and for the backend:
  * ```def render_adding_in_category(request, typeID, gameID, categoryID):```
  * ```def render_adding(request, typeID):```
  * ```def render_edit(request, typeID, itemID):```
  * ```def add(request):```
  * ```def edit(request, itemID):```
  * ```def delete(request, itemID):```
  * ```def reset(linkID):```
These methods **cannot** be named differently. You are however free to add any amount of your own methods to support to framework method basis.
3. In order to render out your modules, you'll need to construct a new HTML/JS template. These are found in **templates/modules**. For Note that you will have to create at the minimum four templates, three for admin and one for the end user frontend. The admin side is used to add new items, add existing or new items to a category and edit existing items. The user frontend is used to render the final module item to the user. The admin templates can be (don't have to, but that is harder) based on an extend to **game/gameAdminpanel/editadd_item.html** for the adding and editing and **game/gameAdminpanel/category_add_item.html** for the adding in a category. The frontend template can be based on an extension of **game/base/base_running_item.html**. All of these base templates are completely build up from django ```{% block %}``` elements. Be sure to familiarize yourself with the django template block systems. Also be sure to study the base templates and all their blocks. Some modules can be templated without altering the basic block fields at all. Also note that on the end user frontend templates, sockets are used as a mean of communications. You don't really have to worry too much about the design of input form since this is pretty much handled in the backend. You can also extend these sockets for more event handlings (again, see the blocks).
4. In order to access your newly build modules from the actual underlying framework, and in order to use them in a game, you will have to register these new modules! Registering these modules is fairly straight forward. In **modules/module_manager.py** you will have to create a new type in ```class ItemTypes```. In the same file, under ```def select_module(item_type, as_model=False, as_admin=False):``` you will have to register the module importing.
5. **OPTIONAL** Optionally you can choose to use the build in django forms and the crispy-forms expansion to add easy formhandling and creation to your modules. These forms are based under **modules/forms**. There you can create a new folder and create new forms which can use in your views and templates
## recommendations
I highly recommend to study existing modules, such as *TextItem* and *MultipleChoice* to understand how the methods of the module framework work. These methods will also have a more detailed description as to what they are supposed to do. I also recommend to experiment with simpler and smaller modules first before implementing a big one to get a feel for them.
