import json
import re
import pytest
import os
import pathlib

from cleaner.configuration import Configuration


def test_proper(fs):
    config_directory = "config"
    config_file_name = "proper_config.json"
    config_json = {
        "retention": {
            "default": 30,
            "942021": 60,
            "9252021": 120
        }
    }
    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    config = Configuration(config_file_path)
    assert config.get_default_retention_policy() == 30
    assert config.get_retention_by_id('942021') == 60
    assert config.get_retention_by_id('9252021') == 120


def test_not_existing_retention_get_default(fs):
    config_directory = "config"
    config_file_name = "proper_config.json"
    config_json = {
        "retention": {
            "default": 30,
            "942021": 60,
            "9252021": 120
        }
    }
    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    config = Configuration(config_file_path)
    assert config.get_retention_by_id_or_default('AAA942021') == 30


def test_config_not_exists():
    current_working_dir = pathlib.Path().resolve()
    config_directory = "test_config_parser"
    config_file_name = "config_not_exists.json"
    config_file_path = os.path.normpath(os.path.join(current_working_dir, config_directory, config_file_name))
    with pytest.raises(RuntimeError) as except_info:
        config = Configuration(config_file_path)
    assert re.match('^File not accessible\. File:.*', except_info.value.args[0])


def test_broken_no_retention_defined(fs):
    config_directory = "config"
    config_file_name = "config_broken_no_retention.json"
    config_json = {

    }

    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    with pytest.raises(RuntimeError) as except_info:
        config = Configuration(config_file_path)
        config.get_default_retention_policy()
    assert except_info.value.args[0] == 'Retention Policy not specified in config'


def test_broken_no_default_retention(fs):
    config_directory = "config"
    config_file_name = "config_broken_no_default_retention.json"
    config_json = {
        "retention": {
            "ABC": 60,
            "123": 120
        }
    }

    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    with pytest.raises(ValueError) as except_info:
        config = Configuration(config_file_path)
        config.get_default_retention_policy()
    assert except_info.value.args[0] == 'Default Retention Policy not specified in config'


def test_broken_default_retention_not_a_number(fs):
    config_directory = "config"
    config_file_name = "config_broken_default_retention_not_a_number.json"
    config_json = {
        "retention": {
            "default": "week",
            "ABC": 60,
            "123": 120
        }
    }

    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    with pytest.raises(TypeError) as except_info:
        config = Configuration(config_file_path)
        config.get_default_retention_policy()
    assert except_info.value.args[0] == 'Defined retention is not an integer value'


def test_broken_not_existing_retention(fs):
    config_directory = "config"
    config_file_name = "proper_config.json"
    config_json = {
        "retention": {
            "default": 30,
            "942021": 60,
            "9252021": 120
        }
    }
    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    with pytest.raises(ValueError) as except_info:
        config = Configuration(config_file_path)
        config.get_retention_by_id('AAA942021')
    assert except_info.value.args[0] == 'Retention Policy not specified in config'


def test_broken_no_default_retention_id_not_exists(fs):
    config_directory = "config"
    config_file_name = "config_broken_no_default_retention.json"
    config_json = {
        "retention": {
            "ABC": 60,
            "123": 120
        }
    }

    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    with pytest.raises(ValueError) as except_info:
        config = Configuration(config_file_path)
        config.get_retention_by_id_or_default('AAA942021')
    assert except_info.value.args[0] == 'Default Retention Policy not specified in config'


def test_broken_id_not_exists_default_retention_not_a_number(fs):
    config_directory = "config"
    config_file_name = "config_broken_default_retention_not_a_number.json"
    config_json = {
        "retention": {
            "default": "week",
            "ABC": 60,
            "123": 120
        }
    }

    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    json_object = json.dumps(config_json, indent=4)
    with open(config_file_path, "w") as outfile:
        outfile.write(json_object)
    assert os.path.exists(config_file_path)

    with pytest.raises(TypeError) as except_info:
        config = Configuration(config_file_path)
        config.get_retention_by_id_or_default('AAA942021')
    assert except_info.value.args[0] == 'Defined retention is not an integer value'


def test_broken_json(fs):
    config_directory = "config"
    config_file_name = "config_broken_json.json"
    config_json = """{
        "retention": {
            "default": 30,
            "ABC": 60,
            "123": 120

        }"""

    config_file_path = os.path.normpath(os.path.join(config_directory, config_file_name))
    fs.create_file(config_file_path)

    with open(config_file_path, "w") as outfile:
        outfile.write(config_json)

    assert os.path.exists(config_file_path)

    with pytest.raises(RuntimeError) as except_info:
        config = Configuration(config_file_path)
    assert except_info.value.args[0] == 'Config file seems to be broken'
