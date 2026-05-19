# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — Cattle Control Revisão 0"""

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("app", "app"),
        ("../frontend/dist", "frontend_dist"),
    ],
    hiddenimports=[
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "sqlalchemy.dialects.sqlite",
        "pydantic_settings",
        "app.models",
        "app.models.matriz",
        "app.models.cria",
        "app.models.exame_toque",
        "app.models.toque_matriz",
        "app.models.reprodutor",
        "app.models.comprador",
        "app.models.desempenho",
        "anthropic",
        "httpx",
        "httptools",
        "websockets",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "notebook", "IPython"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CattleControl",
    debug=False,
    strip=False,
    upx=True,
    console=True,   # console visível: usuário sabe que o servidor está rodando
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CattleControl",
)
