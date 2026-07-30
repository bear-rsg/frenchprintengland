from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.db.models.functions import Lower
from django.db.models import CharField, Q, Count, TextField
from django.urls import reverse
from datetime import datetime
from openpyxl import Workbook
from . import models
import io


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
            {'label': 'ESTC', 'value': self.object.estc},
            {'label': 'STC', 'value': self.object.stc},
            {'label': 'USTC', 'value': self.object.ustc},
            {'label': 'Author', 'value': self.object.author},

            # Publication Information
            {'section_header': 'Publication Information'},
            {'label': 'Translators', 'value': queryset_as_str(self.object.translators.all())},
            {'label': 'Other contributors', 'value': queryset_as_str(self.object.other_contributors.all())},
            {'label': 'Imprint', 'value': self.object.imprint},
            {'label': 'Place of publication', 'value': self.object.place_of_publication},
            {'label': 'False imprint', 'value': self.object.false_imprint},
            {'label': 'Publishers', 'value': queryset_as_str(self.object.publishers.all())},
            {'label': 'Year of publication', 'value': self.object.year_of_publication},
            {'label': 'Associated date', 'value': self.object.associated_date},
            {'label': 'Associated location', 'value': queryset_as_str(self.object.associated_locations.all())},
            {'label': 'Lost book', 'value': self.object.lost_book},

            # Properties
            {'section_header': 'Properties'},
            {'label': 'Languages', 'value': queryset_as_str(self.object.languages.all())},
            {'label': 'Number of languages', 'value': self.object.number_of_languages},
            {'label': 'Type', 'value': self.object.text_type},
            {'label': 'Format_of_publication', 'value': self.object.format_of_publication},
            {'label': 'Number_of_issues', 'value': self.object.number_of_issues},
            {'label': 'Pagination', 'value': self.object.pagination},
            {'label': 'Number of pages containing French', 'value': self.object.number_of_pages_containing_french},
            {'label': 'Textual features', 'value': queryset_as_str(self.object.textual_features.all())},
            {'label': 'Dedicatees', 'value': queryset_as_str(self.object.dedicatees.all())},

            # Bibliographical Information
            {'section_header': 'Bibliographical Information'},
            {'label': 'FB', 'value': self.object.fb},
            {'label': 'RCCC', 'value': self.object.rccc},
            {'label': 'Nelson and Seccombe', 'value': self.object.nelson_and_seccombe},
            {'label': "Stationers' register ", 'value': self.object.nelson_and_seccombe},
            {'label': 'PLRE', 'value': self.object.plre},
            {'label': 'Owners', 'value': queryset_as_str(self.object.owners.all())},
            {'label': 'Full text image', 'value': self.object.full_text_image},
            {'label': 'Full text transcription', 'value': self.object.full_text_transcription},
            {'label': 'Subjects', 'value': queryset_as_str(self.object.subjects.all())},
            {'label': 'Relationships', 'value': queryset_as_str(self.object.relationships.all())},
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
                Q(estc__icontains=search) |
                Q(stc__icontains=search) |
                Q(ustc__icontains=search) |
                Q(title__icontains=search) |
                Q(imprint__icontains=search) |
                Q(year_of_publication__icontains=search) |
                Q(associated_date__icontains=search) |
                Q(pagination__icontains=search) |
                Q(fb__icontains=search) |
                Q(rccc__icontains=search) |
                Q(nelson_and_seccombe__icontains=search) |
                Q(stationers_register__icontains=search) |
                Q(plre__icontains=search) |
                Q(full_text_image__icontains=search) |
                Q(full_text_transcription__icontains=search) |

                # FK
                Q(author__name__icontains=search) |
                Q(author__gender__name__iexact=search) |
                Q(place_of_publication__name__icontains=search) |
                Q(text_type__name__icontains=search) |
                Q(format_of_publication__name__icontains=search) |

                # M2M
                Q(translators__name__icontains=search) |
                Q(translators__gender__name__iexact=search) |
                Q(other_contributors__name__icontains=search) |
                Q(publishers__name__icontains=search) |
                Q(associated_locations__name__icontains=search) |
                Q(languages__name__icontains=search) |
                Q(textual_features__name__icontains=search) |
                Q(dedicatees__name__icontains=search) |
                Q(dedicatees__gender__name__iexact=search) |
                Q(owners__name__icontains=search) |
                Q(subjects__name__icontains=search) |
                Q(relationships__name__icontains=search)
            )
        # Filters
        queryset = filter(self.request, queryset)
        # Sort
        queryset = sort(self.request, queryset, 'title')
        # Return result, showing only distinct
        return queryset.distinct()\
            .prefetch_related(
                'translators',
                'other_contributors',
                'publishers',
                'associated_locations',
                'languages',
                'textual_features',
                'dedicatees',
                'owners',
                'subjects',
                'relationships',
            )\
            .select_related(
                'author',
                'place_of_publication',
                'text_type',
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
                'filter_id': f'{filter_pre_fk}translators',
                'filter_name': 'Translators',
                'filter_options': models.Agent.objects.filter(roles__name__iexact='translator').distinct()
            },
            {
                'filter_id': f'{filter_pre_fk}place_of_publication',
                'filter_name': 'Place of Publication',
                'filter_options': models.Place.objects.all()
            },
            {
                'filter_id': f'{filter_pre_fk}text_type',
                'filter_name': 'Type',
                'filter_options': models.TextType.objects.all()
            },
            {
                'filter_id': f'{filter_pre_fk}format_of_publication',
                'filter_name': 'Format of Publication',
                'filter_options': models.FormatOfPublication.objects.all()
            },
            {
                'filter_id': f'{filter_pre_mm}publishers',
                'filter_name': 'Publishers',
                'filter_options': models.Agent.objects.filter(roles__name__iexact='publisher').distinct()
            },
            {
                'filter_id': f'{filter_pre_mm}languages',
                'filter_name': 'Languages',
                'filter_options': models.Language.objects.all()
            },
            {
                'filter_id': f'{filter_pre_mm}dedicatee',
                'filter_name': 'Dedicatees',
                'filter_options': models.Agent.objects.filter(roles__name__iexact='dedicatee').distinct()
            },
        ]

        return context


def export_excel(request):
    """
    Returns a Excel file containing data from all specified models
    """

    wb = Workbook()
    wb.remove(wb.active)
    for m in [
        models.PlaceType,
        models.Place,
        models.Text,
        models.Agent,
        models.AgentRole,
        models.Gender,
        models.Language,
        models.TextType,
        models.TextualFeatures,
        models.FormatOfPublication,
        models.Subject,
        models.Relationships,
    ]:
        ws = wb.create_sheet(title=str(m._meta.verbose_name_plural).title()[:31])
        fields = [f.name for f in m._meta.fields]
        m2m = [f.name for f in m._meta.many_to_many]
        ws.append(fields + m2m)
        for obj in m.objects.prefetch_related(*m2m):
            row = [
                v.replace(tzinfo=None) if isinstance(v, datetime)
                else v if isinstance(v, (int, float, bool, type(None)))
                else str(v) for v in (getattr(obj, f) for f in fields)
            ] + [", ".join(str(i) for i in getattr(obj, f).all()) for f in m2m]
            ws.append(row)
    b = io.BytesIO()
    wb.save(b)
    ts = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
    r = HttpResponse(b.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    r['Content-Disposition'] = f'attachment; filename="frenchprintengland-dataexport-{ts}.xlsx"'
    return r
