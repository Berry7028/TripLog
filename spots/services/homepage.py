"""
Logic for fetching and sorting spots for the homepage.

This module handles the retrieval of spot data, applying search filters,
and formatting the results for display on the home screen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import Q, QuerySet

from ..models import Spot

ALLOWED_SORT_MODES = {"recent"}
DEFAULT_SORT_MODE = "recent"


@dataclass
class HomepageSpotsResult:
    """
    Encapsulates the result of fetching spots for the homepage.

    Attributes:
        spots (List[Spot]): A list of Spot objects to be displayed.
        search_query (str): The search query string used to filter the spots.
        sort_mode (str): The sorting mode applied to the results.
    """

    spots: List[Spot]
    search_query: str
    sort_mode: str


def fetch_homepage_spots(
    *,
    user: Union[AbstractBaseUser, AnonymousUser],
    search_query: str = "",
    sort_mode: str = DEFAULT_SORT_MODE,
) -> HomepageSpotsResult:
    """
    Fetches a list of spots and metadata for the homepage.

    Retrieves spots from the database, optionally filtering by a search query.
    Currently, it supports sorting by 'recent' (default).

    Args:
        user (Union[AbstractBaseUser, AnonymousUser]): The user requesting the page.
            (Currently unused in logic but reserved for future personalization).
        search_query (str, optional): A keyword to filter spots by title, description,
            address, or tags. Defaults to "".
        sort_mode (str, optional): The sorting criteria. Defaults to 'recent'.
            If an invalid mode is provided, it falls back to default.

    Returns:
        HomepageSpotsResult: A data object containing the list of spots,
        the cleaned search query, and the applied sort mode.
    """

    normalized_query = (search_query or "").strip()
    normalized_sort = sort_mode if sort_mode in ALLOWED_SORT_MODES else DEFAULT_SORT_MODE

    spots_qs = _base_queryset()
    if normalized_query:
        spots_qs = _apply_search_filter(spots_qs, normalized_query)

    spots_list = list(spots_qs)

    return HomepageSpotsResult(
        spots=spots_list,
        search_query=normalized_query,
        sort_mode=normalized_sort,
    )


def _base_queryset() -> QuerySet[Spot]:
    """
    Constructs the base QuerySet for fetching spots.

    Selects related user data and prefetches reviews and tags to optimize
    database access.

    Returns:
        QuerySet[Spot]: The base queryset for Spot objects.
    """
    return (
        Spot.objects.all()
        .select_related("created_by")
        .prefetch_related("reviews", "tags")
    )


def _apply_search_filter(queryset: QuerySet[Spot], search_query: str) -> QuerySet[Spot]:
    """
    Applies a search filter to the spot queryset.

    Filters spots that contain the search query in their title, description,
    address, or associated tag names.

    Args:
        queryset (QuerySet[Spot]): The original queryset of spots.
        search_query (str): The text to search for.

    Returns:
        QuerySet[Spot]: The filtered queryset.
    """
    return queryset.filter(
        Q(title__icontains=search_query)
        | Q(description__icontains=search_query)
        | Q(address__icontains=search_query)
        | Q(tags__name__icontains=search_query)
    ).distinct()
