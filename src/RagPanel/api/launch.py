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
@click.option("--config", help="Path to your config file", default=None)
@click.option("--action", required=True, type=click.Choice([act.value for act in Action]), prompt="Choose an action")
def interactive_cli(config, action):
    config_dict = None
    default_config_path = Path(__file__).parent.parent.parent.parent / ".config" / "config.yaml"

    if config is None:
        config = default_config_path

    try:
        with open(config, "r", encoding="utf-8") as config_file:
            config_dict = yaml.safe_load(config_file)
    except FileNotFoundError:
        if action not in [Action.WEBUI, Action.EXIT]:
            config = click.prompt('Default config not found. Please provide path to your config file')
            with open(config, "r", encoding="utf-8") as config_file:
                config_dict = yaml.safe_load(config_file)
        elif action == Action.WEBUI:
            print("Config file not found, using default settings")
            config_dict = {}

    if action != Action.EXIT and action != Action.WEBUI:
        collection = config_dict["database"]["collection"]
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
        lang = click.prompt('choose your language', type=click.Choice(["en", "zh"]))
        
        # 尝试从配置文件读取host和port，如果失败则使用默认值
        try:
            host = config_dict.get("webui", {}).get("host", "127.0.0.1")
            port = int(config_dict.get("webui", {}).get("port", 8080))
        except (KeyError, TypeError):
            host = "127.0.0.1"
            port = 8080
            
        collection = config_dict.get("database", {}).get("collection", "init")
        create_ui(lang, collection).queue().launch(server_name=host, server_port=port)
