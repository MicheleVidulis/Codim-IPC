import numpy as np
from JGSL import Vector3d
import os, pickle

def bounding_box(pts, dx=0.0):
    bbmin = np.min(pts, axis=0)
    bbmax = np.max(pts, axis=0)
    return np.array([bbmin, bbmax]) + np.array([[-dx, -dx, -dx], [dx, dx, dx]])


def relative_bounding_box_from_nodes_indices(nodes, fixed_nodes, dx=1e-5):
    """
    Compute the relative bounding box (vertices in [0, 1]) that surrounds nodes which indices are in fixedPts.
    Expand the resulting (tight) bbox by 2*dx in each coordinate direction.
    """
    box = bounding_box(nodes)
    boxDim = np.diff(box, axis=0).reshape(1, 3)
    fixedBox = bounding_box(nodes[fixed_nodes], dx=dx)
    relBox = (fixedBox - box[0, :]) / boxDim
    relBox_min = Vector3d(relBox[0, 0], relBox[0, 1], relBox[0, 2])
    relBox_max = Vector3d(relBox[1, 0], relBox[1, 1], relBox[1, 2])
    return relBox_min, relBox_max


def unpickle_braids(directory):
    braids = []
    rod_radii = []
    files = [file for file in os.listdir(directory) if file.startswith('centerline-and-radius-')]
    for file in files:
        file_name = directory + file
        unpickled = pickle.load(open(file_name, "rb"))
        braids.append(unpickled[0])
        rod_radii.append(unpickled[1])
    return braids, rod_radii


def define_knot(npts, r=1, Ti=0, Tf=2*np.pi, duplPts=0):
    nSinglePts = npts - duplPts
    # t = np.linspace(Ti, Tf * (nSinglePts-1) / nSinglePts, nSinglePts)  # npts equispaced points
    t = np.linspace(Ti, Tf, nSinglePts)   # npts points, with angular distance between first and last equal to 2*np.pi - Tf + Ti
    t = np.append(t, t[0:duplPts])

    # Trefoil
    # x = lambda t: r * (np.sin(t) + 2*np.sin(2*t))
    # y = lambda t: r * (np.cos(t) - 2*np.cos(2*t))
    # z = lambda t: r * (np.sin(3*t))

    # Figure eight
    x = lambda t: r * (2 + np.cos(2*t))*np.cos(3*t)
    y = lambda t: r * (2 + np.cos(2*t))*np.sin(3*t)
    z = lambda t: r * np.sin(4*t)

    curve = np.zeros((npts, 3))
    curve[:, 0] = x(t)
    curve[:, 1] = y(t)
    curve[:, 2] = z(t)
    return curve