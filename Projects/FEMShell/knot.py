import sys
sys.path.insert(0, "../../Python")
import Drivers
from JGSL import *
import numpy as np

from helpers import *

if __name__ == "__main__":
    sim = Drivers.FEMDiscreteShellBase("double", 3)

    # Knot
    nv = 100
    rod_radius = 0.05
    pts = define_knot(nv, r=0.5, Ti=0, Tf=2*np.pi, duplPts=0)  # last node is duplicate of first one 
    pts[-1, :] += 1e-8*rod_radius*np.ones(3)  # slightly perturb last node
    sim.make_rod_from_points(pts)

    # Boundary conditions
    fixedPts = [0, 1, nv-2, nv-1]
    relBox_min, relBox_max = relative_bounding_box_from_nodes_indices(pts, fixedPts)
    sim.set_DBC(relBox_min, relBox_max, 
        Vector3d(0, 0, 0), Vector3d(0, 0, 0), Vector3d(0, 0, 0), 0)
    
    # Simulator
    sim.gravity = Vector3d(0, 0, 0) # deactivate gravity
    sim.mu = 0.0                    # deactivate friction

    sim.staticSolve = True  # faster: why? What is it? No intertia? Then dt should not have any effect, but the results change depending on dt
    sim.dt = 0.01
    sim.frame_dt = 1.0 / 24
    # sim.dt = 1.0
    # sim.frame_dt = 100.0 / 24
    sim.frame_num = 24
    sim.withCollision = True

    sim.initialize(sim.cloth_density[0], sim.cloth_Ebase[0], 0.4, sim.cloth_thickness[0], 0)
    sim.initialize_rod(p_density=160, E=1e8, bendStiffMult=1, thickness=2*rod_radius)  # TODO: check units
    sim.initialize_OIPC(thickness=0.5*rod_radius, offset=1.99*rod_radius) # thickness is dHat (elastic thickness), offset is xi (hard thickness)

    sim.outputRod = False # do not save rod<i>.obj files (same as shell<i>.obj but with faces)
    
    sim.run()

    # sim.initialize_gui()
    # for i in range(sim.frame_num):
    #     sim.write_image(i)
    # sim.generate_gif()