#pragma once

#define RECORD_TIME

// If anisotropic type is DoubleSphere, it must be disabled
#define ENABLE_SAT_COLLISION false

// Enum marcos. It is not allowed to define them as int in linux.
enum class ScalarF { Power, Exp };

#define SCALAR_POTENTIAL_TYPE ScalarF::Exp
#define BSHAPE BoundaryC


// Basic options. Varies from one experiment to another.

#define PARTICLE_NUM 100
#define ASSEMBLY_NUM 3
#define INIT_BOUNDARY 12 * 2
#define COMPRESSION_RATE 0.02 * 2
#define NUM_COMPRESSIONS 250
#define OUTPUT_STRIDE 1
#define MAX_INIT_ITERATIONS 40000
#define MAX_ITERATIONS 10000


// Fixed parameters. Better determined and optimized before any experiment.

#define ENERGY_RESOLUTION 1000
#define SCALAR_RESOLUTION 24	// significant figures = log10( 2 ^ SCALAR_RESOLUTION )
#define CLASSIC_STEP_SIZE 1e-3f
#define MAX_STEP_SIZE 0.1f
#define MIN_STEP_SIZE 1e-4f
#define ENERGY_EPS 1e-7f
#define CEASE_FORCE 1e-4f

// Unused

#define ZERO_REPULSION 1e-5f
#define PENALTY_COEFF 1