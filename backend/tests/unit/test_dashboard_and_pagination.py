from datetime import datetime, timezone

from app.schemas.common import PaginatedResponse, PaginationParams
from app.services.dashboard_service import DashboardService, WEEKLY_ACTIVITY_DAYS


def test_pagination_skip_calculation():
    params = PaginationParams(page=3, limit=20)
    assert params.skip == 40


def test_pagination_first_page_has_zero_skip():
    params = PaginationParams(page=1, limit=10)
    assert params.skip == 0


def test_paginated_response_total_pages_rounds_up():
    response = PaginatedResponse.build(items=[], page=1, limit=10, total=25)
    assert response.total_pages == 3


def test_paginated_response_exact_division():
    response = PaginatedResponse.build(items=[], page=1, limit=10, total=20)
    assert response.total_pages == 2


def test_last_n_dates_returns_correct_count_in_chronological_order():
    dates = DashboardService._last_n_dates(WEEKLY_ACTIVITY_DAYS)
    assert len(dates) == WEEKLY_ACTIVITY_DAYS
    parsed = [datetime.fromisoformat(d).replace(tzinfo=timezone.utc) for d in dates]
    assert parsed == sorted(parsed)
    assert parsed[-1].date() == datetime.now(timezone.utc).date()
