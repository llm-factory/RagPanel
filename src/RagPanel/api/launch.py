from enum import Enum, unique
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv


load_dotenv()  # must before utils


from .viewer import dump_history
from ..engines import ApiEngine


try:
    import platform

    if platform.system() != "Windows":
        import readline  # noqa: F401
except ImportError:
    print("Install `readline` for a better experience.")


@unique
class Action(str, Enum):
    BUILD = "build"
    LAUNCH = "launch"
    DUMP = "dump"
    WEBUI = "webui"
    EXIT = "exit"


@click.command()
@click.option("--config", help="Path to your config file")
@click.option("--action", required=True, type=click.Choice([act.value for act in Action]), prompt="Choose an action")
def interactive_cli(config, action):
    if action != Action.WEBUI and action != Action.EXIT:
        if config is None:
            config = click.prompt('path to your config file')
        with open(config, "r", encoding="utf-8") as config_file:
            config_dict = yaml.safe_load(config_file)
            storage_collection = config_dict["database"]["storage_collection"]
            vectorstore_collection = config_dict["database"]["vectorstore_collection"]
            engine = ApiEngine()
            engine.create_database(storage_collection, vectorstore_collection)


    if action == Action.BUILD:
        folder = config_dict["build"]["folder"]
        engine.insert(folder, 32)
    elif action == Action.LAUNCH:
        host = config_dict["launch"]["host"]
        port = int(config_dict["launch"]["port"])
        engine.launch_app(host, port)
    elif action == Action.DUMP:
        folder = Path(config_dict["dump"]["folder"])
        dump_history(Path(folder), "chat_history")
    elif action == Action.WEBUI:
        from ..webui import create_ui
        create_ui().launch()
