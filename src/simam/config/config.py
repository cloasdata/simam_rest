import configparser
from pathlib import Path



DEFAULT_CONFIG_INI = Path(__file__).parent / "default_config.ini"

config = configparser.ConfigParser()
config.read(DEFAULT_CONFIG_INI)

