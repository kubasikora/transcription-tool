import numpy as np
from matplotlib.patches import Wedge
import matplotlib.pyplot as plt
import svgutils.compose as sc
import os, argparse, json


def draw_single_pie(center, r, acc, ax, colors=('k', 'k', 'k'), id="", plot_labels=True):
    """Draws single pie plot in given position
    Args:
        center - position of center of the plot
        r - radius of the plot
        acc - data to be presented on the plot
        ax - handle to axis object where the plot should be drawn
        colors - tuple of colors of the plot's wedges
        id - label of the plot
        plot_labels - should draw the label next to the plot
    """

    if ax is None:
        ax = plt.gca()

    theta1 = 360*acc[0] / 100
    theta2 = theta1 + 360*acc[1] / 100
    ax.add_artist(Wedge(center, r, 0, 360, fc=None, edgecolor='k'))
    ax.add_artist(Wedge(center, r, 0, theta1, fc=colors[0]))
    ax.add_artist(Wedge(center, r, theta1, theta2, fc=colors[1]))
    ax.add_artist(Wedge(center, r, theta2, 360, fc=colors[2]))

    if plot_labels:
        ax.text(center[0] + 1.2 * r, center[1] + 0.9*r, "{:d}%".format(int(acc[0])), verticalalignment='center', fontsize=9)
        ax.text(center[0] + 1.2 * r, center[1], "{:d}%".format(int(acc[1])), verticalalignment='center', fontsize=9)
        ax.text(center[0] + 1.2 * r, center[1] - 0.9*r, "{:d}%".format(int(acc[2])), verticalalignment='center', fontsize=9)
        ax.text(center[0] - 1.2 * r, center[1], id, horizontalalignment="right", verticalalignment='center', fontsize=16)


def draw_plot(data, output):
    """Draws piecharts from given data on lab012 background
    Args:
        data - list of lists of three points with experiment results
        output - name of generated svg file
    """

    positions = [
        [1.6, 1], [1.6, 3], [1.6, 5], [5, 1],
        [5,	3], [5,	5], [8.7, 1], [8.7, 3],
        [8.7, 5], [12, 1], [12, 3], [12, 5]
    ]

    # prepare background
    fig, ax = plt.subplots()
    ax.imshow([[[0,0,0,0]], [[0,0,0,0]]], extent = [-1, 13.25, -1, 7.3])
    ax.patch.set_alpha(0.0)
    ax.axis('off')

    # robot blob
    draw_single_pie([1.3, 5.7], 0.3, [1,1,1], ax, ('k', 'k', 'k'), plot_labels=False)
    ax.text(1.6, 5.9, "Mikrofon")

    # draw points
    for i,d in enumerate(zip(positions, data)):
        draw_single_pie(d[0], 0.5, d[1], ax, ('green', 'orange', 'blue'), str(i+1))

    # save
    fig.tight_layout()
    fig.savefig("out.svg", dpi=200, transparent=True)

    # merge with proper background
    sc.Figure("247.59521mm", "129.31232mm",  
        sc.Panel(sc.SVG("./assets/012-base.svg").scale(0.352)),
        sc.Panel(sc.SVG("out.svg").scale(0.6).move(-25,-40))
    ).save(output)
    os.remove("./out.svg")


if __name__ == "__main__":
    # get arguments
    parser = argparse.ArgumentParser(description="Plot results over experiment background")
    parser.add_argument('input', metavar='input', type=str, help='Input json file with experiment results')
    parser.add_argument('-o', '--output', default='fig.pdf', metavar='filename', type=str, help='Output file name')
    args = parser.parse_args()

    # load data file
    with open(args.input, "r") as file:
        data = json.load(file)

    # draw figure
    output = "output.svg"
    draw_plot(data, output)
    os.system(f"inkscape --export-filename={args.output} {output}")
    os.remove(output)
