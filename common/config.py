import configparser
import os
import toml


CONFIG_PATH = "conf/config.toml"


class Config:
    def __init__(self):
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"Configuration file '{CONFIG_PATH}' not found.")

        try:
            self.__config = toml.load(CONFIG_PATH)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{CONFIG_PATH}' not found.")
        except Exception as e:
            raise Exception(f"Error loading configuration file '{CONFIG_PATH}': {e}")

        print(self.__config)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.__config
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default


config = Config()

if __name__ == "__main__":
    print(f"Camera.pipe_id: [{config.get('Camera.pipe_id')}]")
    print(f"Camera.video_index: [{config.get('Camera.video_index')}]")
    print(f"Camera.fps: [{config.get('Camera.fps')}]")
    print(f"Camera.width: [{config.get('Camera.width')}]")
    print(f"Camera.height: [{config.get('Camera.height')}]")
