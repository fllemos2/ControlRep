from fastapi import APIRouter

from app.api.v1.endpoints import matrizes, reprodutores, compradores, crias, exames_toque, toques_matrizes, chat, sync, parcerias, dashboard, relatorios

api_router = APIRouter()

api_router.include_router(matrizes.router, prefix="/matrizes", tags=["Matrizes"])
api_router.include_router(reprodutores.router, prefix="/reprodutores", tags=["Reprodutores"])
api_router.include_router(compradores.router, prefix="/compradores", tags=["Compradores"])
api_router.include_router(crias.router, prefix="/crias", tags=["Crias"])
api_router.include_router(exames_toque.router, prefix="/exames-toque", tags=["Exames de Toque"])
api_router.include_router(toques_matrizes.router, prefix="/toques-matrizes", tags=["Toques Matrizes"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(sync.router, prefix="/sync", tags=["Sync"])
api_router.include_router(parcerias.router, prefix="/parcerias", tags=["Parcerias"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(relatorios.router, prefix="/relatorios", tags=["Relatorios"])
