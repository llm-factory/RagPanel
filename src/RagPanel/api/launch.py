from enum import Enum, unique
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv


load_dotenv()  # must before utils


from .viewer import dump_history
from ..engines import ApiEngine
from ..utils.save_config import save_config, update_config, get_config


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
@click.option("--action", required=True, type=click.Choice([act.value for act in Action]), prompt="Choose an action")
def interactive_cli(action):
    if action == Action.EXIT:
        return
    config_dict = get_config()

    collection = config_dict["database"]["collection"]
    if action != Action.WEBUI:
        engine = ApiEngine(collection)

    if action == Action.BUILD:
        folder = Path(config_dict["build"]["folder"])
        engine.insert(folder, 32)
    elif action == Action.LAUNCH:
        host = config_dict["launch"]["host"]
        port = int(config_dict["launch"]["port"])
        engine.launch_app(collection, host, port)
    elif action == Action.DUMP:
        folder = Path(config_dict["dump"]["folder"])
        dump_history(Path(folder), "history_" + collection)
    elif action == Action.WEBUI:
        from ..webui import create_ui
        
        host = config_dict.get("webui", {}).get("host", "127.0.0.1")
        port = int(config_dict.get("webui", {}).get("port", 7860))
        lang = config_dict.get("webui", {}).get("lang", None)
        if lang is None:
            lang = click.prompt('choose your language', type=click.Choice(["en", "zh"]))
            update_config("webui", "lang", lang)
            save_config()
            from ..utils.locales import LOCALES
            print(LOCALES["lang_saved"][lang])
            
        create_ui(lang, collection).queue().launch(server_name=host, server_port=port)
