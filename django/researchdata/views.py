from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.db.models.functions import Concat, Lower
from django.db.models import CharField, Value, Q, Count, TextField
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


def details_section_visibility(details_list):
    """
    Show the detail section if at least one value exists
    """
    for section in details_list:
        if len(section):
            for detail in section:
                if 'value' in detail and detail['value']:
                    section[0]['section_visible'] = True
                    break
    return details_list


def html_details_list_items(object_list):
    """
    Return a HTML string of a list of objects (i.e. a queryset) for use in the 'Details' tab of an item page.
    E.g. showing ManyToMany and reverse FK objects

    The model of the object_list must have a dynamic property 'html_details_list_item_text'
    """

    # Multiple objects
    if len(object_list) > 1:
        list_items = '</li><li>'.join(str(item.html_details_list_item_text) for item in object_list)
        return f'<ul><li>{list_items}</li></ul>'
    # 1 object
    elif len(object_list) == 1:
        return str(object_list[0].html_details_list_item_text)
    # No objects (will be ignored)
    else:
        return ""


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



def filter_options_limit_to_published_related_people(objects):
    """
    Only include filter options in select lists if selecting them will show items
    E.g. if there are published people that belong to each filter
    """
    return objects.annotate(
        published_people_count=Count('related_person', filter=Q(related_person__admin_published=True))
    ).filter(published_people_count__gt=0)


class TextDetailView(DetailView):
    """
    Class-based view for text detail template
    """
    template_name = 'researchdata/detail.html'
    queryset = models.Text.objects.filter(published=True)
        # .prefetch_related('person', 'letterperson_set',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Admin URL
        context['admin_url'] = reverse('admin:researchdata_text_change', args=[self.object.id])

        # Details
        # context['details'] = details_section_visibility([
        #     [
        #         {'label': 'First Name', 'value': self.object.first_name},
        #         {'label': 'Middle Name', 'value': self.object.middle_name},
        #         {'label': 'Last Name', 'value': self.object.last_name},
        #         {'label': 'Alternative Spelling of Name Number', 'value': self.object.alternative_spelling_of_name},
        #         {'label': 'Alternative Names', 'value': self.object.alternative_names},
        #         {'label': 'Year of Birth', 'value': self.object.year_of_birth},
        #         {'label': 'Year of Death', 'value': self.object.year_of_death},
        #         {'label': 'Years Active (from)', 'value': self.object.year_of_birth},
        #         {'label': 'Years Active (to)', 'value': self.object.year_of_death},
        #         {'label': 'Gender', 'value': self.object.gender},
        #         {'label': 'Title', 'value': html_details_list_items(self.object.title.all())},
        #         {'label': 'Marital Status', 'value': html_details_list_items(self.object.marital_status.all())},
        #         {'label': 'Religion', 'value': html_details_list_items(self.object.religion.all())},
        #         {'label': 'Rank', 'value': html_details_list_items(self.object.rank.all())},
        #         {'label': 'Occupation', 'value': self.object.occupation},
        #     ],
        # ])

        return context


class TextListView(ListView):
    """
    Class-based view for text list template
    """
    template_name = 'researchdata/list.html'
    model = models.Text
    paginate_by = 60

    # def get_queryset(self):
    #     # Start with all published objects
    #     queryset = self.model.objects.filter(admin_published=True)
    #     # Add annotations for improved searching
    #     # name_first_last
    #     queryset = queryset.annotate(
    #         name_first_last=Concat('first_name', Value(' '), 'last_name',
    #                                output_field=CharField()))
    #     # name_full
    #     queryset = queryset.annotate(
    #         name_full=Concat('first_name', Value(' '), 'middle_name', Value(' '), 'last_name',
    #                          output_field=CharField()))

    #     # Search
    #     search = self.request.GET.get('search', '')
    #     if search != '':
    #         queryset = queryset.filter(
    #             Q(first_name__icontains=search) |
    #             Q(middle_name__icontains=search) |
    #             Q(last_name__icontains=search) |
    #             Q(alternative_spelling_of_name__icontains=search) |
    #             Q(alternative_names__icontains=search) |
    #             Q(year_of_birth__icontains=search) |
    #             Q(year_of_death__icontains=search) |
    #             Q(year_of_birth__icontains=search) |
    #             Q(year_of_death__icontains=search) |
    #             Q(occupation__icontains=search) |

    #             # Annotation fields
    #             Q(name_first_last__icontains=search) |
    #             Q(name_full__icontains=search) |

    #             # FK
    #             Q(gender__name__icontains=search) |

    #             # M2M
    #             Q(title__name__icontains=search) |
    #             Q(marital_status__name__icontains=search) |
    #             Q(religion__name__icontains=search) |
    #             Q(rank__name__icontains=search) |

    #             # M2M via LetterPerson
    #             Q(letterperson__body_part__name__icontains=search) |
    #             Q(letterperson__bodily_activity__name__icontains=search) |
    #             Q(letterperson__appearance__name__icontains=search) |
    #             Q(letterperson__emotion__name__icontains=search) |
    #             Q(letterperson__sensation__name__icontains=search) |
    #             # Following are commented out for performance reasons (too many = too slow)
    #             # Q(letterperson__condition_specific_state__name__icontains=search) |
    #             # Q(letterperson__immaterial__name__icontains=search) |
    #             # Q(letterperson__condition_specific_life_stage__name__icontains=search) |
    #             # Q(letterperson__condition_generalized_state__name__icontains=search) |
    #             # Q(letterperson__treatment__name__icontains=search) |
    #             # Q(letterperson__roles__name__icontains=search) |
    #             # Q(letterperson__context__name__icontains=search) |
    #             # Q(letterperson__state__name__icontains=search) |

    #             # M2M via LetterPerson > Letter
    #             Q(letterperson__letter__letter_type__name__icontains=search) |
    #             Q(letterperson__letter__commentary__name__icontains=search) |
    #             Q(letterperson__letter__location__name__icontains=search)
    #         )
    #     # Filters
    #     queryset = filter(self.request, queryset)
    #     # Sort
    #     queryset = sort(self.request, queryset, 'first_name')
    #     # Return result, showing only distinct
    #     return queryset.distinct()\
    #         .prefetch_related('letterperson_set').select_related('gender')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     # Options: Filters
    #     context['filters'] = [
    #         {
    #             'filter_id': f'{filter_pre_mm}gender',
    #             'filter_name': 'Gender',
    #             'filter_options': models.SlPersonGender.objects
    #         },
    #         {
    #             'filter_id': f'{filter_pre_mm}marital_status',
    #             'filter_name': 'Marital Status',
    #             'filter_options': filter_options_limit_to_published_related_people(
    #                 models.SlPersonMaritalStatus.objects
    #             )
    #         },
    #         {
    #             'filter_id': f'{filter_pre_mm}religion',
    #             'filter_name': 'Religion',
    #             'filter_options': filter_options_limit_to_published_related_people(models.SlPersonReligion.objects)
    #         },
    #         {
    #             'filter_id': f'{filter_pre_mm}rank',
    #             'filter_name': 'Rank',
    #             'filter_options': filter_options_limit_to_published_related_people(models.SlPersonRank.objects)
    #         },
    #         {
    #             'filter_id': f'{filter_pre_gt}year_of_birth',
    #             'filter_classes': filter_pre_gt,
    #             'filter_name': 'Year of Birth (from)',
    #             'filter_options': models.Person.objects.filter(year_of_birth__gt=1000).exclude(year_of_birth__isnull=True).distinct().order_by('year_of_birth').values_list('year_of_birth', flat=True),  # NOQA
    #             'valueSameAsText': True
    #         },
    #         {
    #             'filter_id': f'{filter_pre_lt}year_of_birth',
    #             'filter_classes': filter_pre_lt,
    #             'filter_name': 'Year of Birth (to)',
    #             'filter_options': models.Person.objects.filter(year_of_birth__gt=1000).exclude(year_of_birth__isnull=True).distinct().order_by('year_of_birth').values_list('year_of_birth', flat=True),  # NOQA
    #             'valueSameAsText': True
    #         },
    #         {
    #             'filter_id': f'{filter_pre_gt}year_of_death',
    #             'filter_classes': filter_pre_gt,
    #             'filter_name': 'Year of Death (from)',
    #             'filter_options': models.Person.objects.filter(year_of_death__gt=1000).exclude(year_of_death__isnull=True).distinct().order_by('year_of_death').values_list('year_of_death', flat=True),  # NOQA
    #             'valueSameAsText': True
    #         },
    #         {
    #             'filter_id': f'{filter_pre_lt}year_of_death',
    #             'filter_classes': filter_pre_lt,
    #             'filter_name': 'Year of Death (to)',
    #             'filter_options': models.Person.objects.filter(year_of_death__gt=1000).exclude(year_of_death__isnull=True).distinct().order_by('year_of_death').values_list('year_of_death', flat=True),  # NOQA
    #             'valueSameAsText': True
    #         }
    #     ]

    #     return context



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
