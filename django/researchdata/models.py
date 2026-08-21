from django.db import models
from django.urls import reverse
from django.db.models.functions import Upper


# 1. Secondary Models
# 2. Primary Models


class SimpleModelAbstract(models.Model):
    """
    An abstract model for simple models that only include a name field
    See: https://docs.djangoproject.com/en/4.0/topics/db/models/#abstract-base-classes
    """

    name = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = [Upper('name'), 'id']
        constraints = [
            models.UniqueConstraint(
                Upper('name'),
                name='unique_%(app_label)s_%(class)s_name'
            )
        ]


# 1. Secondary Models


class PlaceType(SimpleModelAbstract):
    """ A type of place """


class Place(SimpleModelAbstract):
    """ A Place, e.g. place of publication of a text """

    types = models.ManyToManyField(PlaceType, related_name='places', blank=True)


class Gender(SimpleModelAbstract):
    """ Genders (e.g. male, female) """


class AgentRole(SimpleModelAbstract):
    """ A role of agent (e.g. author, contributor, publisher, etc.) """


class Agent(SimpleModelAbstract):
    """ An author, contributor, publisher, etc. of a text """

    related_name = 'agents'

    roles = models.ManyToManyField(AgentRole, related_name=related_name, blank=True)
    gender = models.ForeignKey(Gender, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True)
    birth_year = models.CharField(max_length=1000, blank=True, null=True)
    death_year = models.CharField(max_length=1000, blank=True, null=True)
    associated_countries = models.ManyToManyField(Place, related_name=related_name, blank=True)
    viaf = models.CharField(max_length=1000, blank=True, null=True, verbose_name='VIAF')
    other_links = models.TextField(blank=True, null=True)

    def roles_as_str(self):
        roles = list(self.roles.all())
        if roles:
            return ", ".join(str(role) for role in roles)

    def __str__(self):
        return self.name

    class Meta:
        ordering = [Upper('name'), 'id']


class Language(SimpleModelAbstract):
    """ Language, e.g. English, French """


class TextType(SimpleModelAbstract):
    """ Type of text """


class TextualFeatures(SimpleModelAbstract):
    """ Features of a text """

    class Meta:
        verbose_name_plural = 'textual features'


class FormatOfPublication(SimpleModelAbstract):
    """ Format of publication, e.g. 4to, 8to """


class Subject(SimpleModelAbstract):
    """ Subject of a text """


class Relationships(SimpleModelAbstract):
    """ Relationships of a text """

    class Meta:
        verbose_name_plural = 'relationships'


# 2. Primary Models


class Text(models.Model):
    """
    The main primary model, contains data about Texts used in project
    """

    related_name = 'texts'

    estc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='ESTC')
    stc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='STC/Wing')
    ustc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='USTC')
    title = models.TextField()
    author = models.ForeignKey(Agent, related_name=f'{related_name}_authors', on_delete=models.SET_NULL, blank=True, null=True)
    translators = models.ManyToManyField(Agent, related_name=f'{related_name}_translators', blank=True)
    other_contributors = models.ManyToManyField(Agent, related_name=f'{related_name}_othercontributors', blank=True)

    # Publication Information
    imprint = models.TextField(blank=True, null=True)
    place_of_publication = models.ForeignKey(Place, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True)
    false_imprint = models.BooleanField(default=False)
    publishers = models.ManyToManyField(Agent, related_name=f'{related_name}_publishers', blank=True, verbose_name='printer/publisher')
    year_of_publication = models.CharField(max_length=1000, blank=True, null=True)
    associated_date = models.CharField(max_length=1000, blank=True, null=True)
    associated_locations = models.ManyToManyField(Place, blank=True)
    lost_book = models.BooleanField(default=False)

    # Properties
    languages = models.ManyToManyField(Language, blank=True)
    number_of_languages = models.IntegerField(blank=True, null=True)
    text_type = models.ForeignKey(TextType, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='type')
    format_of_publication = models.ForeignKey(FormatOfPublication, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True)
    number_of_issues = models.IntegerField(blank=True, null=True)
    pagination = models.CharField(max_length=1000, blank=True, null=True)
    textual_features = models.ManyToManyField(TextualFeatures, related_name=f'{related_name}_dedicatees', blank=True)
    dedicatees = models.ManyToManyField(Agent, related_name=f'{related_name}_dedicatees', blank=True)

    # Bibliographical Information
    fb = models.CharField(max_length=1000, blank=True, null=True, verbose_name='FB')
    rccc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='RCCC')
    nelson_and_seccombe = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Nelson and Seccombe')
    stationers_register = models.CharField(max_length=1000, blank=True, null=True, verbose_name="stationers' register")
    plre = models.CharField(max_length=1000, blank=True, null=True, verbose_name='PLRE')
    owners = models.ManyToManyField(Agent, related_name=f'{related_name}_owners', blank=True)
    full_text_image = models.CharField(max_length=1000, blank=True, null=True, verbose_name='full-text - image')
    full_text_transcription = models.CharField(max_length=1000, blank=True, null=True, verbose_name='full-text - transcription')
    subjects = models.ManyToManyField(Subject, related_name=related_name, blank=True)
    relationships = models.ManyToManyField(Relationships, related_name=related_name, blank=True)
    number_of_surviving_copies_in_uk = models.IntegerField(blank=True, null=True,
                                                           verbose_name='Number of surviving copies in UK and Ireland')
    number_of_surviving_copies_in_continental_europe = models.IntegerField(blank=True, null=True, verbose_name='Number of Surviving Copies in Continental Europe')
    number_of_surviving_copies_in_rest_of_world = models.IntegerField(blank=True, null=True)

    # Admin
    notes = models.TextField(blank=True, null=True)
    record_date_created = models.DateTimeField(auto_now_add=True)
    record_date_updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('researchdata:text-detail', args=[str(self.id)])

    class Meta:
        ordering = [Upper('title'), 'id']
