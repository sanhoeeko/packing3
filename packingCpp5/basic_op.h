#pragma once

#include"states.h"
#include"collision.h"
#include"sampling.h"
#include"scalar_func.h"

inline bool is_bad_data(float& x) {
	return std::isnan(x) || std::isinf(x);
}
template<int dN>
bool checkDataIntegration(Vecf<dN>* v) {
	float* ptr = v->data();
	float* pend = ptr + dN;
	for (; ptr < pend; ptr++) {
		if (is_bad_data(*ptr))return false;
	}
	return true;
}

/*
	Functions that starts with uppercase letters are interfaces.
	LRU cache is used, so call them for free.
*/

template<int m, int N, typename bt>
Grid* GridLocate(StateInfo<m, N, bt>& state_info) {
	if (state_info.grid()->is_clear) {
		_gridLocate<m * N>(state_info.grid(), state_info.sphereSpace()->data());
	}
	return state_info.grid();
}

/*
	Note: collisions are detected in the 2Nm space.
*/
template<int m, int N, typename bt>
void _collisionC(DistInfo* rs, Grid* grid, bt* b, float* px) {
	/*
		px: input data: must be .data() of a vector in the 2Nm space
		[rs->distpp], [rs->distpw] are also in the 2Nm space
	*/
	_collisionDetectC<m, N>(grid, px, rs->distpp);
	_boundaryCollisionDetectC<m * N>(b, px, rs->distpw);
}

template<int m, int N, typename bt>
DistInfo* Collision(StateInfo<m, N, bt>& state_info) {
	if (state_info.dist()->is_clear) {
		_collisionC<m, N, bt>(state_info.dist(), GridLocate(state_info), 
			state_info.state->boundary, state_info.sphereSpace()->data());
	}
	return state_info.dist();
}

float _calEnergy_from_dist(DistInfo* rs) {
	// use Eigen vectorization to accelerate loops
	static auto lambda_pp = [](float r)->float {return V.pp(r); };
	static auto lambda_pw = [](float h)->float {return V.pw(h); };

	float energy_pp = rs->distpp->get_r_array().unaryViewExpr(lambda_pp).sum();
	float energy_pw = rs->distpw->get_h_array().unaryViewExpr(lambda_pw).sum();

	return energy_pp + energy_pw;
}

Eigen::Vector2f singleForcePP(Triplet& rxy) {
	float fr = V.dpp_r(rxy.r);
	return { fr * rxy.x,fr * rxy.y };
}

Eigen::Vector2f singleForcePW(TripletB& hxy) {
	float r = sqrt(hxy.x * hxy.x + hxy.y * hxy.y);
	float fr = V.dpw(hxy.h) / r;
	return { fr * hxy.x,fr * hxy.y };
}

template<int m, int N, typename bt>
Vecf<2 * N * m> _calForce_from_dist(DistInfo* rs, SphereAssembly<m>* sa) {
	static auto fpp = std::function<Eigen::Vector2f(Triplet&)>(singleForcePP);
	static auto fpw = std::function<Eigen::Vector2f(TripletB&)>(singleForcePW);
	// particle-particle force
	Vecf<2 * N * m> forces_pp = rs->distpp->apply(fpp).rowwiseSumAsym().template toVector<N, m>();
	// particle-wall force
	Vecf<2 * N * m> forces_pw = rs->distpw->apply(fpw).template toVector<N, m>();
	Vecf<2 * N * m> forces = forces_pp + forces_pw;
	return forces;
}

template<int m, int N, typename bt>
Vecf<3 * N>* CalGradient(StateInfo<m, N, bt>& state_info) {
	if (state_info.gradient == NULL) {
		Vecf<2 * N * m> temp = _calForce_from_dist<m, N, bt>(Collision(state_info), state_info.state->sa);
		state_info.gradient = new Vecf<3 * N>(state_info.transformer->project(temp));
	}
	return state_info.gradient;
}

template<int m, int N, typename bt>
float CalEnergy(StateInfo<m, N, bt>& state_info) {
	if (state_info._energy == NULL) {
		state_info._energy = new float[1];
		*(state_info._energy) = _calEnergy_from_dist(Collision(state_info));
	}
	return state_info.energy();
}

// Descent method has no slot functions, so here is it.
template<int m, int N, typename bt>
void Descent(StateInfo<m, N, bt>& state_info, float step_size) {
	(*state_info.state->q) -= step_size * (*state_info.gradient);
}

// initialization of a state object
template<int m, int N, typename bt>
StateInfo<m, N, bt> CreateRandomState(float initial_boundary_a, float initial_boundary_b) {
	bt* b = new bt(initial_boundary_a, initial_boundary_b);
	SphereChain<m>* sphere_chain = new SphereChain<m>(1.0f);
	State<m, N, bt>* state = new State<m, N, bt>(b, sphere_chain);
	RandomInit<m, N, bt>(state);
	return StateInfo<m, N, bt>(state);
}

// Step interface. It seems to have two slot functions. However, they can be deduced from known template parameters!
// So it has no slot functions, too.

template<int m, int N, typename bt>
float Step(StateInfo<m, N, bt>& state_info, float step_size) {
	state_info.clearCache();
	CalGradient(state_info);
	Descent(state_info, step_size);
	return CalEnergy(state_info);
}

// GradientNorm interface

template<int N>
Vecf<N> GradientNorm(Vecf<3 * N>* g) {
	Eigen::Ref<Vecf<N>> g1 = g->template head<N>();
	Eigen::Ref<Vecf<N>> g2 = g->template segment<N>(N);
	Eigen::Ref<Vecf<N>> g3 = g->template tail<N>();
	Vecf<N> res = (g1.cwiseProduct(g1) + g2.cwiseProduct(g2) + g3.cwiseProduct(g3)).cwiseSqrt();
	return res;
}

template<int N>
float GradientMaxAbs(Vecf<3 * N>* g) {
	return GradientNorm<N>(g).maxCoeff();
}