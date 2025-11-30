from django.core.management.base import BaseCommand
from spots.models import Spot
from spots.services.image_lookup import fetch_spot_image

class Command(BaseCommand):
    help = "Backfill spot images using external image lookup service."

    def handle(self, *args, **options):
        queryset = Spot.objects.filter(image="", image_url="")
        for spot in queryset.iterator():
            result = fetch_spot_image(
                title=spot.title,
                description=spot.description,
                latitude=spot.latitude,
                longitude=spot.longitude,
            )
            if result:
                spot.image_url = result.url
                spot.save(update_fields=["image_url"])
                self.stdout.write(self.style.SUCCESS(f"Filled {spot.pk}: {spot.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Failed {spot.pk}: {spot.title}"))
        self.stdout.write(self.style.SUCCESS("全てのスポット画像のバックフィルが完了しました。"))