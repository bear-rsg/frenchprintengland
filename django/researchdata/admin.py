from django.contrib import admin
from django.db.models import ManyToManyField, ForeignKey
from . import models


# Actions


def publish(modeladmin, request, queryset):
    """
    Sets all selected objects in queryset to published
    """
    queryset.update(published=True)


publish.short_description = "Publish selected items (will appear on main site)"


def unpublish(modeladmin, request, queryset):
    """
    Sets all selected objects in queryset to not published
    """
    queryset.update(published=False)


unpublish.short_description = "Unpublish selected items (will not appear on main site)"


#
# 1. Reusable code
#


def get_manytomany_fields(model, exclude=[]):
    """
    Returns a list of strings containing the field names of many to many fields of a model
    To ignore certain fields, provide a list of such field names (as strings) using the exclude parameter
    """
    return list(f.name for f in model._meta.get_fields() if type(f) is ManyToManyField and f.name not in exclude)


def get_foreignkey_fields(model, exclude=[]):
    """
    Returns a list of strings containing the field names of foreign key fields of a model
    To ignore certain fields, provide a list of such field names (as strings) using the exclude parameter
    """
    return list(f.name for f in model._meta.get_fields() if type(f) is ForeignKey and f.name not in exclude)


class GenericAdminView(admin.ModelAdmin):
    """
    This is a generic class that can be applied to most models to customise their inclusion in the Django admin.

    This class can either be inherited from to customise, e.g.:
    class [ModelName]AdminView(GenericAdminView):

    Or if you don't need to customise it just register a model, e.g.:
    admin.site.register([model name], GenericAdminView)
    """
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)
    list_per_page = 50
    search_fields = ('id', 'name',)
    exclude = ('name_clean',)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set all many to many fields to display the filter_horizontal widget
        self.filter_horizontal = get_manytomany_fields(self.model)
        # Set all foreign key fields to display the autocomplete widget
        self.autocomplete_fields = get_foreignkey_fields(self.model)


# Simple ModelAdmins


admin.site.register(models.Gender, GenericAdminView)
admin.site.register(models.AgentRole, GenericAdminView)
admin.site.register(models.Place, GenericAdminView)
admin.site.register(models.Language, GenericAdminView)
admin.site.register(models.TextType, GenericAdminView)
admin.site.register(models.FormatOfPublication, GenericAdminView)
admin.site.register(models.Subject, GenericAdminView)
admin.site.register(models.PrimarySource, GenericAdminView)
admin.site.register(models.SecondarySource, GenericAdminView)


# Custom ModelAdmins


@admin.register(models.Agent)
class AgentAdminView(GenericAdminView):
    """ Customise the admin interface for Agent model """

    list_filter = ('gender',)


@admin.register(models.Text)
class TextAdminView(GenericAdminView):
    """ Customise the admin interface for Text model """

    list_display = (
        'id',
        'title',
        'author',
        'record_date_created',
        'record_date_updated',
        'published',
    )
    list_display_links = ('id',)
    actions = (publish, unpublish)
    search_fields = (
        'id',
        'title',
        'notes'
    )
    list_filter = (
        'published',
        'type',
        'format_of_publication',
        'subject',
    )
    fieldsets = (
        ('', {
            'fields': (
                'title',
                'author',
            )
        }),
        ('Publication Information', {
            'fields': (
                'translator',
                'other_contributors',
                'place',
                'false_imprint',
                'address_of_publication',
                'associated_location',
                'publisher',
                'year_of_publication',
                'specific_date',
                'lost_book',
            )
        }),
        ('Properties', {
            'fields': (
                'languages',
                'multilingual',
                'translation',
                'type',
                'format_of_publication',
                'number_of_issues',
                'pagination',
                'number_of_main_text_pages',
                'number_of_liminary_pages',
                'number_of_pages_containing_french',
                'dedicatee',
                'illustrations',
                'nelson_and_seccombe',
                'plre'
            )
        }),
        ('Bibliographical Information', {
            'fields': (
                'stc',
                'estc',
                'ustc',
                'fb_number',
                'rccc',
                'full_text_image',
                'full_text_transcription',
                'subject',
                'primary_sources',
                'secondary_sources',
                'number_of_surviving_copies_in_uk',
                'number_of_surviving_copies_in_continental_europe',
                'number_of_surviving_copies_in_rest_of_world'
            )
        }),
        ('Admin', {
            'fields': (
                'notes',
                'record_date_created',
                'record_date_updated',
                'published',
            )
        }),
    )
    readonly_fields = (
        'record_date_created',
        'record_date_updated'
    )
