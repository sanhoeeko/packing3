#pragma once

#include"states.h"
#include<random>
#include<time.h>
#include<math.h>

#define PI 3.14159265359f

inline float randf() {
	return (float)rand() / RAND_MAX;
}

template<int N>
void randomInitSC(float* x, float boundary_radius) {
	srand(time(0));
	float* xptr = x;
	float* xend = x + N;
	float* yptr = xend;
	float* theta_ptr = x + 2 * N;
	while (xptr < xend) {
		float r = boundary_radius * sqrt(randf());
		float phi = randf() * (2 * PI);
		float theta = randf() * (2 * PI);
		*xptr++ = r * cos(phi);
		*yptr++ = r * sin(phi);
		*theta_ptr++ = theta;
	}
}

template<int N>
void x_affine(float* x, float aspect_ratio) {
	for (int i = 0; i < N; i++) {
		x[i] *= aspect_ratio;
	}
}

template<int N>
void randomInitSE(float* x, float a, float b) {
	float aspect_ratio = a / b;
	randomInitSC<N>(x, b);
	x_affine<N>(x, aspect_ratio);
}

// Interfaces

template<int m, int N, typename bt>
void RandomInit(State<m, N, bt>* state);

template<int m, int N, typename bt> void RandomInit(StateC<m, N>* state) {
	randomInitSC<N>(state->q->data(), state->boundary->radius);
}
template<int m, int N, typename bt> void RandomInit(StateE<m, N>* state) {
	randomInitSE<N>(state->q->data(), state->boundary->b);
}