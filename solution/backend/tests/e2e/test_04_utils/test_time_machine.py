import pytest

from tests.e2e.fixtures import AppClient, test_client


@pytest.mark.parametrize(
    "current_day",
    [-1, 0, 1, 100, 10000]
)
async def test_time_change(
        test_client: AppClient,
        current_day: int,
):
    response = await test_client.post(
        "/time/advance",
        json={"current_date": current_day}
    )
    assert response.status_code == 200
    response = await test_client.get("/ping")
    assert response.status_code == 200
    assert response.json()["current_date"] == current_day
