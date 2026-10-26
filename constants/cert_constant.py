from enum import Enum

class CertificateType(Enum):
    ISTQB = [
        {"key": "CTFL", "name": "Certified Tester Foundation Level 4.0", "description": "The ISTQB® Certified Tester Foundation Level 4.0 (CTFL 4.0) certification provides essential testing knowledge that can be put to practical use as well as the terminology and concepts used worldwide in the testing domain. The CTFL 4.0 certification is relevant across software delivery approaches and practices whether Agile, Waterfall or DevOps with continuous integration, continuous delivery and continuous testing."},
        {"key":"CTAI", "name": "Certified Tester AI Testing v2.0", "description": "The ISTQB® Certified Tester AI Testing v2.0 (CT-AI) certification provides a comprehensive introduction to testing AI-based systems, with a primary focus on machine learning and including key concepts and testing approaches for generative AI."},
    ]

    @classmethod
    def get_certificates(cls) -> list["CertificateType"]:
        return list(cls)
    
    @classmethod
    def get_names(cls) -> list[str]:
        return [ct.name for ct in cls]
    
    @classmethod
    def get_values(cls) -> list[list[dict]]:
        return [ct.value for ct in cls]
    
    @classmethod
    def get_all_items(cls) -> list[dict]:
        return [item for ct in cls for item in ct.value]

    @classmethod
    def as_dict(cls) -> dict[str, list[dict]]:
        return {ct.name: ct.value for ct in cls}

    @classmethod
    def from_name(cls, name: str) -> "CertificateType":
        """Lookup by name, case-insensitive, raises ValueError if unknown."""
        try:
            return cls[name.upper()]
        except KeyError:
            valid = ", ".join(cls.__members__)
            raise ValueError(f"Unknown certificate type '{name}'. Valid: {valid}") from None
    
    @property
    def items(self) -> list[dict]:
        return self.value
    
    def get_all_names(self) -> list[str]:
        return [item["name"] for item in self.value]
    
    def get_all_keys(self) -> list[str]:
        return [item["key"] for item in self.value]
    
    def get_by_key(self, key:str) -> dict | None:
        for item in self.value:
            if item["key"] == key:
                return item
        return None
    
    def get_by_key_name(self, key: str) -> str | None:
        item = self.get_by_key(key)
        return item["name"] if item else None
    
    def get_description_by_key(self, key:str) -> dict | None:
        item = self.get_by_key(key)
        return item["description"] if item else None

    
if __name__ == "__main__":
    name = "ISTQB"                     # comes from a string input
    certs = CertificateType.from_name(name).items
    for item_idx, item in enumerate(certs):
        # print (f"item_idx: {item_idx}")
        # print (f"item: {item}")
        print(item["description"])

