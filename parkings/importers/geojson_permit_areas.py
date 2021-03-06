import logging
import os

from django.db import transaction

from parkings.models import PermitArea

from .geojson_importer import GeoJsonImporter

logger = logging.getLogger(__name__)
mydir = os.path.dirname(__file__)


class PermitAreaImporter(GeoJsonImporter):
    """
    Imports permit area data
    """

    def import_permit_areas(self, geojson_file_path):
        permit_area_dicts = self.read_and_parse(geojson_file_path)
        count = self._save_permit_areas(permit_area_dicts)
        logger.info('Created or updated {} permit areas'.format(count))

    @transaction.atomic
    def _save_permit_areas(self, permit_areas_dict):
        logger.info('Saving permit areas.')
        count = 0
        permit_area_ids = []
        for area_dict in permit_areas_dict:
            permit_area, _ = PermitArea.objects.update_or_create(
                identifier=area_dict['identifier'],
                defaults=area_dict)
            permit_area_ids.append(permit_area.pk)
            count += 1
        PermitArea.objects.exclude(pk__in=permit_area_ids).delete()
        return count

    def _parse_member(self, member):
        identifier = member['properties']['identifier']
        name = member['properties']['name']
        geom = self.get_polygons(member['geometry'])

        return {
            'name': name,
            'identifier': identifier,
            'geom': geom,
        }
