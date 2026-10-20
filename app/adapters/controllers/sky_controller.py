from fastapi import APIRouter
from app.use_cases.sky_use_case import GetSkyCatalogUseCase

router = APIRouter(prefix="/sky", tags=["Sky Observatory"])

sky_use_case = GetSkyCatalogUseCase()


@router.get("/catalog")
async def get_celestial_catalog():
    return {"catalog": sky_use_case.execute()}
