import sys
from utils.utils import load_map, get_map_path
from server.server import create_server

if __name__ == "__main__":
    map_path = get_map_path()
    if map_path:
        map = load_map(map_path)
        server = create_server(map)
        server.launch()
    else:
        print("No file selected.")
        sys.exit(1)