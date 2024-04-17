import time
import os
import traceback
import logging
import networkx as nx
import numpy as np
import cvxpy as cp
import opendssdirect as dss
from dataclasses import dataclass, astuple, field
from pprint import pprint

MASTER = "master.dss"
ROOT = os.getcwd()
OUT_DIR = f"{ROOT}/output"
IN_DIR = f"{ROOT}/input"

logging.basicConfig(
    level=logging.DEBUG,
    filename=f"{OUT_DIR}/log.txt",
    filemode='w')
log = logging.getLogger(__name__)


@dataclass
class ComplexPower:
    real: float = 0.0
    imag: float = 0.0

    def __array__(self):
        return np.array(astuple(self))


@dataclass
class PhasePower:
    a: ComplexPower = field(default=ComplexPower())
    b: ComplexPower = field(default=ComplexPower())
    c: ComplexPower = field(default=ComplexPower())

    def __array__(self):
        return np.array(astuple(self))


@dataclass
class PhaseVoltage:
    a: float = field(default=0.0)
    b: float = field(default=0.0)
    c: float = field(default=0.0)

    def __array__(self):
        return np.array(astuple(self))


def dict_to_array(d: dict) -> np.ndarray:
    results = d.values()
    data = list(results)
    return np.array(data)


def get_active_element_power() -> PhasePower:
    w_a = dss.CktElement.Powers()[0]/1000
    w_b = dss.CktElement.Powers()[2]/1000
    w_c = dss.CktElement.Powers()[4]/1000

    var_a = dss.CktElement.Powers()[1]/1000
    var_b = dss.CktElement.Powers()[3]/1000
    var_c = dss.CktElement.Powers()[5]/1000

    return PhasePower(
        a=ComplexPower(w_a, var_a),
        b=ComplexPower(w_b, var_b),
        c=ComplexPower(w_c, var_c)
    )


def get_active_voltage_pu() -> PhaseVoltage:
    kv_a = dss.CktElement.VoltagesMagAng()[0]
    kv_b = dss.CktElement.VoltagesMagAng()[2]
    kv_c = dss.CktElement.VoltagesMagAng()[4]

    bus_name = dss.CktElement.BusNames()
    dss.Circuit.SetActiveBus(bus_name[0])
    kv_base = dss.Bus.kVBase()*1000

    return PhaseVoltage(
        a=kv_a/kv_base,
        b=kv_b/kv_base,
        c=kv_c/kv_base
    )


def create_graph() -> nx.Graph:
    G = nx.Graph()

    dss.Topology.First()
    source_bus, _ = dss.CktElement.BusNames()[0].split('.', 1)
    while (0 != dss.Topology.Next()):
        bus_1, _ = dss.CktElement.BusNames()[0].split('.', 1)
        bus_2, _ = dss.CktElement.BusNames()[1].split('.', 1)
        G.add_edge(bus_1, bus_2)

    return G


def get_bus_distance(phase: int) -> dict:
    dist = {}
    for name in dss.Circuit.AllBusNames():
        dss.Circuit.SetActiveBus(f"{name}")
        if phase in dss.Bus.Nodes():
            index = dss.Bus.Nodes().index(phase)
            re, im = dss.Bus.PuVoltage()[index:index+2]
            D = dss.Bus.Distance()

            dist[dss.Bus.Name()] = D
    return dist


def get_bus_voltage(phase: int) -> dict:
    volts = {}
    for name in dss.Circuit.AllBusNames():
        dss.Circuit.SetActiveBus(f"{name}")
        if phase in dss.Bus.Nodes():
            index = dss.Bus.Nodes().index(phase)
            re, im = dss.Bus.PuVoltage()[index:index+2]
            V = abs(complex(re, im))

            volts[dss.Bus.Name()] = V
    return volts


def get_bus_coords() -> dict:
    pos = {}
    for name in dss.Circuit.AllBusNames():
        dss.Circuit.SetActiveBus(f"{name}")
        pos[dss.Bus.Name()] = [dss.Bus.X(), dss.Bus.Y()]
    return pos


def init() -> None:
    dss.Text.Command(f'Redirect {MASTER}')
    dss.Text.Command(f'Compile {MASTER}')


def change_dir(path: str) -> None:
    os.chdir(path)
    log.debug(f'Working dicrectory: {os.getcwd()}')


class App:
    def __init__(self):
        self.loads = dss.utils.loads_to_dataframe()
        pprint(self.loads)
        self.pecs = dss.utils.pvsystems_to_dataframe()
        pprint(self.pecs)

    def dispatch() -> None:
        pass


if __name__ == "__main__":
    log.debug('OpenDSSDirect.py version: {dss.__version__}')

    model_dir = IN_DIR + "/ieee123/qsts"
    change_dir(model_dir)

    try:

        init()
        app = App()

    except Exception as e:
        print(e)
        print(traceback.format_exc())
