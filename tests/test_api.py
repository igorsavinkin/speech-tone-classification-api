from fastapi.testclient import TestClient

from app.main import app, queue

client = TestClient(app)


def setup_function() -> None:
    queue.reset()


def test_classify_high_confidence_returns_immediate_result() -> None:
    response = client.post("/classify", json={"text": "good excellent amazing"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["label"] == "positive"
    assert payload["confidence"] >= 0.9
    assert payload["task_id"] is None


def test_classify_low_confidence_creates_task_and_aggregates() -> None:
    response = client.post("/classify", json={"text": "okay"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "waiting_for_humans"
    task_id = payload["task_id"]
    assert task_id

    client.post(f"/tasks/{task_id}/label", json={"label": "positive"})
    client.post(f"/tasks/{task_id}/label", json={"label": "negative"})
    final_response = client.post(
        f"/tasks/{task_id}/label", json={"label": "positive"}
    )
    assert final_response.status_code == 200
    final_payload = final_response.json()
    assert final_payload["status"] == "completed"
    assert final_payload["final_label"] == "positive"
    assert len(final_payload["human_labels"]) == 3
