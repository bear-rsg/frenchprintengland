from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.db.models.functions import Lower
from django.db.models import CharField, Q, Count, TextField
from django.urls import reverse
from datetime import datetime
from . import models
import csv


def get_field_type(field_name, queryset):
    """
    Return the type of a field
    E.g. used in sort() to see if case insensitivity is needed (if field is a CharField/TextField)
    """
    try:
        stripped_field_name = field_name.lstrip('-')
        if stripped_field_name in queryset.query.annotations:
            return queryset.query.annotations[stripped_field_name].output_field
        return queryset.model._meta.get_field(stripped_field_name)
    except Exception:
        return CharField  # If it fails, assume it's a CharField by default


def queryset_as_str(queryset, separator=', '):
    """
    Return a string of all objects in a queryset separated by a separator
    """

    if len(queryset):
        return separator.join(str(obj) for obj in queryset)


# Special starts to the values & labels of options in 'filter' select lists
# used in below filter() function and within views scripts
filter_pre = 'filter_'
filter_pre_mm = f'{filter_pre}mm_'  # Many to Many relationship
filter_pre_fk = f'{filter_pre}fk_'  # Foreign Key relationship
filter_pre_gt = f'{filter_pre}gt_'  # Greater than (or equal to) filter, e.g. "Date (from)"
filter_pre_lt = f'{filter_pre}lt_'  # Less than (or equal to) filter, e.g. "Date (to)"


def filter(request, queryset):
    """
    request = http request object, e.g. self.request
    queryset = the Django queryset to be searched

    Returns a filtered Django queryset, allowing for multiple filters (of M2M and FK relationships) to be applied
    """

    # Only loop through filter values in all GET request values (e.g. exclude search, sort, etc. values)
    for filter_key in [k for k in list(request.GET.keys()) if k.startswith(filter_pre)]:

        filter_value = request.GET.get(filter_key, '')
        if filter_value != '':

            # Many to Many relationship (uses __in comparison and filter_value is a list)
            if filter_key.startswith(filter_pre_mm):
                filter_field = filter_key.replace(filter_pre_mm, '')
                queryset = queryset.filter(**{f'{filter_field}__in': [filter_value]})

            # Foreign Key relationship
            elif filter_key.startswith(filter_pre_fk):
                filter_field = filter_key.replace(filter_pre_fk, '')
                queryset = queryset.filter(**{filter_field: filter_value})

            # Greater than or equal to
            elif filter_key.startswith(filter_pre_gt):
                filter_field = filter_key.replace(filter_pre_gt, '')
                queryset = queryset.filter(**{f'{filter_field}__gte': filter_value})

            # Less than or equal to
            elif filter_key.startswith(filter_pre_lt):
                filter_field = filter_key.replace(filter_pre_lt, '')
                queryset = queryset.filter(**{f'{filter_field}__lte': filter_value})

    return queryset


# Special starts to the values & labels of options in 'sort by' select lists,
# used in below sort() function and within views scripts
sort_pre_count_value = 'count_'
sort_pre_count_label = 'Number of '


def sort(request, queryset, sort_by_default='id'):
    """
    request = http request object, e.g. self.request
    queryset = the Django queryset to be sorted
    sort_by_default = default field to sort by, e.g. id, ...

    Returns a sorted Django queryset
    """

    # Establish the sort direction (asc/desc) and the field to sort by, from the request
    sort_dir = request.GET.get('sort_direction', '')
    sort_by = request.GET.get('sort_by', sort_by_default)
    sort = sort_dir + sort_by
    sort_pre_length = len(f"{sort_dir}{sort_pre_count_value}")  # e.g. '-numerical_' for descending numerical

    # Count sorting (e.g. sort by count of related items)
    if sort_pre_count_value in sort:
        order_by = sort_dir + 'countitems'  # '-countitems' if descending, 'countitems' if ascending
        return queryset.annotate(countitems=Count(sort[sort_pre_length:])).order_by(order_by)
    # Standard sort
    else:

        # Sort descending (Z-A)
        if sort_dir == '-':
            # Convert CharField and TextField values to lowercase, for case insensitivity
            if isinstance(get_field_type(sort_by, queryset), (CharField, TextField)):
                return queryset.order_by(Lower(sort_by).desc())
            else:
                return queryset.order_by(sort)

        # Sort ascending (A-Z)
        else:
            # Convert CharField and TextField values to lowercase, for case insensitivity
            if isinstance(get_field_type(sort_by, queryset), (CharField, TextField)):
                return queryset.order_by(Lower(sort_by))
            else:
                return queryset.order_by(sort_by)


class TextDetailView(DetailView):
    """
    Class-based view for text detail template
    """
    template_name = 'researchdata/detail.html'

    def get_queryset(self):
        queryset = models.Text.objects.all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Admin URL
        context['admin_url'] = reverse('admin:researchdata_text_change', args=[self.object.id])

        # Details
        context['details'] = [
            {'label': 'Author', 'value': self.object.author},
            {'label': 'Translator', 'value': self.object.translator},
            {'label': 'Other contributors', 'value': queryset_as_str(self.object.other_contributors.all())},
            {'label': 'Place', 'value': self.object.place},
            {'label': 'False imprint', 'value': self.object.false_imprint},
            {'label': 'Address of publication', 'value': self.object.address_of_publication},
            {'label': 'Associated location', 'value': self.object.associated_location},
            {'label': 'Publisher', 'value': queryset_as_str(self.object.publisher.all())},
            {'label': 'Year of publication', 'value': self.object.year_of_publication},
            {'label': 'Specific date', 'value': self.object.specific_date},
            {'label': 'Lost book', 'value': self.object.lost_book},
            {'label': 'Languages', 'value': queryset_as_str(self.object.languages.all())},
            {'label': 'Multilingual', 'value': self.object.multilingual},
            {'label': 'Translation', 'value': self.object.translation},
            {'label': 'Type', 'value': self.object.type},
            {'label': 'Format_of_publication', 'value': self.object.format_of_publication},
            {'label': 'Number_of_issues', 'value': self.object.number_of_issues},
            {'label': 'Pagination', 'value': self.object.pagination},
            {'label': 'Number of main text pages', 'value': self.object.number_of_main_text_pages},
            {'label': 'Number of liminary pages', 'value': self.object.number_of_liminary_pages},
            {'label': 'Number of pages containing French', 'value': self.object.number_of_pages_containing_french},
            {'label': 'Dedicatee', 'value': queryset_as_str(self.object.dedicatee.all())},
            {'label': 'Illustrations', 'value': self.object.illustrations},
            {'label': 'Nelson and Seccombe', 'value': self.object.nelson_and_seccombe},
            {'label': 'PLRE', 'value': self.object.plre},
            {'label': 'Owner', 'value': queryset_as_str(self.object.owner.all())},
            {'label': 'Illustrations', 'value': self.object.illustrations},
            {'label': 'STC', 'value': self.object.stc},
            {'label': 'ESTC', 'value': self.object.estc},
            {'label': 'USTC', 'value': self.object.ustc},
            {'label': 'FB number', 'value': self.object.fb_number},
            {'label': 'RCCC', 'value': self.object.rccc},
            {'label': 'Full text image', 'value': self.object.full_text_image},
            {'label': 'Full text transcription', 'value': self.object.full_text_transcription},
            {'label': 'Subject', 'value': queryset_as_str(self.object.subject.all())},
            {'label': 'Primary sources', 'value': queryset_as_str(self.object.primary_sources.all())},
            {'label': 'Secondary sources', 'value': queryset_as_str(self.object.secondary_sources.all())},
            {'label': 'Number of surviving copies in UK', 'value': self.object.number_of_surviving_copies_in_uk},
            {'label': 'Number of surviving copies in continental Europe', 'value': self.object.number_of_surviving_copies_in_continental_europe},
            {'label': 'Number of surviving copies in rest of the world', 'value': self.object.number_of_surviving_copies_in_rest_of_world},
        ]

        return context


class TextListView(ListView):
    """
    Class-based view for text list template
    """
    template_name = 'researchdata/list.html'
    model = models.Text
    paginate_by = 60

    def get_queryset(self):
        # Start with all published objects
        queryset = self.model.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(published=True)

        # Search
        search = self.request.GET.get('search', '')
        if search != '':
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(address_of_publication__icontains=search) |
                Q(associated_location__icontains=search) |
                Q(specific_date__icontains=search) |
                Q(pagination__icontains=search) |
                Q(nelson_and_seccombe__icontains=search) |
                Q(plre__icontains=search) |
                Q(stc__icontains=search) |
                Q(estc__icontains=search) |
                Q(ustc__icontains=search) |
                Q(fb_number__icontains=search) |
                Q(rccc__icontains=search) |
                Q(full_text_image__icontains=search) |
                Q(full_text_transcription__icontains=search) |

                # FK
                Q(author__name__icontains=search) |
                Q(translator__name__icontains=search) |
                Q(place__name__icontains=search) |
                Q(type__name__icontains=search) |
                Q(format_of_publication__name__icontains=search)
            )
        # Filters
        queryset = filter(self.request, queryset)
        # Sort
        queryset = sort(self.request, queryset, 'title')
        # Return result, showing only distinct
        return queryset.distinct()\
            .prefetch_related(
                'other_contributors',
                'publisher',
                'languages',
                'dedicatee',
                'owner',
                'subject',
                'primary_sources',
                'secondary_sources',
            )\
            .select_related(
                'author',
                'translator',
                'place',
                'type',
                'format_of_publication'
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Options: Filters
        context['filters'] = [
            {
                'filter_id': f'{filter_pre_fk}author',
                'filter_name': 'Author',
                'filter_options': models.Agent.objects.filter(roles__name__iexact='author').distinct()
            },
            {
                'filter_id': f'{filter_pre_fk}translator',
                'filter_name': 'Translator',
                'filter_options': models.Agent.objects.filter(roles__name__iexact='translator').distinct()
            },
            {
                'filter_id': f'{filter_pre_fk}place',
                'filter_name': 'Place',
                'filter_options': models.Place.objects.all()
            },
            {
                'filter_id': f'{filter_pre_fk}type',
                'filter_name': 'Text Type',
                'filter_options': models.TextType.objects.all()
            },
            {
                'filter_id': f'{filter_pre_fk}format_of_publication',
                'filter_name': 'Format of Publication',
                'filter_options': models.FormatOfPublication.objects.all()
            },
            {
                'filter_id': f'{filter_pre_mm}publishers',
                'filter_name': 'Publisher',
                'filter_options': models.Agent.objects.filter(roles__name__iexact='publisher').distinct()
            },
            {
                'filter_id': f'{filter_pre_mm}languages',
                'filter_name': 'Language',
                'filter_options': models.Language.objects.all()
            },
            {
                'filter_id': f'{filter_pre_mm}dedicatee',
                'filter_name': 'Dedicatee',
                'filter_options': models.Agent.objects.filter(roles__name__iexact='dedicatee').distinct()
            },
        ]

        return context


def export_csv(request):
    """
    Returns a CSV file containing all OratorInPassage objects
    """

    # Define data
    queryset = models.OratorInPassage.objects.all()
    # Prepare response
    response = HttpResponse(content_type='text/csv')
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="data_export_{now}.csv"'
    # Setup the CSV Writer
    writer = csv.writer(response)

    if queryset is not None:
        # Write header row to CSV file
        field_names = [field.name for field in queryset.model._meta.fields]
        writer.writerow(field_names)
        # Write the data rows to CSV file
        for obj in queryset:
            # Extract the value for each field on the current object
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)

    return response
