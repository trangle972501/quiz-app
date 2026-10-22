from enum import Enum

class Languages(Enum):
    english = {"key": "en", "name": "English"}
    vietname = {"key": "vi", "name": "Vietnamese"}

    @classmethod
    def get_languages(cls) -> list["Languages"]:
        return list(cls)
    
    @classmethod
    def get_all_as_dicts(cls) -> list[dict]:
        return [{"key": m.key, "name": m.name} for m in cls]
    
    @classmethod
    def get_language_names(cls):
        return [m.name for m in cls]
    
    @classmethod
    def get_language_keys(cls):
        return [m.key for m in cls]
    
    @classmethod
    def from_key(cls, key: str) -> "Languages | None":
        for member in cls:
            if member.key == key:
                return member
        return None
    
    @classmethod
    def from_name(cls, name: str) -> "Languages | None":
        for member in cls:
            if member.name == name:
                return member
        return None
    
    @classmethod
    def get_language_key_by_name(cls, name) -> "str | None":
        language = cls.from_name(name)
        return language.key if language else None
    
    @property
    def key(self) -> str:
        return self.value["key"]
    
    @property
    def name(self) -> str:
        return self.value["name"]
    
def main():
    print(Languages.get_language_names())
    print(Languages.get_language_keys()) 
    print(Languages.get_language_key_by_name("English")) 

main()

    