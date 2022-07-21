def test_all_routes(client):
    routes = [
        "/",
        "/home",
        "/search",
        "/simplesearch/",
        "/user/mw2056/",
        "/fish/1",
        "/fish/1/changes/all",
        "/fish/1/history/",
        "/fish/1/updatealleles/",
        "/newfish/",
        "/updatefish/1/",
        "/allfish/",
        "/projectlicense/ABC123456/",
        "/stock/S0001/",
        "/settings/",
        "/fish/1/photo/1/editcaption/",
        "/guides/",
        "/userlist/",


    ]



    for route in routes:
        response = client.post(route)
        assert response.status_code != 404
        assert response.status_code not in range(500,505)
        print(response.status_code)

    response = client.post("/invalidroute/")
    assert response.status_code == 404
        
