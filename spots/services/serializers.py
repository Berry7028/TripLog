"""
Serializer utilities for converting Spot models to dictionary formats.

These functions are used to prepare Spot data for JSON responses in views and APIs.
"""

from __future__ import annotations

from typing import Dict, Optional

from ..models import Spot


def serialize_spot_summary(spot: Spot) -> Dict[str, object]:
    """
    Serializes a Spot object into a dictionary summary for lists or API responses.

    Includes full details such as description, coordinates, image URL, creator,
    creation date, and tags.

    Args:
        spot (Spot): The Spot instance to serialize.

    Returns:
        Dict[str, object]: A dictionary containing the spot's summary data.
    """

    image_url = _resolve_image_url(spot)
    return {
        "id": spot.id,
        "title": spot.title,
        "description": spot.description,
        "latitude": spot.latitude,
        "longitude": spot.longitude,
        "address": spot.address,
        "image": image_url,
        "created_by": spot.created_by.username,
        "created_at": spot.created_at.isoformat() if spot.created_at else None,
        "tags": [tag.name for tag in spot.tags.all()],
    }


def serialize_spot_brief(spot: Spot) -> Dict[str, object]:
    """
    Serializes a Spot object into a brief dictionary for search suggestions.

    Includes only minimal details needed for identification and location:
    ID, title, address, and coordinates.

    Args:
        spot (Spot): The Spot instance to serialize.

    Returns:
        Dict[str, object]: A dictionary containing brief spot data.
    """

    return {
        "id": spot.id,
        "title": spot.title,
        "address": spot.address,
        "latitude": spot.latitude,
        "longitude": spot.longitude,
    }


def _resolve_image_url(spot: Spot) -> Optional[str]:
    """
    Resolves the image URL for a spot.

    Prioritizes the uploaded image file URL. If that fails or doesn't exist,
    falls back to the external image URL string.

    Args:
        spot (Spot): The Spot instance.

    Returns:
        Optional[str]: The resolved URL string, or None if no image is available.
    """
    if spot.image:
        try:
            return spot.image.url
        except Exception:
            pass
    return spot.image_url or None
