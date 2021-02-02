from django.db import models

from modules.module_manager import *
from modules.models import AllModuleItems


class Game(models.Model):
    gameID = models.AutoField(primary_key=True)
    gameName = models.CharField(max_length=100)

    # Let the game only be found and accessed through a tag
    accessThroughTag = models.BooleanField(default=False)
    accessTag = models.CharField(max_length=100, unique=True, blank=True, null=True)

    publicationDate = models.DateTimeField(auto_now_add=True)
    lastChangedDate = models.DateTimeField(auto_now=True)

    # Determine whether the game is dependant on a start date/time and end date/time.
    noDateNorTime = models.BooleanField(default=False)
    startDateTime = models.DateTimeField(null=True, blank=True, default=None)
    endDateTime = models.DateTimeField(null=True, blank=True, default=None)

    # Open up for public to enter
    open = models.BooleanField(default=False)

    published = models.BooleanField(default=False)

    # Text displayed on the game 'homescreen'
    generalText = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'

    def __str__(self):
        return self.gameName

    def is_completed(self):
        """
        Check whether a game has been completed or not
        """
        categories = Category.objects.filter(game=self)

        for category in categories:
            if category.is_completed() is False:
                return False
        return True

    def max_score(self):
        """
        Return maximum game score
        """
        categories = Category.objects.filter(game=self)

        score = 0
        for category in categories:
            score += category.maxCategoryScore
        return score

    def obtained_score(self):
        """
        Return obtained game score
        """
        categories = Category.objects.filter(game=self)

        score = 0
        for category in categories:
            score += category.obtainedCategoryScore
        return score


class Category(models.Model):
    categoryID = models.AutoField(primary_key=True)
    categoryName = models.CharField(max_length=100)

    # Set max score is set during publishing by reading the max scores from each connected GameItemLink
    obtainedCategoryScore = models.IntegerField(default=0)
    maxCategoryScore = models.IntegerField(default=0)

    # If a category is chained, the connected GameItemLinks are traversed in "chronological"
    # order as set by their ordering.
    chained = models.BooleanField(default=False)

    # If a category is chained, the first item will point to the first GameItemLink
    firstItem = models.ForeignKey(
        'GameItemLink',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='firstItem'
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Catgory'
        verbose_name_plural = 'Catgories'

    def __str__(self):
        return self.categoryName

    def reset(self):
        """
        Reset values during publishing
        """
        self.obtainedCategoryScore = 0
        self.maxCategoryScore = 0

    def score_percentage(self):
        """
        Calculates a score percentage obtained by dividing the obtained score by the max score
        """
        if self.maxCategoryScore == 0 or self.obtainedCategoryScore == 0:
            return 0
        return int(round((self.obtainedCategoryScore / self.maxCategoryScore) * 100, 0))

    def is_completed(self):
        """
        Check whether a category has been completed or not
        """
        items = GameItemLink.objects.filter(category=self, gameItemStateCompleted=False)

        if items.count() == 0:
            return True
        else:
            return False


class GameItemLink(models.Model):
    gameItemLinkID = models.AutoField(primary_key=True)
    gameItemLinkName = models.CharField(max_length=100)

    # Foreign key to the actual module. Depending on the type, it points to an entirely new and specific database
    # and handlers. Always use module_item_content() and module_item_handlers() when interacting with the modules.
    module = models.ForeignKey(
        AllModuleItems,
        on_delete=models.CASCADE
    )

    # Used for "chronological" sequence followup when the category is set to chained
    nextItem = models.ForeignKey(
        'GameItemLink',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Itemorder used to correctly order the items in the game "homescreen" and used for chaining.
    itemOrder = models.IntegerField(default=0, blank=True, null=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

    # Hidden item
    hidden = models.BooleanField(default=False)

    # Determine how many users need to provide a correct answer
    gameItemStateGivenNInput = models.IntegerField(default=0)

    # Max number of attempt and keeps track of how many wrong answers have been given
    gameItemStateGivenWrongNInput = models.IntegerField(default=0)
    maxNumAttempts = models.IntegerField(default=1)

    # Used for item routing and feedback to user
    gameItemStateVisited = models.BooleanField(default=False)
    gameItemStateCompleted = models.BooleanField(default=False)

    # Game can only be continued by a gamemaster
    gameItemContinueByGM = models.BooleanField(default=False)

    # Maximum allowed time for a given gameitem
    gameItemMaxTime = models.TimeField(null=True, default=None, blank=True)
    gameItemStartTime = models.DateTimeField(null=True, default=None, blank=True)

    # Max score is set during game creation and obtainedscore is calculated after a question has been answered
    maxScore = models.IntegerField(default=0)
    obtainedScore = models.IntegerField(default=0)

    # Number of points subtracted with each wrong answer
    faultPenalty = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'GameItemLink'
        verbose_name_plural = 'GameItemLinks'

    def __str__(self):
        if models is None:
            return self.gameItemLinkName
        return self.module.__str__()

    def module_item_content(self):
        """
        Returns the model object of the connected module
        """
        return self.module.module_item_content()

    def module_item_handlers(self, admin=False):
        """
        Returns the handler functions of the connected module
        """
        return self.module.module_item_handlers(admin)

    def reset(self):
        """
        Resets all the parameters (usually called during publishing)
        """
        self.module_item_handlers(True).reset(self.gameItemLinkID)
        self.gameItemStateCompleted = False
        self.gameItemStateVisited = False
        self.gameItemStateGivenNInput = 0
        self.gameItemStateGivenWrongNInput = 0
        self.obtainedScore = 0
        self.save()
