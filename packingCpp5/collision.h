#pragma once

#include"defs.h"
#include"grid.h"
#include"my_sparse.h"
#include <cmath>

template<int m, int N>
void _collisionDetectC(Grid* grid, float* x, MySparseMatrix<m * N, Triplet>* dst) {
	/*
		Given that a particle is in a certain grid,
		it is only possible to collide with particles in that grid or surrounding grids.
	*/
	float* y = x + m * N;
	ivector<int, MAX_CONTACT_NUMBER>* lst = grid->p;

	// set the beginning pointer at the (1,1) cell.
	lst += grid->cols + 1;

	for (int i = 1; i < grid->lines - 1; i++) {
		for (int j = 1; j < grid->cols - 1; j++) {
			// if there is a particle in the grid:
			if (lst->cnt) {
				// for "half-each" surrounding grid (not 9, but 5 cells, including itself):
				// 4 cells that is different from self
				auto pend = lst->end();
				for (int k = 0; k < 4; k++) {
					auto nlst = lst + grid->collision_detect_region[k];
					if (nlst->cnt) {
						// for each particle pair in these two grid:
						auto qend = nlst->end();
						for (auto p = lst->begin(); p < pend; p++) {
							for (auto q = nlst->begin(); q < qend; q++) {
								// if *p, *q are congruent modulo N, they are from the same particle: skip them
								if ((*p - *q) % N == 0)continue;
								float dx = x[*p] - x[*q];
								float dy = y[*p] - y[*q];
								float r2 = dx * dx + dy * dy;
								if (r2 < 4) {
									float r = sqrtf(r2);
									dst->link(*p, *q, r, dx, dy);
								}
							}
						}
					}
				}
				// When and only when collide in one cell, triangular loop must be taken,
				// which ensure that no collision is calculated twice.
				for (auto p = lst->begin(); p < pend; p++) {
					for (auto q = p + 1; q < pend; q++) {
						// if *p, *q are congruent modulo N, they are from the same particle: skip them
						if ((*p - *q) % N == 0)continue;
						float dx = x[*p] - x[*q];
						float dy = y[*p] - y[*q];
						float r2 = dx * dx + dy * dy;
						if (r2 < 4) {
							float r = sqrtf(r2);
							dst->link(*p, *q, r, dx, dy);
						}
					}
				}
			}
			lst++;
		}
		lst += 2;  // if the number of verbose cells on the boundary is 1. 
	}
}

template<int mN>
void _boundaryCollisionDetectC(Boundary* b, float* x, MySparseVector<mN, TripletB>* dst) {
	/*
		Though it is also collision detection, grid is not necessary.
	*/
	float* y = x + mN;
	for (int i = 0; i < mN; i++) {
		float h = b->h(x[i], y[i]);		// call the distance to boundary function
		if (h < 1) {
			dst->link(i, h, x[i], y[i]);
		}
	}
}