#pragma once

#include"defs.h"
#include"ivector.h"

class Grid { public:
	/*
		This class is for locating particles.
	*/
	bool is_clear;
	ivector<int, MAX_CONTACT_NUMBER>* p;
	float a;									// the "lattice constant" of the grid
	int m, n;									// number of efficient cells of a half axis
	int xshift, yshift;							// number of cells of a half axis
	int lines, cols;							// number of cells of each line of the grid
	int size;									// lines * cols
	int* collision_detect_region;				// only 5 cells (including self) are taken into account 
												// in the collision detection of a cell.

	Grid(float cell_size, float boundary_a, float boundary_b);
	int xlocate(float x);
	int ylocate(float y);
	void add(int i, int j, int particle_id);
	ivector<int, MAX_CONTACT_NUMBER>* loc(int i, int j);
	void clear();
};

/*
	Determine what grid cell a particle is in.

	Note that only x and y are required in the class [Particle],
	and the covering rectangle are required in the class [Boundary],
	which means that this method is independent of the shape of either particles or the boundary.
*/
template<int N>
void _gridLocate(Grid* grid, float* px) {
	/*
		Only DOF x and y are considered. The third DOF, if there is, is omitted.
	*/
	float* py = px + N;
	for (int cnt = 0; cnt < N; cnt++) {
		int i = grid->xlocate(px[cnt]);
		int j = grid->ylocate(py[cnt]);
		grid->add(i, j, cnt);
	}
	grid->is_clear = false;
}