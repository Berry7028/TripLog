"""
Service functions for spot interactions such as viewing and favoriting.

This module manages logic for logging spot views, tracking user engagement
duration, checking favorite status, and toggling favorites.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Union

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import F, QuerySet
from django.utils import timezone

from ..models import Spot, SpotView, UserProfile, UserSpotInteraction

logger = logging.getLogger(__name__)


def log_spot_view(spot: Spot, user: Union[AbstractBaseUser, AnonymousUser]) -> None:
    """
    Records a spot view event and updates the user's view count.

    Creates a SpotView log entry for every view. If the user is authenticated,
    it also updates or creates a UserSpotInteraction record to track how many
    times the user has viewed the spot.

    Args:
        spot (Spot): The spot being viewed.
        user (Union[AbstractBaseUser, AnonymousUser]): The user viewing the spot.
    """

    try:
        SpotView.objects.create(spot=spot)
    except Exception:  # pragma: no cover - logging failure is not critical
        logger.exception("Failed to store SpotView log", extra={"spot_id": spot.id})

    if not getattr(user, "is_authenticated", False):
        return

    try:
        interaction, created = UserSpotInteraction.objects.get_or_create(
            user=user,
            spot=spot,
            defaults={"view_count": 1},
        )
        if not created:
            UserSpotInteraction.objects.filter(pk=interaction.pk).update(
                view_count=F("view_count") + 1,
                last_viewed_at=timezone.now(),
            )
    except Exception:  # pragma: no cover - failure to record analytics is ignored
        logger.exception(
            "Failed to update user spot interaction",
            extra={"spot_id": spot.id, "user_id": getattr(user, "id", None)},
        )


def update_view_duration(spot: Spot, user: Union[AbstractBaseUser, AnonymousUser], duration: timedelta) -> None:
    """
    Updates the total duration a user has spent viewing a spot.

    If the user is authenticated, this adds the specified duration to their
    existing total view duration for the spot.

    Args:
        spot (Spot): The spot being viewed.
        user (Union[AbstractBaseUser, AnonymousUser]): The user viewing the spot.
        duration (timedelta): The amount of time spent on the spot page.
    """

    if not getattr(user, "is_authenticated", False):
        return

    normalized_duration = duration if duration > timedelta(0) else timedelta(0)

    try:
        interaction, created = UserSpotInteraction.objects.get_or_create(
            user=user,
            spot=spot,
            defaults={
                "view_count": 1,
                "total_view_duration": normalized_duration,
            },
        )
        if created or normalized_duration == timedelta(0):
            return

        UserSpotInteraction.objects.filter(pk=interaction.pk).update(
            total_view_duration=F("total_view_duration") + normalized_duration,
            last_viewed_at=timezone.now(),
        )
    except Exception:  # pragma: no cover - failure to record analytics is ignored
        logger.exception(
            "Failed to update view duration",
            extra={"spot_id": spot.id, "user_id": getattr(user, "id", None)},
        )


def is_favorite_spot(spot: Spot, user: Union[AbstractBaseUser, AnonymousUser]) -> bool:
    """
    Checks if the specified spot is in the user's list of favorites.

    Args:
        spot (Spot): The spot to check.
        user (Union[AbstractBaseUser, AnonymousUser]): The user to check for.

    Returns:
        bool: True if the spot is in the user's favorites, False otherwise.
              Returns False for anonymous users.
    """

    if isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False

    return UserProfile.objects.filter(user=user, favorite_spots=spot).exists()


def toggle_favorite_spot(spot: Spot, user: Union[AbstractBaseUser, AnonymousUser]) -> bool:
    """
    Toggles the favorite status of a spot for the given user.

    If the spot is already a favorite, it is removed. If not, it is added.

    Args:
        spot (Spot): The spot to toggle.
        user (Union[AbstractBaseUser, AnonymousUser]): The authenticated user.

    Returns:
        bool: True if the spot is now a favorite, False if it was removed.

    Raises:
        ValueError: If the user is not authenticated.
    """

    if not getattr(user, "is_authenticated", False):
        raise ValueError("toggle_favorite_spot requires an authenticated user")

    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.favorite_spots.filter(pk=spot.pk).exists():
        profile.favorite_spots.remove(spot)
        return False

    profile.favorite_spots.add(spot)
    return True


def fetch_related_spots(spot: Spot, limit: int = 5) -> QuerySet[Spot]:
    """
    Fetches related spots, defined as other spots posted by the same user.

    Args:
        spot (Spot): The reference spot.
        limit (int, optional): The maximum number of related spots to return.
            Defaults to 5.

    Returns:
        QuerySet[Spot]: A queryset of related Spot objects, excluding the reference spot,
        ordered by creation date (descending).
    """

    return (
        spot.created_by.spot_set.exclude(id=spot.id)
        .select_related("created_by")
        .prefetch_related("tags")
        .order_by("-created_at")[:limit]
    )
