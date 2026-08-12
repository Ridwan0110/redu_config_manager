"""
AI Generated. Tweaked by human.
"""

# Imports
import pytest
import yaml
from pathlib import Path
from redu_config_manager import ConfigManager, __version__


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_config_data():
    return {
        "app": {
            "name": "TestApp",
            "version": "1.0.0",
            "debug": True
        },
        "database": {
            "host": "localhost",
            "port": 5432
        },
        "simple_key": "simple_value"
    }


@pytest.fixture
def temp_yaml_file(tmp_path, sample_config_data):
    """Creates a temporary valid YAML configuration file."""
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.safe_dump(sample_config_data, f)
    return config_file


# ============================================================================
# 1. VERSION TESTS
# ============================================================================
def test_version_attribute():
    """Verify package version is present and standard string format."""
    assert isinstance(__version__, str)

def test_version():
    """Verify package version is set."""
    assert __version__ == "1.1.0"


# ============================================================================
# 2. INITIALIZATION AND REPRESENTATION TESTS
# ============================================================================

def test_initialization(temp_yaml_file):
    """Test successful initialization and repr formatting."""
    cm = ConfigManager(temp_yaml_file)
    assert cm.config_path == Path(temp_yaml_file)
    assert repr(cm).startswith(f"ConfigManager(config_path={temp_yaml_file}")

def test_file_not_found(tmp_path):
    """Test FileNotFoundError when loading a non-existent file."""
    non_existent = tmp_path / "non_existent.yaml"
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        ConfigManager(non_existent)

def test_invalid_file_extension(tmp_path):
    """Test ValueError when initializing with unsupported extension."""
    invalid_file = tmp_path / "config.json"
    invalid_file.touch()

    with pytest.raises(ValueError, match="Unsupported file format"):
        ConfigManager(invalid_file)

def test_ignore_file_format(tmp_path, sample_config_data):
    """Test ignore_file_format flag bypassing extension check."""
    txt_file = tmp_path / "config.txt"
    with open(txt_file, "w") as f:
        yaml.safe_dump(sample_config_data, f)

    # Should not raise ValueError even though it's .txt
    cm = ConfigManager(txt_file, ignore_file_format=True)
    assert cm.get_value("app.name") == "TestApp"

def test_corrupted_yaml(tmp_path):
    """Test ValueError raised on malformed YAML contents."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("app: [invalid yaml structure: {")

    with pytest.raises(ValueError, match="Error loading YAML file"):
        ConfigManager(bad_yaml)


# ============================================================================
# 3. READING VALUES
# ============================================================================

def test_get_value(temp_yaml_file):
    """Test reading direct and nested keys."""
    cm = ConfigManager(temp_yaml_file)

    # Root-level key
    assert cm.get_value("simple_key") == "simple_value"

    # Nested key using dot notation
    assert cm.get_value("app.name") == "TestApp"
    assert cm.get_value("database.port") == 5432

    # Non-existent key with default values
    assert cm.get_value("non_existent") is None
    assert cm.get_value("app.non_existent", default="default_val") == "default_val"
    assert cm.get_value("a.b.c.d", default=42) == 42

def test_get_config_dict(temp_yaml_file, sample_config_data):
    """Test the @property get_config_dict."""
    cm = ConfigManager(temp_yaml_file)
    assert cm.get_config_dict == sample_config_data


# ============================================================================
# 4. WRITING AND UPDATING VALUES
# ============================================================================

def test_set_value_with_save(temp_yaml_file):
    """Test setting values (existing, nested, new) and persisting to file."""
    cm = ConfigManager(temp_yaml_file)

    # Update existing nested key
    cm.set_value("app.version", "2.0.0", save=True)
    assert cm.get_value("app.version") == "2.0.0"

    # Set new deeply nested key
    cm.set_value("logging.level.console", "DEBUG", save=True)
    assert cm.get_value("logging.level.console") == "DEBUG"

    # Verify updates persisted to file by re-reading disk file
    cm_reloaded = ConfigManager(temp_yaml_file)
    assert cm_reloaded.get_value("app.version") == "2.0.0"
    assert cm_reloaded.get_value("logging.level.console") == "DEBUG"

def test_set_value_without_save(temp_yaml_file):
    """Test set_value with save=False (in-memory update only)."""
    cm = ConfigManager(temp_yaml_file)
    cm.set_value("app.name", "NewName", save=False)

    # Updated in-memory
    assert cm.get_value("app.name") == "NewName"

    # Reloaded instance from file should still have old value
    cm_reloaded = ConfigManager(temp_yaml_file)
    assert cm_reloaded.get_value("app.name") == "TestApp"

def test_replace_config_dict(temp_yaml_file):
    """Test replacing in-memory dictionary and invalid input handling."""
    cm = ConfigManager(temp_yaml_file)
    new_data = {"server": {"port": 8080}}

    # Valid replacement
    cm.replace_config_dict(new_data)
    assert cm.get_config_dict == new_data
    assert cm.get_value("server.port") == 8080
    assert cm.get_value("app.name") is None  # Old data gone

    # Test invalid replacements (should ignore and preserve current state)
    cm.replace_config_dict(None)
    assert cm.get_config_dict == new_data

    cm.replace_config_dict("not_a_dict")
    assert cm.get_config_dict == new_data

    cm.replace_config_dict({})
    assert cm.get_config_dict == new_data
