import logging
import os

from django.db import transaction

from parkings.models import PaymentZone

from .geojson_importer import GeoJsonImporter

logger = logging.getLogger(__name__)

mydir = os.path.dirname(__file__)


class PaymentZoneImporter(GeoJsonImporter):
    """
    Imports paymentzones data
    """

    def import_payment_zones(self, geojson_file_path):
        payment_zone_dicts = self.read_and_parse(geojson_file_path)
        count = self._save_payment_zones(payment_zone_dicts)
        logger.info('Created or updated {} payment zones'.format(count))

    @transaction.atomic
    def _save_payment_zones(self, payment_zone_dicts):
        logger.info('Saving payment zones.')
        count = 0
        payment_zone_ids = []
        for payment_dict in payment_zone_dicts:
            payment_zone, _ = PaymentZone.objects.update_or_create(
                number=payment_dict['number'],
                defaults=payment_dict)
            payment_zone_ids.append(payment_zone.pk)
            count += 1
        PaymentZone.objects.exclude(pk__in=payment_zone_ids).delete()
        return count

    def _parse_member(self, member):
        name = member['properties']['name']
        number = member['properties']['number']
        geom = self.get_polygons(member['geometry'])

        return {
            'name': name,
            'number': number,
            'geom': geom,
        }
