"""
A simple configuration manager that reads a configuration file and provides methods to access
configuration values programmatically.

Only work with supported file formats.
"""

# Imports
import yaml
from pathlib import Path
from typing import Union

__version__ = "1.1.0"

# Only these supported file formats will be parsed correctly.
# Note: Adding support for more file formats is possible if the logic is implemented.
supported_file_formats = ('.yaml', '.yml')


class ConfigManager:
    def __init__(self,
                 config_path: Union[str, Path],
                 ignore_file_format: bool=False,
    ):
        """
        Initialize the ConfigManager class.

        Args:
            config_path: Path to the configuration file.
            ignore_file_format: If True, ignore file format checks. NOT RECOMMENDED.
        """
        # Initialize arguments
        self.config_path = Path(config_path)
        self.ignore_file_format = ignore_file_format

        # Check if the file format is supported
        if not ignore_file_format:
            self._check_file_format()

        # Load the configuration file and store it in memory
        self._config = None
        self._load_config()

    def __repr__(self):
        """
        Return a string representation of the ConfigManager instance.

        Includes:
         - The path to the configuration file.
         - The memory address of the instance.
        """
        return f"ConfigManager(config_path={self.config_path}, address={hex(id(self))})"

    def _check_file_format(self):
        """
        Check if the configuration file has a supported format.

        Raises:
            ValueError: If the file format is not supported and ignore_file_format is False.
        """

        if not self.config_path.suffix in supported_file_formats:
            raise ValueError(f"Unsupported file format: {self.config_path.suffix}. Supported formats are: {supported_file_formats}")

    def _load_config(self):
        """
        Load the configuration file and store it in memory.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If there is an error loading the YAML file.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f)
                if self._config is None:
                    self._config = {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading YAML file: {e}")

    def save_config(self):
        """
        Save the current configuration to the file from the memory.

        Raises:
            ValueError: If there is an error saving the YAML file.
        """
        try:
            with open(self.config_path, "w") as f:
                yaml.safe_dump(self._config, f)
        except Exception as e:
            raise ValueError(f"Error saving YAML file: {e}")

    def get_value(self, key, default=None):
        """
        Get a configuration value by key. Get nested values using dot notation. i.e. 'nested.key'.

        Args:
            key: The key to look up in the configuration.
            default: The default value to return if the key is not found.
            The value associated with the key, or the default value if the key is not found.
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set_value(self, key, value, save=True):
        """
        Set a configuration value by key. Supports dot-separated keys for nested values.
        Creates nested dictionaries as needed.

        Args:
            key: The key (dot-separated for nested) to set.
            value: The value to set.
            save: If True, save the config to file after setting.
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}  # Create a new dictionary if the key does not exist or is not a dict
            config = config[k]  # Update config to the nested dictionary
        # Set the final key to the value
        config[keys[-1]] = value
        if save:
            self.save_config()

    @property
    def get_config_dict(self) -> dict:
        """Returns ``self._config`` from memory"""
        return self._config

    def replace_config_dict(self, config_dict: dict):
        """
        Replaces in-memory ``self._config`` with ``config_dict``

        Args:
            config_dict (dict): The dictionary to replace with as config
        """
        if not config_dict or not isinstance(config_dict, dict):
            return

        self._config = config_dict
