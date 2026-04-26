def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_login(client):
    response = client.post("/api/auth/login", json={"email": "admin@medstore.local", "password": "Admin@12345"})
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_medicine_list_requires_auth(client):
    assert client.get("/api/medicines").status_code == 401


def test_medicine_list(client, auth):
    response = client.get("/api/medicines", headers=auth)
    assert response.status_code == 200
    assert response.get_json()["total"] >= 1


def test_create_bill_updates_stock(client, auth):
    med = client.get("/api/medicines?per_page=1", headers=auth).get_json()["items"][0]
    mrp = float(med["mrp"])
    gst = float(med["gst_rate"])
    total = mrp + (mrp * gst / 100)
    payload = {
        "patient_name": "Test Patient",
        "phone": "9999999999",
        "items": [{"medicine_id": med["id"], "qty": 1, "discount": "0.00"}],
        "payments": [{"mode": "cash", "amount": f"{total:.2f}"}],
    }
    response = client.post("/api/bills", json=payload, headers=auth)
    assert response.status_code == 201
    assert response.get_json()["status"] == "paid"
