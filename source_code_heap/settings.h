#pragma once

#define RECORD_TIME

// Enum marcos. It is not allowed to define them as int in linux.
enum class ScalarF { Power, ScreenedColumb, Exp };

#define SCALAR_POTENTIAL_TYPE ScalarF::ScreenedColumb
#define BSHAPE BoundaryC
// #define SAMPLE_NO_EDGE

// Basic options. Varies from one experiment to another.

#define PARTICLE_NUM 1000
#define ASSEMBLY_NUM 17
#define SPHERE_DIST 0.4f
#define BOUNDARY_A 180
#define BOUNDARY_B 180
#define END_BOUNDARY_B 8
#define MAX_COMPRESSION_A 0.4
#define MAX_INIT_ITERATIONS 100000
#define MAX_ITERATIONS 100000
#define MAX_INIT_ITERATIONS_FOR_CIRC 100000
#define FINE_ITERATIONS 1000000


// Fixed parameters. Better determined and optimized before any experiment.

#define ENERGY_RESOLUTION 1000
#define SCALAR_RESOLUTION 24	// significant figures = log10( 2 ^ SCALAR_RESOLUTION )
#define MAX_CONTACT_NUMBER 128	// relates to memory cost
#define CLASSIC_STEP_SIZE 1e-3f
#define FINE_STEP_SIZE 1e-4f
#define ENERGY_EPS 1e-7f
#define EARLY_STOP_COEF 0.1f
#define EARLY_STOP_PATIENCE 10

// depricated

#define COMPRESSION_RATE 0.1
#define NUM_COMPRESSIONS 400
#define OUTPUT_STRIDE 1
#define CEASE_FORCE 5e-2f	// non-zero contact force