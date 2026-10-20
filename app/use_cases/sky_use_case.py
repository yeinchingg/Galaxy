from app.domain.sky_domain import CELESTIAL_CATALOG


class GetSkyCatalogUseCase:
    def execute(self):
        return CELESTIAL_CATALOG
