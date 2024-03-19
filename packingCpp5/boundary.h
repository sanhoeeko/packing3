#pragma once

#include"grid.h"
#include"solver.h"

const float particle_radius = 1 + (float)(ASSEMBLY_NUM - 1) / 2 * SPHERE_DIST;

class Boundary {
public:
	float initial_scalar_radius;
	float scalar_radius;

	virtual Grid* getGrid() = 0;
	virtual void step(float compression_rate) = 0;
	virtual float h(float x, float y) = 0;
	void define_scalar_radius(float r);
};

class BoundaryC : public Boundary {
public:
	float radius;

	BoundaryC(float initial_radius, float _);
	Grid* getGrid();
	void step(float compression_rate);
	float h(float x, float y);
};

class BoundaryE : public Boundary {
public:
	float a, b;
	float aspect_ratio;
	BESolver sol;

	BoundaryE(float a, float b);
	Grid* getGrid();
	void step(float compression_rate);
	float h(float x, float y);
};
