"""
Serviço IPCA — busca série mensal no Banco Central do Brasil (série 433)
e calcula fator de correção monetária entre duas datas.
"""
import json
import time
import urllib.request
from datetime import date
from typing import Dict, Optional, Tuple

BCB_URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
    "?formato=json&dataInicial=01/01/2008"
)

_cache_index: Optional[Dict[Tuple[int, int], float]] = None
_cache_ts: float = 0.0
_CACHE_TTL = 86400  # 24 h


def _fetch_series() -> list:
    try:
        req = urllib.request.Request(BCB_URL, headers={"User-Agent": "CattleControl/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[IPCA] falha ao buscar série BCB: {e}")
        return []


def _build_index(series: list) -> Dict[Tuple[int, int], float]:
    """Índice acumulado: índice[ano, mês] = produto acumulado de (1 + variação)."""
    index: Dict[Tuple[int, int], float] = {}
    cum = 1.0
    for item in series:
        try:
            dd, mm, yy = item["data"].split("/")
            var = float(item["valor"])
        except (KeyError, ValueError):
            continue
        cum *= 1.0 + var / 100.0
        index[(int(yy), int(mm))] = cum
    return index


def _get_index() -> Dict[Tuple[int, int], float]:
    global _cache_index, _cache_ts
    if _cache_index is not None and (time.time() - _cache_ts) < _CACHE_TTL:
        return _cache_index
    series = _fetch_series()
    _cache_index = _build_index(series) if series else {}
    _cache_ts = time.time()
    return _cache_index


def _nearest(index: dict, ym: Tuple[int, int]) -> Optional[float]:
    if ym in index:
        return index[ym]
    keys = sorted(index.keys())
    before = [k for k in keys if k <= ym]
    return index[before[-1]] if before else None


def fator_correcao(data_base: date, data_fim: Optional[date] = None) -> float:
    """
    Retorna o fator multiplicador IPCA de data_base até data_fim (padrão: hoje).
    Ex.: R$ 1.000 em jun/2015 → R$ 1.000 * fator_correcao(date(2015,6,1)) em valor atual.
    Fallback de 5,5% a.a. se a API BCB estiver indisponível.
    """
    if data_fim is None:
        data_fim = date.today()
    if data_base >= data_fim:
        return 1.0

    idx = _get_index()
    if not idx:
        anos = (data_fim - data_base).days / 365.25
        return 1.055 ** anos

    v_base = _nearest(idx, (data_base.year, data_base.month))
    v_fim  = _nearest(idx, (data_fim.year,  data_fim.month))

    if v_base is None or v_fim is None or v_base == 0:
        anos = (data_fim - data_base).days / 365.25
        return 1.055 ** anos

    return v_fim / v_base


def ipca_disponivel() -> bool:
    return bool(_get_index())
