# tests/contrib/capacity_parsers/test_ember_mode_mapper.py
from __future__ import annotations

import pytest
import pandas as pd

# Ajuste este import conforme a estrutura do seu repo:
# Ex.: electricitymap.contrib.capacity_parsers.ember
import electricitymap.contrib.capacity_parsers.EMBER as ember


def _row(zone_key: str, mode):
    """Helper para criar a linha (pd.Series) esperada pelo mapper."""
    return pd.Series({"zone_key": zone_key, "mode": mode})


@pytest.fixture(autouse=True)
def patch_energies(monkeypatch):
    """
    Garante ambiente determinístico para o teste:
    - ENERGIES contém itens comuns
    - 'xyz' não pertence a ENERGIES
    """
    monkeypatch.setattr(
        ember,
        "ENERGIES",
        {"solar", "wind", "gas", "coal", "oil", "hydro", "nuclear"},
        raising=False,
    )


@pytest.mark.parametrize(
    "zone,mode,expected",
    [
        # CT1 — Mapeamento específico (TR + "other renewables") → "geothermal"
        ("TR", "other renewables", "geothermal"),
        # CT2 — B verdadeiro, C falso → default "unknown"
        ("TR", "xyz", "unknown"),
        # CT3 — Caminho ENERGIES (solar)
        ("FR", "solar", "solar"),
        # CT4 — Mapper genérico Ember (bioenergy → biomass)
        ("FR", "bioenergy", "biomass"),
        # CT5 — Default desconhecido (sem mapeamento)
        ("FR", "xyz", "unknown"),
        # CT7 — Case-insensitive em ENERGIES (SOLAR)
        ("FR", "SOLAR", "solar"),
        # CT8 — Específico: BD + "other fossil" → oil
        ("BD", "other fossil", "oil"),
        # CT9 — Sem específico, mas E verdadeiro ("other fossil") → "unknown"
        ("FR", "other fossil", "unknown"),
        # CT10 — Específico: NZ + "other renewables" → geothermal
        ("NZ", "other renewables", "geothermal"),
    ],
    ids=[
        "CT1_TR_other_renewables_specific",
        "CT2_TR_xyz_default_unknown",
        "CT3_FR_solar_energies",
        "CT4_FR_bioenergy_generic_biomass",
        "CT5_FR_xyz_default_unknown",
        "CT7_FR_SOLAR_case_insensitive",
        "CT8_BD_other_fossil_specific_oil",
        "CT9_FR_other_fossil_generic_unknown",
        "CT10_NZ_other_renewables_specific_geothermal",
    ],
)
def test_ember_production_mode_mapper_expected(zone, mode, expected):
    row = _row(zone, mode)
    out = ember._ember_production_mode_mapper(row)
    assert out == expected


def test_ember_production_mode_mapper_non_string_mode_raises():
    """
    CT6 — A falso (mode não-string) → comportamento atual levanta UnboundLocalError,
    pois 'production_mode' não é definido quando o isinstance falha.
    Se você corrigir o método para retornar "unknown" nesse caso,
    troque o assert para verificar o retorno.
    """
    row = _row("FR", None)
    with pytest.raises(UnboundLocalError):
        ember._ember_production_mode_mapper(row)
