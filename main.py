from src.cli import StartCli
from src.loader import setup_app


if __name__ == "__main__":
    setup_app()
    StartCli.start()
