import pytest

from app.client.utils import Url, get_socket_url, load_latest_messages, register_user


@pytest.fixture()
def mock_get_req(mocker):
    return mocker.patch('app.client.utils.requests.get')


@pytest.fixture()
def mock_post_req(mocker):
    return mocker.patch('app.client.utils.requests.post')


def test_load(mock_get_req):
    mock_get_req.return_value.json.return_value = ['mes1', 'mes2']
    assert load_latest_messages() == ['mes1', 'mes2']


def test_register(mock_post_req):
    mock_post_req.return_value.status_code = 201
    mock_post_req.return_value.json.return_value = {'id': 1}
    assert register_user('user') == 1

    mock_post_req.return_value.status_code = 409
    mock_post_req.return_value.json.return_value = {'id': 1}
    assert register_user('user') is None


def test_get_socket_url():
    expected = f'{Url.WEBSOCKET}/1'
    assert get_socket_url(1) == expected
