import asyncio

import typer

from .socket import start_chat
from .utils import load_latest_messages, register_user

typer_app = typer.Typer()


@typer_app.command()
def main(
    name: str = typer.Option(..., prompt=True),
    is_load: bool = typer.Option(..., prompt='Load latest messages?'),
) -> None:
    # get id for user
    user_id = register_user(name)
    if user_id is None:
        typer.echo('Something went wrong!')
        raise typer.Exit(code=401)

    # load latest messages
    if is_load is True:
        messages = load_latest_messages()
        for message in messages:
            typer.echo(message)

    asyncio.run(start_chat(user_id))
