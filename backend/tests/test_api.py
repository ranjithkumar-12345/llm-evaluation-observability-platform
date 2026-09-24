def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data or "message" in data


def test_documents_list_endpoint(client):
    response = client.get("/api/documents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_stats_endpoint(client):
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data or "total_evaluations" in data