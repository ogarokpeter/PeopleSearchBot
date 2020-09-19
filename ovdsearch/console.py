import click
from . import cfg, webapp, db

@click.group()
def cli():
    """
    Сервис для координации поиска людей,
    увезенных силовиками в неизвестном направлении
    """

@cli.command("bot")
def serve_bot():
    """
    Запускает работу бота.
    """
    config = cfg.Config()
    config.check()
    database = db.Database(url=config.db_url)
    webapp.main(database, token=config.telegram_token)
