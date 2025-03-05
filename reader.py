import itertools

import numpy as np
import pandas as pd
from shapely.geometry import Polygon


def read_csv(fpath):
    """Parse csv, validates it and return polygon vertices."""
    delimiter = get_delimiter(fpath)
    df = pd.read_csv(fpath, delimiter=delimiter)

    if not all(col in df.columns for col in ["x", "y"]):
        raise ValueError("File must contain 'x' and 'y' columns.")

    return list(zip(df.x, df.y))


def get_delimiter(fpath):
    """Get majority separator (, or ;) from first 100 lines."""
    data = "".join(first_n_lines(fpath, 100))
    if data.count(";") > data.count(","):
        return ";"
    return ","


def first_n_lines(fpath, n=20):
    """Extract first n lines of a file."""
    with open(fpath, encoding="utf-8", errors="replace") as fp:
        return [line.strip() for line in itertools.islice(fp, n)]


def is_valid_polygon(vertices):
    """Check validity of a polygon based on its vertices.

    Rules:
    - Polygon should have at least 3 unique points.
    - Polygon should not have redundant vertices.
    - Polygon should not have intersecting edges.
    """
    if len(vertices) < 3:
        stdout = "Polygon should have at least 3 unique points."
        return False, stdout

    vertices = sort_vertices(vertices)
    # Check for redundancies
    polygon = Polygon(vertices)
    n_vertex = len(polygon.exterior.coords)
    polygon_simple = polygon.simplify(0, preserve_topology=False)
    n_vertex_simple = len(polygon_simple.exterior.coords)
    if n_vertex != n_vertex_simple:
        stdout = "Polygon shouldn't have redundant points."
        return False, stdout

    # Finally check for overall validity
    stdout = "Polygon is valid" if polygon.is_valid else "Polygon is not valid."
    return polygon.is_valid, stdout


def sort_vertices(vertices):
    """Sort vertices in counter-clockwise direction."""
    # Calculate the centroid of the polygon
    centroid = np.array(Polygon(vertices).centroid.coords)
    vertices = np.array(vertices)
    diff_center = vertices - centroid
    return vertices[np.atan2(diff_center[:, 1], diff_center[:, 0]).argsort()]
