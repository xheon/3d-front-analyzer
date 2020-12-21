import json
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path
from typing import List, Dict, Set, Optional

from tqdm import tqdm

from scene import Scene, Furniture


class Analyzer:
    def __init__(self, is_debug: bool = False):
        self.scenes: Dict[str, Scene] = {}
        self.shapes: Set[str] = set()
        self.is_debug = is_debug
        self.available_scene_objects = set()
        self.shape_category_info: List[Dict] = []
        self.category_super_category_mapping: Dict[str, str] = {}

    def parse_houses(self, dataset_path: Path, num_scenes: Optional[int] = None):
        # scene_list = []
        file_paths = [file for file in dataset_path.iterdir() if file.is_file() and file.suffix == ".json"][:num_scenes]

        if self.is_debug:
            num_workers = 1
        else:
            num_workers = 12

        with Pool(num_workers) as pool:
            with tqdm(total=len(file_paths), desc="Parsing scenes") as pbar:
                for scene in pool.imap_unordered(self.parse_scene, file_paths, 1):
                    self.scenes[scene.uid] = scene
                    pbar.update()

            # scene_list = pool.imap_unordered(self.parse_scene, file_paths, 1)
        # self.scenes = {s.uid: s for s in scene_list}
        # for path in tqdm(file_paths, desc="Parsing scenes"):
        #     scene = self.parse_scene(path)
        #     scenes[path.stem] = scene

    @staticmethod
    def parse_scene(file_path: Path) -> Scene:
        scene = Scene()

        try:
            with open(file_path) as f:
                content = json.load(f)
            scene = scene.from_config(content)
        except UnicodeError:
            print(f"Error while parsing {file_path}")

        return scene

    def parse_shapes(self, dataset_path: Path):
        self.shapes = set([folder.name for folder in dataset_path.iterdir() if folder.is_dir()])

    def parse_shape_categories(self, file_path: Path):
        with open(file_path) as f:
            self.shape_category_info = json.load(f)

        self.category_super_category_mapping = {}
        for category_info in self.shape_category_info:
            category = category_info["category"]
            super_category = category_info["super-category"]
            self.category_super_category_mapping[category] = super_category

    @staticmethod
    def get_scene_furniture(scenes: Dict[str, Scene]) -> List[Furniture]:
        objects = []

        for scene in scenes.values():
            # iterate over all rooms
            for room in scene.rooms.values():
                # iterate over all (existing) objects
                for obj in room.furniture.values():
                    objects.append(obj)

        return objects

    def collect_available_scene_furniture(self):
        objects = self.get_scene_furniture(self.scenes)

        for obj in objects:
            if obj.jid in self.shapes:
                self.available_scene_objects.add(obj)

    def get_unique_categories(self) -> Set[str]:
        categories = set()
        # iterate over all scenes
        for obj in self.get_scene_furniture(self.scenes):
            category = obj.category
            categories.add(category)

        return categories

    def get_unique_categories_of_available_objects(self) -> Set[str]:
        categories = set()

        for obj in self.available_scene_objects:
            category = obj.category
            categories.add(category)

        return categories

    def get_unique_available_objects(self) -> Set[str]:
        objects = set()

        for obj in self.available_scene_objects:
            objects.add(obj.jid)

        return objects

    def get_unique_available_objects_by_category(self) -> Dict[str, set]:
        objects_per_category = defaultdict(set)

        for obj in self.available_scene_objects:
            objects_per_category[obj.category].add(obj.jid)

        return objects_per_category

    def get_unique_available_objects_by_super_category(self) -> Dict[str, set]:
        objects_by_category = self.get_unique_available_objects_by_category()

        by_super_category = defaultdict(set)

        for category, objects in objects_by_category.items():
            if category not in self.category_super_category_mapping:
                print(f"Missing super-category for: {category}")
            super_category = self.category_super_category_mapping.get(category, "missing")
            by_super_category[super_category].update(objects)

        return by_super_category

    def get_rooms_by_room_type(self, non_empty: bool = False) -> Dict[str, int]:
        by_room_type = defaultdict(lambda: 0)

        for scene in self.scenes.values():
            for room in scene.rooms.values():
                if non_empty:
                    if len(room.furniture) > 0:
                        by_room_type[room.category] += 1
                else:
                    by_room_type[room.category] += 1

        return by_room_type

    def get_room_types_for_scene_list(self, scene_list: str) -> Dict[str, int]:
        pass

    def get_rooms_with_multiple_floors(self):
        rooms_with_multiple_floors = set()

        total_rooms = 0

        for scene_name, scene in self.scenes.items():
            for room_name, room in scene.rooms.items():
                floor_counter = 0
                total_rooms += 1
                for el in room.structure.values():
                    if el.category == "Floor":
                        floor_counter += 1

                if floor_counter > 2:
                    key = f"{scene_name}/{room_name}"
                    rooms_with_multiple_floors.add(key)

        print(total_rooms)

        return rooms_with_multiple_floors
