from datetime import datetime, timezone

import pytest


@pytest.fixture
def referencia_fixa() -> datetime:
    """Data de referência fixa para tornar determinísticos os cálculos de idade/tempo."""
    return datetime(2024, 1, 1, tzinfo=timezone.utc)
