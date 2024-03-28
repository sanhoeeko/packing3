#pragma once

#define RECORD_TIME

// Enum marcos. It is not allowed to define them as int in linux.
enum class ScalarF { Power, ScreenedColumb, Exp };

#define SCALAR_POTENTIAL_TYPE ScalarF::ScreenedColumb
#define BSHAPE BoundaryE
// #define SAMPLE_NO_EDGE

// Basic options. Varies from one experiment to another.

#define PARTICLE_NUM 200
#define ASSEMBLY_NUM 1
#define SPHERE_DIST 1.0f
#define BOUNDARY_A 25
#define BOUNDARY_B 25
#define END_BOUNDARY_B 16
#define COMPRESSION_RATE 0.05
#define MAX_INIT_ITERATIONS 20000
#define MAX_ITERATIONS 20000
#define FINE_ITERATIONS 1000000


// Fixed parameters. Better determined and optimized before any experiment.

#define ENERGY_RESOLUTION 1000
#define SCALAR_RESOLUTION 24	// significant figures = log10( 2 ^ SCALAR_RESOLUTION )
#define MAX_CONTACT_NUMBER 32	// relates to memory cost
#define CLASSIC_STEP_SIZE 1e-3f
#define FINE_STEP_SIZE 1e-4f
#define ENERGY_EPS 1e-7f
#define EARLY_STOP_COEF 0.01f
#define EARLY_STOP_PATIENCE 10

// depricated

#define NUM_COMPRESSIONS 400
#define OUTPUT_STRIDE 1
#define CEASE_FORCE 5e-2f	// non-zero contact force