def test_get_settings_returns_defaults_for_new_user(authenticated_client, fake_db):
    query = fake_db.table.return_value
    query.execute.return_value.data = []

    response = authenticated_client.get("/api/user/me/settings")

    assert response.status_code == 200
    assert response.json() == {
        "courier_arrival_sms": False,
        "nearby_cart_alerts": False,
        "member_direct_chat_alerts": False,
    }
    query.eq.assert_called_once_with("authid", "test-auth-uuid")


def test_patch_settings_sends_only_the_changed_toggle(authenticated_client, fake_db):
    upsert = fake_db.table.return_value.upsert
    upsert.return_value.execute.return_value.data = [{
        "courier_arrival_sms": False,
        "nearby_cart_alerts": False,
        "member_direct_chat_alerts": True,
    }]

    response = authenticated_client.patch(
        "/api/user/me/settings",
        json={"nearby_cart_alerts": False},
    )

    assert response.status_code == 200
    assert response.json()["member_direct_chat_alerts"] is True
    upsert.assert_called_once_with(
        {"authid": "test-auth-uuid", "nearby_cart_alerts": False},
        on_conflict="authid",
        default_to_null=False,
    )


def test_patch_settings_rejects_a_client_supplied_account_id(authenticated_client):
    response = authenticated_client.patch(
        "/api/user/me/settings",
        json={"authid": "another-account"},
    )

    assert response.status_code == 422