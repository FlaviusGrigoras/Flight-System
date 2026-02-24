from django.db.models import Q

from geo.models import Airport


class AirportRepository:
    def search(
        self,
        *,
        country_id=None,
        country_iso2=None,
        query=None,
        limit=None,
    ):
        airports = Airport.objects.select_related("country").all()

        if country_id is not None:
            airports = airports.filter(country_id=country_id)

        if country_iso2 is not None:
            airports = airports.filter(country__iso2=country_iso2)

        if query:
            airports = airports.filter(
                Q(name__icontains=query)
                | Q(city__icontains=query)
                | Q(iata_code__icontains=query)
                | Q(icao_code__icontains=query)
            )

        if limit is not None:
            airports = airports[:limit]

        return airports
