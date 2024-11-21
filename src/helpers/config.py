from pydantic_settings import BaseSettings , SettingsConfigDict
import logging
import os
import json


logger = logging.getLogger('uvicorn.error')


class Settings(BaseSettings):

    APP_NAME : str
    APP_VERSION : str

    FILE_ALLOWED_TYPES : list
    FILE_MAX_SIZE : int
    FILE_DEFAULT_CHUNK_SIZE : int

    MONGODB_URL : str
    MONGODB_DATABASE : str

    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str

    OPENAI_API_KEY : str 
    OPENAI_API_URL : str

    COHERE_API_KEY : str

    GENERATION_MODEL_ID : str
    EMBEDDING_MODEL_ID : str
    EMBEDDING_MODEL_SIZE : str

    DEFAULT_INPUT_MAX_CHARACTERS : int = None
    DEFAULT_GENERATION_MAX_OUTPUT_TOKENS : int = None
    DEFAULT_GENERATION_TEMPREATUER : float = None

    VECTORDB_BACKEND : str
    VECTORDB_PATH : str
    VECTORDB_DISTANCE_METHOD : str

    DEFAULT_LANGUAGE : str = 'en'
    PRIMARY_LANGUAGE : str




    class Config(SettingsConfigDict):
        env_file = ".env"

def get_settings():
    return Settings()

def format_value(value):
    """
    Format the value based on its type for the .env file.
    """
    if isinstance(value, str):
        # Enclose strings in a single pair of double quotes (no extra quotes)
        return f'"{value}"'
    elif isinstance(value, list):
        # Manually create a list in the format ["item1", "item2"] without additional quotes
        # This approach avoids escaping inner quotes like json.dumps does.
        return "[" + ",".join(f'"{item}"' for item in value) + "]"
    elif isinstance(value, int) or isinstance(value, float):
        # For numeric values, just convert them to string (no quotes)
        return str(value)
    else:
        raise ValueError(f"Unsupported type: {type(value)}")
    

async def update_env_file_configuration(updated_config : dict, env_file = ".env"):

    #logger.error(f"Info from Config File............................................")

    env_vars = get_settings().dict()
    # current_config.update(updated_config)

    #logger.info(f"Info from Config File  : Updated Configuration :{current_config}")

    # with open(env_file, "w") as f:
    #     for key, value in current_config.items():
    #         # Ensure value is a string (Pydantic may keep it as an int or list)
    #         value_str = ','.join(value) if isinstance(value, list) else str(value)
    #         f.write(f"{key}={value_str}\n")

    # env_vars = {}
    # if os.path.exists(env_file):
    #     with open(env_file, "r") as f:
    #         for line in f:
    #             line = line.strip()
    #             if line and not line.startswith("#") and "=" in line:
    #                 key, value = line.split("=", 1)
    #                 env_vars[key] = value.strip() 
    #logger.info(f"Info from Config File  : Current Configuration :{env_vars}")
    env_vars.update(updated_config)
    # logger.info(f"Info from Config File  : Updated Configuration :{env_vars}")

    with open(env_file, "w") as f:
        for key, value in env_vars.items():
            formatted_value = format_value(value)
            f.write(f"{key}={formatted_value}\n")   
    