from typing import Dict, List, Optional


class Furniture:
    def __init__(self):
        self.jid: str = ""
        self.uid: str = ""
        self.category: str = ""

    def from_config(self, description: Dict):
        self.jid = description.get("jid", "")
        self.uid = description.get("uid", "")
        self.category = description.get("category", "")

        return self


class Structure:
    def __init__(self):
        self.jid: str = ""
        self.uid: str = ""
        self.category: str = ""

    def from_config(self, description: Dict):
        self.jid = description.get("jid", "")
        self.uid = description.get("uid", "")
        self.category = description.get("type", "")

        return self


class Room:
    def __init__(self):
        self.id: str = ""
        self.category: str = ""
        self.size: float = 0.0
        self.objects: List[str] = []
        self.furniture: Dict[str, Furniture] = {}
        self.structure: Dict[str, Structure] = {}
        self.missing_furniture: List[str] = []

    def from_config(self, description: Dict, furniture: Optional[Dict[str, Furniture]] = None, structure: Optional[Dict[str, Structure]] = None):
        self.id = description.get("instanceid", "")
        self.category = description.get("type", "")
        self.size = description.get("size", 0.0)
        self.objects = [child["ref"] for child in description.get("children", [])]

        if furniture is not None:
            self.furniture = {}
            for object_reference in self.objects:
                if object_reference in furniture:
                    reference = furniture[object_reference]

                    if reference.category != "":
                        self.furniture[object_reference] = reference
                    else:
                        self.missing_furniture.append(object_reference)
                else:
                    self.missing_furniture.append(object_reference)

        if structure is not None:
            self.structure = {}

            for object_reference in self.objects:
                if object_reference in structure:
                    reference = structure[object_reference]

                    self.structure[object_reference] = reference

        return self


class Scene:
    def __init__(self):
        self.uid: str = ""
        self.furniture: Dict[str, Furniture] = {}
        self.structure: Dict[str, Structure] = {}
        self.rooms: Dict[str, Room] = {}

    def from_config(self, description: Dict):
        self.uid = description["uid"]
        self.furniture = self.parse_furniture(description["furniture"])
        self.structure = self.parse_structure(description["mesh"])
        self.rooms = self.parse_rooms(description["scene"].get("room", []), self.furniture, self.structure)

        return self

    @staticmethod
    def parse_furniture(description: List[Dict]) -> Dict[str, Furniture]:
        furniture_map = {}

        for element in description:
            furniture = Furniture().from_config(element)
            furniture_map[furniture.uid] = furniture

        return furniture_map

    @staticmethod
    def parse_structure(description: List[Dict]) -> Dict[str, Structure]:
        structure_map = {}

        for element in description:
            structure = Structure().from_config(element)
            structure_map[structure.uid] = structure

        return structure_map

    @staticmethod
    def parse_rooms(description: List[Dict], furniture: Optional = None, structure: Optional = None) -> Dict[str, Room]:
        room_map = {}

        for element in description:
            room = Room().from_config(element, furniture, structure)
            room_map[room.id] = room

        return room_map

