import pytest
from typer.testing import CliRunner

from app.client.app import typer_app

runner = CliRunner()


@pytest.fixture
def mock_register_user(mocker):
    return mocker.patch('app.client.app.register_user')


@pytest.fixture
def mock_load(mocker):
    return mocker.patch('app.client.app.load_latest_messages')


def test_app_no_name(mock_register_user):
    mock_register_user.return_value = None
    result = runner.invoke(typer_app, input='user\n yes\n')
    assert result.exit_code == 401


def test_app_load(mock_register_user, mock_load):
    mock_register_user.return_value = 1

    mock_load.return_value = ['user: hello']
    result = runner.invoke(typer_app, input='user\n yes\n')
    assert 'user: hello' in result.stdout
    mock_load.assert_called_once_with()


def test_app_no_load(mock_register_user, mock_load):
    mock_register_user.return_value = 1

    runner.invoke(typer_app, input='user\n no\n')

    assert not mock_load.called
