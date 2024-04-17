import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame


def create_line_graph(phase=1):
    G = nx.Graph()

    df = dss.utils.lines_to_dataframe()
    data = df[['Bus1', 'Bus2']].to_dict(orient="index")

    for name in data:
        line = data[name]
        if f".{phase}" in line["Bus1"] and f".{phase}" in line["Bus2"]:
            G.add_edge(line["Bus1"].split(".")[0], line["Bus2"].split(".")[0])

    pos = {}
    for name in dss.Circuit.AllBusNames():
        dss.Circuit.SetActiveBus(f"{name}")
        if phase in dss.Bus.Nodes():
            index = dss.Bus.Nodes().index(phase)
            re, im = dss.Bus.PuVoltage()[index:index+2]
            V = abs(complex(re, im))
            D = dss.Bus.Distance()

            pos[dss.Bus.Name()] = (D, V)
    return G, pos


def plot_graph(name: str) -> None:
    G = create_graph()
    pos = get_bus_coords()
    voltages = get_bus_voltage(1)

    # settings
    cmap = plt.cm.plasma

    # nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=2,
        nodelist=list(voltages.keys()),
        node_color=list(voltages.values()),
        cmap=cmap)

    # node labels
    # nx.draw_networkx_labels(G, pos, font_size=1, font_family="sans-serif")

    # edges
    nx.draw_networkx_edges(G, pos, width=1, alpha=0.4)

    # Colorbar
    vmin = min(voltages.values())
    vmax = max(voltages.values())
    cobj = plt.cm.ScalarMappable(cmap=cmap)
    cobj.set_clim(vmin=vmin, vmax=vmax)

    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()
    plt.colorbar(cobj, ax=ax, orientation='vertical')
    plt.savefig(f"{OUT_DIR}/{name}_voltage_graph.png", dpi=400)


def plot_voltage_tree() -> None:
    G, pos = create_line_graph()

    fig, ax = plt.subplots()
    ax.grid()
    ax.set_ylabel("Voltage in p.u.")
    ax.set_xlabel("Distances in km")
    plt.tight_layout()

    # nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=0)

    # node labels
    # nx.draw_networkx_labels(G, pos, font_size=1, font_family="sans-serif")

    # edges
    nx.draw_networkx_edges(G, pos, ax=ax)
    plt.savefig(f"{OUT_DIR}/voltage_tree.png", dpi=400)


def plot_profiles() -> None:
    load = read_csv(LOAD_SHAPE)
    solar = read_csv(PV_SHAPE)

    fig, ax = plt.subplots()

    ax.plot(solar, label='Solar')
    ax.plot(load, label='Load')

    ax.set(xlabel='Time (5 min)', ylabel='Output (%)')
    fig.legend()
    plt.savefig(f'{OUT_DIR}/profiles.png', dpi=400)


if __name__ == "__main__":
    pass
