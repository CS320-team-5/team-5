from app.repositories.user import (
    PUBLIC_USER_COLUMNS,
    get_user,
    update_user,
)


def test_get_user_selects_only_public_columns(fake_db, user_row):
    query = fake_db.table.return_value
    query.execute.return_value.data = [user_row]

    result = get_user(fake_db, 7)

    assert result == user_row
    fake_db.table.assert_called_once_with("users")
    query.select.assert_called_once_with(PUBLIC_USER_COLUMNS)
    query.eq.assert_called_once_with("userid", 7)
    query.limit.assert_called_once_with(1)
    assert "authid" not in PUBLIC_USER_COLUMNS


def test_get_user_returns_none_when_missing(fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    assert get_user(fake_db, 999) is None


def test_update_user_targets_only_requested_id(fake_db, user_row):
    query = fake_db.table.return_value
    query.execute.return_value.data = [{**user_row, "name": "Changed"}]

    result = update_user(fake_db, 7, {"name": "Changed"})

    assert result["name"] == "Changed"
    fake_db.table.assert_called_once_with("users")
    query.update.assert_called_once_with({"name": "Changed"})
    query.eq.assert_called_once_with("userid", 7)
    query.select.assert_called_once_with(PUBLIC_USER_COLUMNS)


def test_update_missing_user_returns_none(fake_db):
    fake_db.table.return_value.execute.return_value.data = []
    assert update_user(fake_db, 7, {"name": "New"}) is None