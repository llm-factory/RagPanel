from pathlib import Path
import yaml
from typing import Any, Dict, Optional


class ConfigManager:
    _config: Dict[str, Any] = {
        "database": {
            "collection": "test"
        },
        "build": {
            "folder": "./inputs"
        },
        "launch": {
            "host": "127.0.0.1",
            "port": 8080
        },
        "webui": {
            "host": "127.0.0.1",
            "port": 7860,
        },
        "dump": {
            "folder": "./chat_history"
        }
    }

    def __init__(self):
        self._config_path = Path(__file__).parent.parent.parent.parent / ".config" / "config.yaml"
        self._load_config()

    def _load_config(self) -> None:
        """从配置文件加载配置"""
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    self._config.update(loaded_config)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self._config_path}, using default settings")
            self.save_config()

    def save_config(self) -> None:
        """保存配置到文件"""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)

    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """获取配置
        
        Args:
            section: 配置节点名称，如果为None则返回整个配置
        
        Returns:
            配置字典
        """
        if section is None:
            return self._config
        return self._config.get(section, {})

    def update_config(self, section: str, key: str, value: Any) -> None:
        """更新配置的特定值
        
        Args:
            section: 配置节点名称
            key: 配置键
            value: 配置值
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value


# 创建全局配置管理器实例
config_manager = ConfigManager()

# 导出便捷函数
def get_config(section: Optional[str] = None) -> Dict[str, Any]:
    return config_manager.get_config(section)

def update_config(section: str, key: str, value: Any) -> None:
    config_manager.update_config(section, key, value)

def save_config() -> None:
    config_manager.save_config()
