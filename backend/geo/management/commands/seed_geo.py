import csv
import io
import logging
from urllib.request import urlopen

from django.core.management.base import BaseCommand
from django.db import transaction

from geo.models import Country, Airport

logger = logging.getLogger(__name__)

OURAIRPORTS_AIRPORTS_CSV = "https://ourairports.com/data/airports.csv"
OURAIRPORTS_COUNTRIES_CSV = "https://ourairports.com/data/countries.csv"


class Command(BaseCommand):
    help = "Seed Countries and Airports from OurAirports public datasets"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit-airports",
            type=int,
            default=0,
            help="Limit airports inserted (0 = no limit).",
        )
        parser.add_argument(
            "--only-iata",
            action="store_true",
            help="Insert only airports that have an IATA code.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write to DB, only print stats.",
        )

    def handle(self, *args, **options):
        limit = options["limit_airports"]
        only_iata = options["only_iata"]
        dry_run = options["dry_run"]

        self.stdout.write("Downloading countries.csv...")
        countries_rows = self._download_csv(OURAIRPORTS_COUNTRIES_CSV)

        # OurAirports: code = ISO2, name = country name
        countries_to_upsert = []
        for r in countries_rows:
            iso2 = (r.get("code") or "").strip().upper()
            name = (r.get("name") or "").strip()
            if len(iso2) != 2 or not name:
                continue
            countries_to_upsert.append((iso2, name))

        self.stdout.write(f"Countries parsed: {len(countries_to_upsert)}")

        self.stdout.write("Downloading airports.csv...")
        airports_rows = self._download_csv(OURAIRPORTS_AIRPORTS_CSV)

        airports_to_create = []
        seen = 0

        # Preload countries map (iso2 -> Country)
        # We'll create countries first.
        if dry_run:
            self.stdout.write("Dry-run: skipping DB writes.")
            self.stdout.write(f"Would upsert ~{len(countries_to_upsert)} countries.")
            self.stdout.write(
                f"Would parse airports and insert (limit={limit}, only_iata={only_iata})."
            )
            return

        with transaction.atomic():
            for iso2, name in countries_to_upsert:
                # Use country name as the natural key so pre-existing rows
                # (created before iso2 existed) are upgraded instead of duplicated.
                Country.objects.update_or_create(name=name, defaults={"iso2": iso2})

            country_map = {c.iso2: c for c in Country.objects.all().only("id", "iso2")}
            existing_keys = set(
                Airport.objects.values_list(
                    "country_id", "iata_code", "icao_code", "name", "city"
                )
            )
            skipped_duplicates = 0

            for r in airports_rows:
                if limit and seen >= limit:
                    break

                iso2 = (r.get("iso_country") or "").strip().upper()
                if iso2 not in country_map:
                    continue

                iata = (r.get("iata_code") or "").strip().upper()
                icao = (
                    (r.get("gps_code") or "").strip().upper()
                )  # often ICAO in OurAirports
                name = (r.get("name") or "").strip()
                city = (r.get("municipality") or "").strip()

                if not name:
                    continue
                if only_iata and not iata:
                    continue

                airport_key = (country_map[iso2].id, iata, icao, name, city)
                if airport_key in existing_keys:
                    skipped_duplicates += 1
                    continue

                airports_to_create.append(
                    Airport(
                        iata_code=iata,
                        icao_code=icao,
                        name=name,
                        city=city,
                        country=country_map[iso2],
                    )
                )
                existing_keys.add(airport_key)
                seen += 1

            Airport.objects.bulk_create(airports_to_create, batch_size=2000)

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete: "
                f"countries={len(countries_to_upsert)}, "
                f"airports_inserted={len(airports_to_create)}, "
                f"duplicates_skipped={skipped_duplicates}"
            )
        )

    def _download_csv(self, url: str):
        with urlopen(url) as resp:
            data = resp.read().decode("utf-8", errors="replace")
        f = io.StringIO(data)
        reader = csv.DictReader(f)
        return list(reader)
