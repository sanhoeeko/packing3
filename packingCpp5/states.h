#pragma once

#include"defs.h"
#include"boundary.h"
#include"my_sparse.h"
#include"sphere_assembly.h"

/*
	Two elements define a state: the configuration and the boundary.
	This structure carries data.
*/
template<int m, int N, typename bt>	// bt:BoundaryType
struct State
{
	Vecf<3 * N>* q;				// generalized coordinates
	bt* boundary;				// pointer of boundary
	SphereAssembly<m>* sa;		// the shape of the particle

	State(bt* boundary_ptr, SphereAssembly<m>* sa) {
		this->boundary = boundary_ptr;
		this->sa = sa;
		this->q = new Vecf<3 * N>();
	}
	State(Vecf<3 * N>* q_ptr, bt* boundary_ptr, SphereAssembly<m>* sa) {
		this->boundary = boundary_ptr;
		this->sa = sa;
		this->q = q_ptr;
	}
};

template<int m, int N> using StateC = State<m, N, BoundaryC>;
template<int m, int N> using StateE = State<m, N, BoundaryE>;


struct DistInfo {
	MySparseMatrix<Triplet>* distpp;
	MySparseVector<TripletB>* distpw;
	bool is_clear = true;

	void clear() {
		distpp->clear(); distpw->clear(); is_clear = true;
	}
};

/*
	This structure does not carry data.
*/
template<int m, int N, typename bt>
struct StateInfo{
	/*
		All except [state] are caches of intermediate results.
		The basic procedure of computation:

		[state]
		   |
		   |	gridLocate
		   v
		[grid] ----> can be used by hessian evaluation
		   |
		   |	collisionDetect
		   v
		[dist] ---calEnergy--> [energy]
		   |
		   |	calGradient
		   v
		[gradient] + [state]
				   |
				   |	classicDescent, ArmijoDescent
				   v
			  [new state]

		When output, only [state] will remain, while caches are cleared.
	*/

	State<m, N, bt>* state = NULL;
	SpaceTransformer<N, m>* transformer = NULL;
	Vecf<2 * N * m>* _sphere_space = NULL;		// access variables start with underline by calling corresponding functions
	Grid* _grid = NULL;					
	DistInfo* _dist = NULL;
	Vecf<3 * N>* gradient = NULL;
	float* _energy = NULL;

	StateInfo() { ; }
	StateInfo(State<m, N, bt>* state) {
		this->state = state;
		this->transformer = new SpaceTransformer<N, m>(state->sa);
	}
	/*
	StateInfo(StateInfo& copy) {
		state = copy.state; transformer = copy.transformer; _grid = copy._grid;
		_dist = copy._dist; gradient = copy.gradient; _energy = copy._energy;
	}*/

	void clearCache() {
		if (_sphere_space) {
			delete _sphere_space; _sphere_space = NULL;
		}
		if (_grid) {
			_grid->clear();
		}
		if (_dist) {
			_dist->clear();
		}
		if (gradient) {
			delete gradient; gradient = NULL;
		}
		if (_energy) {
			delete[] _energy; _energy = NULL;
		}
	}
	Vecf<2 * N * m>* sphereSpace() {
		if (this->_sphere_space == NULL) {
			this->_sphere_space = new Vecf<2 * N * m>(transformer->lift(*(this->state->q)));
		}
		return this->_sphere_space;
	}
	Grid* grid() {
		if (this->_grid == NULL) {
			this->_grid = state->boundary->getGrid();
		}
		return this->_grid;
	}
	DistInfo* dist() {
		if (this->_dist == NULL) {
			this->_dist = new DistInfo();
			_dist->distpp = new MySparseMatrix<Triplet>();
			_dist->distpw = new MySparseVector<TripletB>();
			_dist->distpp->dict.reserve(32 * m * N);
			_dist->distpw->dict.reserve(m * N);
		}
		return this->_dist;
	}
	float energy() {
		return *_energy;
	}
};

template<int m, int N> using StateInfoC = StateInfo<m, N, BoundaryC>;
template<int m, int N> using StateInfoE = StateInfo<m, N, BoundaryE>;
