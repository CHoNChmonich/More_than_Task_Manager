from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline
from django.db.models import Q

from tasks.models import Task


def q_search(query):
    if query.isdigit() and len(query) <= 5:
        return Task.objects.filter(id=int(query))
    vector = SearchVector('title', 'description')
    query = SearchQuery(query)
    result = Task.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0).order_by('-rank')
    result = result.annotate(
        headline=SearchHeadline('title', query,
                                start_sel='<span style="background-color: yellow">',
                                stop_sel='</span>'))
    result = result.annotate(
        bodyline=SearchHeadline('description', query,
                                start_sel='<span style="background-color: yellow">',
                                stop_sel='</span>'))
    return result
