import sys
sys.path.insert(0, "../../Python")
import Drivers
from JGSL import *
import numpy as np

from helpers import *

if __name__ == "__main__":
    
    knot_type = '4_1'
    braids_directory = '../../../ElasticKnots/data/pickled/scrambled_braids/' + knot_type + '/'
    braids, rod_radii = unpickle_braids(braids_directory)

    num_braids = len([f for f in os.listdir(braids_directory)])
    for braid_idx in range(num_braids):

        sim = Drivers.FEMDiscreteShellBase("double", 3)

        pts = braids[braid_idx]
        rod_radius = rod_radii[braid_idx]
        # pts = pts[0:-1, :]  # drop last duplicated node
        pts = np.vstack((pts, pts[0, :]))  # duplicate first node
        pts[-1, :] += 1e-2*rod_radius*np.ones(3) # slightly perturb last node
        # pts = np.vstack((pts, pts[0, :], pts[1, :]))  # duplicate first and second nodes
        # pts[-2::, :] += 2e0*rod_radius*np.ones(3) # slightly perturb last nodes
        nv = pts.shape[0]

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
        # sim.dt = 1.0
        # sim.frame_dt = 100.0 / 24
        sim.dt = 0.1
        sim.frame_dt = 1.0 / 24
        sim.frame_num = 24
        sim.withCollision = True

        sim.initialize(sim.cloth_density[0], sim.cloth_Ebase[0], 0.4, sim.cloth_thickness[0], 0)
        sim.initialize_rod(p_density=160, E=1e8, bendStiffMult=1, thickness=2*rod_radius)  # TODO: check units
        sim.initialize_OIPC(thickness=0.5*rod_radius, offset=1.99*rod_radius) # thickness is dHat (elastic thickness), offset is xi (hard thickness)

        sim.output_folder = "output/" + os.path.splitext(os.path.basename(sys.argv[0]))[0] + "/" + knot_type + "/" + str(braid_idx) + "/"
        os.makedirs(sim.output_folder, exist_ok=True)

        sim.run()
