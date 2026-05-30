import click
import uvicorn


@click.group()
def cli() -> None:
    """OpenLobbying application commands."""


@cli.command()
@click.option("--port", "-p", type=int, default=8000, help="Port")
@click.option("--host", "-h", default="127.0.0.1", help="Host")
@click.option("--reload", "-r", is_flag=True, default=False, help="Reload")
def server(port: int, host: str, reload: bool) -> None:
    """Start the OpenLobbying API server."""
    uvicorn.run("openlobbying.api.server:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()
