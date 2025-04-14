from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def test_ai_text_gen(test_client: AppClient):
    response = await test_client.post(
        "/ai/generate-text",
        json={
            "topic": "корм для собак",
            "language": "RU"
        }
    )
    assert response.status_code == 200
    text = response.json()["result"]
    assert "корм" in text.lower()


async def test_ai_text_gen_with_additional(test_client: AppClient):
    response = await test_client.post(
        "/ai/generate-text",
        json={
            "topic": "корм для собак",
            "language": "RU",
            "additional": "Корм является лучшим по результатам опросов."
        }
    )
    assert response.status_code == 200
    text = response.json()["result"]
    assert "корм" in text.lower()
    assert "лучший" in text.lower()
