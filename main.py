from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
from tabulate import tabulate

from analyzer import Analyzer


def main(opts):
    # 3D-Front
    analyzer = Analyzer(is_debug=False)
    analyzer.parse_houses(Path(opts.house_path), num_scenes=None)
    analyzer.parse_shapes(Path(opts.shape_path))
    analyzer.parse_shape_categories(Path("resources/category_mapping.json"))
    analyzer.collect_available_scene_furniture()

    # shape_analysis(analyzer)
    # scene_analysis(analyzer)
    room_analysis(analyzer)


def shape_analysis(analyzer):
    # Shape analysis
    unique_categories = analyzer.get_unique_categories()
    print("Unique categories", len(unique_categories))

    unique_categories_available = analyzer.get_unique_categories_of_available_objects()
    print("Unique available categories", len(unique_categories_available))

    unique_objects = analyzer.get_scene_furniture(analyzer.scenes)
    print("Unique objects", len(unique_objects))

    unique_available_objects = analyzer.get_unique_available_objects()
    print("Unique available objects", len(unique_available_objects))

    # By category
    unique_objects_by_category = analyzer.get_unique_available_objects_by_category()
    print("Unique available objects by category")
    # entries = [[len(category) for category in unique_objects_by_category.values()]]
    # headers = ["\n".join([c.strip() for c in category.split("/")]) for category in unique_objects_by_category.keys()]
    entries = sorted([[k, len(v)] for k, v in unique_objects_by_category.items()], key=lambda x: x[1], reverse=True)
    headers = ["category", "#objects"]
    print(tabulate(entries, headers=headers, tablefmt="github"))

    # By super-categories
    unique_objects_by_super_category = analyzer.get_unique_available_objects_by_super_category()
    print("Unique available objects by super-category")
    # entries = [[len(category) for category in unique_objects_by_category.values()]]
    # headers = ["\n".join([c.strip() for c in category.split("/")]) for category in unique_objects_by_category.keys()]
    entries = sorted([[k, len(v)] for k, v in unique_objects_by_super_category.items()], key=lambda x: x[1],
                     reverse=True)
    headers = ["super-category", "#objects"]
    print(tabulate(entries, headers=headers, tablefmt="github"))


def scene_analysis(analyzer):
    print("All rooms")
    by_room_type = analyzer.get_rooms_by_room_type()
    entries = sorted([[k, v] for k, v in by_room_type.items()], key=lambda x: x[1], reverse=True)
    headers = ["Type", "#rooms"]
    print(tabulate(entries, headers=headers, tablefmt="github"))

    print("All non-empty rooms")
    by_room_type = analyzer.get_rooms_by_room_type(non_empty=True)
    entries = sorted([[k, v] for k, v in by_room_type.items()], key=lambda x: x[1], reverse=True)
    headers = ["Type", "#rooms"]
    print(tabulate(entries, headers=headers, tablefmt="github"))


def room_analysis(analyzer):
    rooms_with_multiple_floors = analyzer.get_rooms_with_multiple_floors()

    print(len(rooms_with_multiple_floors))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--house-path", type=str)
    parser.add_argument("--shape-path", type=str)
    args = parser.parse_args()

    main(args)
