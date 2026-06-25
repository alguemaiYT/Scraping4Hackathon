"""Stub para futura integração com APIs universitárias REST."""

from collector.base import AcademicDataSource, CollectedEvent


class UniversityApiSource(AcademicDataSource):
    """Placeholder para APIs REST de sistemas acadêmicos.

    Substitua OpenMeteoSource em collector/main.py quando a API estiver disponível.
    """

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self._base_url = base_url
        self._api_key = api_key

    @property
    def source_name(self) -> str:
        return "API Universitária"

    @property
    def source_type(self) -> str:
        return "api"

    async def fetch_current_events(
        self, latitude: float, longitude: float, location_name: str
    ) -> CollectedEvent:
        raise NotImplementedError(
            "Implemente a integração com a API universitária alvo."
        )
