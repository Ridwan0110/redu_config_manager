"""
A simple configuration manager that reads a configuration file and provides methods to access
configuration values.

Only work with supported file formats.
"""

# Imports
import yaml
import redu_logger
from pathlib import Path
from typing import Union


# Only these supported file formats will be parsed correctly.
# Note: Adding support for more file formats is possible if the logic is implemented.
supported_file_formats = ('.yaml', '.yml')


class NullLogger:
    def info(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass


class ConfigManager:
    def __init__(self,
                 config_path: Union[str, Path],
                 ignore_file_format: bool=False,
                 enable_logging: bool=False,
                 logger_local_log_file_name: str = "config.log",
                 logger_local_log_path: Union[str, Path] = "logs/config"
    ):
        """
        Initialize the ConfigManager class.

        :param config_path: Path to the configuration file.
        :param ignore_file_format: If True, ignore file format checks. NOT RECCOMMENDED.
        :param enable_logging: If True, enable logging. Default is False.
        :param logger_local_log_file_name: Name of the local log file.
        :param logger_local_log_path: Path to the local log file directory.
        """
        # Initialize the logger
        self.enable_logging = enable_logging
        self.logger_local_log_file_name = logger_local_log_file_name
        self.logger_local_log_path = str(logger_local_log_path)
        if enable_logging:
            self.logger = self._init_logger()
        else:
            self.logger = NullLogger()

        self.logger.info(f"Initializing ConfigManager with config_path: {config_path}")

        # Initialize arguments
        self.config_path = Path(config_path)
        self.ignore_file_format = ignore_file_format

        # Check if the file format is supported
        if not ignore_file_format:
            self.logger.info("Checking file format...")
            self._check_file_format()
        else:
            self.logger.warning("Ignoring file format check. This is not recommended.", True)

        # Log all arguments for debugging purposes
        self.logger.debug("ConfigManager initialized with arguments:")
        self.logger.info(locals())

        # Load the configuration file and store it in memory
        self.logger.info(f"Loading configuration from {self.config_path}")
        self._config = None
        self._load_config()

    def __repr__(self):
        """
        Return a string representation of the ConfigManager instance.

        Includes:
         - The path to the configuration file.
         - The memory address of the instance.
        """
        self.logger.info(f"Representing ConfigManager instance at {hex(id(self))}")

        return f"ConfigManager(config_path={self.config_path}, address={hex(id(self))})"

    def _init_logger(self):
        """
        Initialize redu_logger locally for the ConfigManager.
        """
        # Initialize the logger
        logger = redu_logger.RemoteLogger(
            local_logging=True,
            remote_logging=False,
            is_main=True,
            local_log_file_name=self.logger_local_log_file_name,
            local_log_path=self.logger_local_log_path,
            local_multi_log=True
        )

        return logger

    def _check_file_format(self):
        """
        Check if the configuration file has a supported format.

        Raises:
            ValueError: If the file format is not supported and ignore_file_format is False.
        """
        self.logger.info(f"Checking file format for {self.config_path}")

        if not self.config_path.suffix in supported_file_formats:
            raise ValueError(f"Unsupported file format: {self.config_path.suffix}. Supported formats are: {supported_file_formats}")

    def _load_config(self):
        """
        Load the configuration file and store it in memory.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If there is an error loading the YAML file.
        """
        self.logger.info(f"Loading configuration from {self.config_path}")

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f)
                if self._config is None:
                    self._config = {}
                    self.logger.info("Configuration file is empty. Initializing with an empty dictionary.")
            self.logger.info("Configuration loaded successfully.")
        except yaml.YAMLError as e:
            self.logger.error(f"Error loading YAML file: {e}", True)
            raise ValueError(f"Error loading YAML file: {e}")

    def save_config(self):
        """
        Save the current configuration to the file from the memory.

        Raises:
            ValueError: If there is an error saving the YAML file.
        """
        self.logger.info(f"Saving configuration to {self.config_path}")

        try:
            with open(self.config_path, "w") as f:
                yaml.safe_dump(self._config, f)
            self.logger.info("Configuration saved successfully.")
        except Exception as e:
            self.logger.error(f"Error saving YAML file: {e}", True)
            raise ValueError(f"Error saving YAML file: {e}")

    def get_value(self, key, default=None):
        """
        Get a configuration value by key. Get nested values using dot notation. i.e. 'nested.key'.

        :param key: The key to look up in the configuration.
        :param default: The default value to return if the key is not found.
        :return: The value associated with the key, or the default value if the key is not found.
        """
        self.logger.info("Getting value for key: {key} with default: {default}")

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

        :param key: The key (dot-separated for nested) to set.
        :param value: The value to set.
        :param save: If True, save the config to file after setting.
        """
        self.logger.info(f"Setting value for key: {key} to {value}")

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
