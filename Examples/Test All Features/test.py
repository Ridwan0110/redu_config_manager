# test.py

import os
import yaml

from redu_config_manager.redu_config_manager import ConfigManager

def create_sample_yaml(path):
    config_data = {
        'host': 'localhost',
        'port': 8080,
        'debug': True,
        'nested': {
            'key': 'value'
        }
    }
    with open(path, 'w') as f:
        yaml.dump(config_data, f)
    print(f"[DEBUG] Sample YAML config written to {path}")

def test_config_manager():
    config_path = 'test_config.yaml'
    create_sample_yaml(config_path)

    print("[DEBUG] Initializing ConfigManager...")
    config = ConfigManager(config_path)
    print(f"[DEBUG] ConfigManager initialized: {config}")

    # Test getting existing keys
    host = config.get_value('host')
    print(f"[DEBUG] host: {host} (expected: 'localhost')")

    port = config.get_value('port')
    print(f"[DEBUG] port: {port} (expected: 8080)")

    debug = config.get_value('debug')
    print(f"[DEBUG] debug: {debug} (expected: True)")

    # Test getting nested key (should return None)
    nested = config.get_value('nested.key')
    print(f"[DEBUG] nested: {nested} (expected: value)")

    # Test getting non-existent key with default
    missing = config.get_value('not_found', default='default_value')
    print(f"[DEBUG] not_found: {missing} (expected: 'default_value')")

    # Test file format check
    try:
        print("[DEBUG] Testing unsupported file format...")
        ConfigManager('test_config.txt')
    except ValueError as e:
        print(f"[DEBUG] Caught expected ValueError: {e}")

    # Test file format check with ignore_file_format=True
    try:
        print("[DEBUG] Testing unsupported file format with ignore_file_format=True...")
        ConfigManager('test_config.txt', ignore_file_format=True)
        print("[DEBUG] ConfigManager initialized with unsupported file format (ignore_file_format=True)")
    except Exception as e:
        print(f"[DEBUG] Caught unexpected Exception: {e}")

    # Test file not found
    try:
        print("[DEBUG] Testing file not found...")
        ConfigManager('does_not_exist.yaml')
    except FileNotFoundError as e:
        print(f"[DEBUG] Caught expected FileNotFoundError: {e}")

    # Clean up
    os.remove(config_path)
    print(f"[DEBUG] Removed sample config file: {config_path}")

def test_set_and_save():
    config_path = 'test_config_set.yaml'
    create_sample_yaml(config_path)

    print("[DEBUG] Initializing ConfigManager...")
    config = ConfigManager(config_path)
    print(f"[DEBUG] ConfigManager initialized: {config}")

    # Set a top-level value
    config.set_value('host', '127.0.0.1')
    print(f"[DEBUG] host after set: {config.get_value('host')} (expected: '127.0.0.1')")

    # Set a nested value
    config.set_value('nested.key', 'new_value')
    print(f"[DEBUG] nested.key after set: {config.get_value('nested.key')} (expected: 'new_value')")

    # Add a new nested value
    config.set_value('new.section.value', 123)
    print(f"[DEBUG] new.section.value after set: {config.get_value('new.section.value')} (expected: 123)")

    # Save and reload to check persistence
    config.save_config()
    config2 = ConfigManager(config_path)
    print(f"[DEBUG] host after reload: {config2.get_value('host')} (expected: '127.0.0.1')")
    print(f"[DEBUG] nested.key after reload: {config2.get_value('nested.key')} (expected: 'new_value')")
    print(f"[DEBUG] new.section.value after reload: {config2.get_value('new.section.value')} (expected: 123)")

    # Clean up
    os.remove(config_path)
    print(f"[DEBUG] Removed sample config file: {config_path}")

if __name__ == '__main__':
    test_config_manager()
    test_set_and_save()