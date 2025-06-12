def test_liveness(test_client):
    response = test_client.get("/livez")
    assert response.status_code == 200
    assert response.data == b"OK"


def test_readiness(test_client):
    response = test_client.get("/readyz")
    assert response.status_code == 200
    assert response.data == b"OK"


def test_index(test_client):
    response = test_client.get("/")
    assert response.status_code == 200


def test_detail(test_client):
    response = test_client.get("/api/1")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert b"JOHN SMITH" in response.data


def test_geocode_q(test_client):
    response = test_client.get("/api/geocode", query_string={"q": "smith"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert b"JOHN SMITH" in response.data
    response = test_client.get("/api/geocode", query_string={"q": "springfield"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert b"JOHN SMITH" in response.data
    response = test_client.get("/api/geocode", query_string={"q": "foobar"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert b"JOHN SMITH" not in response.data


def test_geocode_point(test_client):
    response = test_client.get("/api/geocode", query_string={"point": "-71.17763236840248,42.39033676010929"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert b"JOHN SMITH" in response.data
    response = test_client.get("/api/geocode", query_string={"point": "0.0,0.0"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert b"JOHN SMITH" not in response.data


def test_geocode_invalid(test_client):
    response = test_client.get("/api/geocode")
    assert response.status_code == 400


def test_geocode_point_invalid(test_client):
    response = test_client.get("/api/geocode", query_string={"point": "foobar"})
    assert response.status_code == 400
