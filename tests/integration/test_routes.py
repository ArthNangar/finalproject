def test_register_login_and_dashboard(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Advance Calculator WebApp" in r.text

    r = client.post("/auth/register", data={"username":"arth","email":"arth@example.com","password":"Password123!"}, follow_redirects=False)
    assert r.status_code in (302, 303)

    r = client.post("/auth/login", data={"username":"arth","password":"Password123!"}, follow_redirects=False)
    assert r.status_code in (302, 303)
    assert "access_token" in r.cookies

    client.cookies.set("access_token", r.cookies.get("access_token"))
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Calculator" in r.text

def test_api_calculate_and_history(client):
    # register + login
    client.post("/auth/register", data={"username":"arth2","email":"arth2@example.com","password":"Password123!"}, follow_redirects=False)
    r = client.post("/auth/login", data={"username":"arth2","password":"Password123!"}, follow_redirects=False)
    client.cookies.set("access_token", r.cookies.get("access_token"))

    r = client.post("/api/calculate", json={"op":"mod","a":10,"b":3})
    assert r.status_code == 200
    assert r.json()["result"] == 1

    r = client.get("/api/history")
    assert r.status_code == 200
    assert len(r.json()) >= 1
