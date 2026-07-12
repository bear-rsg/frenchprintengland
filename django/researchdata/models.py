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
    associated_country = models.CharField(max_length=1000, blank=True, null=True)
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


class Place(SimpleModelAbstract):
    """ A Place, e.g. place of publication of a text """


class Language(SimpleModelAbstract):
    """ Language, e.g. English, French """


class TextType(SimpleModelAbstract):
    """ Type of text """


class FormatOfPublication(SimpleModelAbstract):
    """ Format of publication, e.g. 4to, 8to """


class Subject(SimpleModelAbstract):
    """ Subject of a text """


class PrimarySource(SimpleModelAbstract):
    """ Primary source of text """

    related_name = 'primarysources'

    name = models.CharField(max_length=1000, verbose_name='title')
    author = models.ForeignKey(Agent, related_name=f'{related_name}_authors', on_delete=models.SET_NULL, blank=True, null=True)
    other_contributors = models.ManyToManyField(Agent, related_name=f'{related_name}_othercontributors', blank=True)
    place_of_publication = models.ForeignKey(Place, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True)
    year_of_publication = models.CharField(max_length=1000, blank=True, null=True)
    languages = models.ManyToManyField(Language, related_name=related_name, blank=True)
    manuscript = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)


class SecondarySource(SimpleModelAbstract):
    """ Secondary source of text """

    related_name = 'secondarysources'

    name = models.CharField(max_length=1000, verbose_name='title')
    author = models.ForeignKey(Agent, related_name=f'{related_name}_authors', on_delete=models.SET_NULL, blank=True, null=True)
    year_of_publication = models.CharField(max_length=1000, blank=True, null=True)
    link = models.URLField(blank=True, null=True)


# 2. Primary Models


class Text(models.Model):
    """
    The main primary model, contains data about Texts used in project
    """

    related_name = 'texts'

    title = models.CharField(max_length=1000)
    author = models.ForeignKey(Agent, related_name=f'{related_name}_authors', on_delete=models.SET_NULL, blank=True, null=True)

    # Publication Information
    translator = models.ForeignKey(Agent, related_name=f'{related_name}_translator', on_delete=models.SET_NULL, blank=True, null=True)
    other_contributors = models.ManyToManyField(Agent, related_name=f'{related_name}_othercontributors', blank=True)
    place = models.ForeignKey(Place, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True)
    false_imprint = models.BooleanField(default=False)
    address_of_publication = models.TextField(blank=True, null=True)
    associated_location = models.CharField(max_length=1000, blank=True, null=True)
    publisher = models.ManyToManyField(Agent, related_name=f'{related_name}_publishers', blank=True, verbose_name='printer/publisher')
    year_of_publication = models.IntegerField(blank=True, null=True)
    specific_date = models.CharField(max_length=1000, blank=True, null=True)
    lost_book = models.BooleanField(default=False)

    # Properties
    languages = models.ManyToManyField(Language, blank=True)
    multilingual = models.BooleanField(default=False)
    translation = models.BooleanField(default=False)
    type = models.ForeignKey(TextType, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True)
    format_of_publication = models.ForeignKey(FormatOfPublication, related_name=related_name, on_delete=models.SET_NULL, blank=True, null=True)
    number_of_issues = models.IntegerField(blank=True, null=True)
    pagination = models.CharField(max_length=1000, blank=True, null=True)
    number_of_main_text_pages = models.IntegerField(blank=True, null=True)
    number_of_liminary_pages = models.IntegerField(blank=True, null=True)
    number_of_pages_containing_french = models.IntegerField(blank=True, null=True, verbose_name='Number of pages containing French')
    dedicatee = models.ManyToManyField(Agent, related_name=f'{related_name}_dedicatees', blank=True)
    illustrations = models.BooleanField(default=False)
    nelson_and_seccombe = models.TextField(blank=True, null=True, verbose_name='Nelson and Seccombe')
    plre = models.TextField(blank=True, null=True, verbose_name='PLRE')
    owner = models.ManyToManyField(Agent, related_name=f'{related_name}_owners', blank=True)
    illustrations = models.BooleanField(default=False)

    # Bibliographical Information
    stc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='STC/Wing number')
    estc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='ESTC')
    ustc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='USTC')
    fb_number = models.CharField(max_length=1000, blank=True, null=True, verbose_name='FB number')
    rccc = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Renaissance Cultural Crossroads Catalogue (RCCC)')
    full_text_image = models.CharField(max_length=1000, blank=True, null=True, verbose_name='full-text - image')
    full_text_transcription = models.TextField(blank=True, null=True, verbose_name='full-text - transcription')
    subject = models.ManyToManyField(Subject, related_name=related_name, blank=True)
    primary_sources = models.ManyToManyField(PrimarySource, related_name=related_name, blank=True)
    secondary_sources = models.ManyToManyField(SecondarySource, related_name=related_name, blank=True)
    number_of_surviving_copies_in_uk = models.IntegerField(blank=True, null=True, verbose_name='Number of surviving copies in UK and Ireland')
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
