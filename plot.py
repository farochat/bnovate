import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from reader import sort_vertices
import os

STATIC_FOLDER = "static"
os.makedirs(STATIC_FOLDER, exist_ok=True)


def polygon(vertices, filename=None):
    # Ensure that the vertices list is not empty
    if not vertices:
        return None

    p = Polygon(sort_vertices(vertices))
    x, y = p.exterior.xy

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(x, y, color="darkred", linestyle="-", linewidth=3)
    ax.set_title(f"Polygon area: {p.area:.2f}")
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 7)

    outfile = os.path.join(STATIC_FOLDER, filename)
    _, ext = os.path.splitext(outfile)
    if not ext:
        outfile += ".png"
        format = "png"

    plt.savefig(outfile, format=format)
    plt.close()

    return outfile
