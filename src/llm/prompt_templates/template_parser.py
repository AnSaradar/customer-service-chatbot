import os
import logging

class TemplateParser:

    def __init__(self, language: str = None, default_language: str = "en"):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        self.set_language(language)


        self.logger = logging.getLogger(__name__)


    
    def set_language(self, language: str):
        language_path = os.path.join(self.current_path,"locales",language)
        if language is not None and os.path.exists(language_path):
            self.language = language
        else:
            self.logger.error(f"Could not find the language : {language}")
            self.language = self.default_language

    
    def get_template(self, group: str, key: str, vars: dict={}):

        if not group:
            self.logger.error("Group is missing.")
            return None
        
        if not key:
            self.logger.error("Key is missing.")
            return None
        
        group_path = os.path.join(self.current_path,'locales',self.language,f"{group}.py")
        target_language = self.language
        if not os.path.exists(group_path):
            self.logger.error(f"Group file not found: {group_path}")
            group_path = os.path.join(self.current_path,'locales',self.default_language,f"{group}.py")
            target_language = self.default_language

        if not os.path.exists(group_path):
            self.logger.error(f"Default group file not found: {group_path}")
            return None
        
        module = __import__(f"llm.prompt_templates.locales.{target_language}.{group}", fromlist={group})

        if not module:
            self.logger.error(f"Failed to import module: {group_path}")
            return None
        
        key_attributes = getattr(module,key)

        if not key_attributes:
            self.logger.error(f"Key not found in the module: {group_path}.{key}")
            return None

        return key_attributes.substitute(vars)

