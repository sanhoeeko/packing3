from project_replica import newExperiment

# main script: execute this to invoke Cpp
# for convenience, useful settings are listed here:
"""
PARTICLE_NUM: int = 100     ASSEMBLY_NUM: int           SPHERE_DIST: float = 1.0f   BOUNDARY_A: float
COMPRESSION_RATE: float     NUM_COMPRESSIONS: int       OUTPUT_STRIDE: int = 1      BOUNDARY_B: float
MAX_ITERATIONS: int = 10000                             MAX_INIT_ITERATIONS: int = 20000
SCALAR_POTENTIAL_TYPE: str (ScalarF::Power | ScalarF::Exp)
BSHAPE: str (BoundaryC | BoundaryE)
"""

newExperiment(PARTICLE_NUM=1000, ASSEMBLY_NUM=7, BOUNDARY_A=179, BOUNDARY_B=179, COMPRESSION_RATE=0.08,
              NUM_COMPRESSION=800, MAX_ITERATIONS=100000, MAX_INIT_ITERATIONS=100000,
              SCALAR_POTENTIAL_TYPE="ScalarF::Exp", BSHAPE="BoundaryC")

newExperiment(PARTICLE_NUM=1000, ASSEMBLY_NUM=7, BOUNDARY_A=269, BOUNDARY_B=119, COMPRESSION_RATE=0.08,
              NUM_COMPRESSION=800, MAX_ITERATIONS=100000, MAX_INIT_ITERATIONS=100000,
              SCALAR_POTENTIAL_TYPE="ScalarF::Exp", BSHAPE="BoundaryE")
