#pragma once

#include"states.h"
#include<random>
#include<time.h>
#include<math.h>

#define PI 3.14159265359f

inline float scalar_cross(Eigen::Vector2f& A, Eigen::Vector2f& B) {
	return A(0) * B(1) - A(1) * B(0);
}

/*
	Eliminate interpenetrate case when sampling.
	segment collision detect:
	if not collide: return -1
	if collide: return the ratio (form 0 to 1) in the first segment
*/
inline float segmentCollide(Eigen::Vector2f& A, Eigen::Vector2f& B, Eigen::Vector2f& C, Eigen::Vector2f& D) {
	Eigen::Vector2f AB = B - A;
	Eigen::Vector2f AC = C - A;
	Eigen::Vector2f AD = D - A;
	if (scalar_cross(AB, AC) > 0 == scalar_cross(AB, AD) > 0)return -1;
	Eigen::Vector2f CB = B - C;
	Eigen::Vector2f CD = D - C;
	Eigen::Vector2f CA = -AC;
	float s1 = scalar_cross(CD, CA);
	float s2 = scalar_cross(CD, CB);
	if (s1 > 0 == s2 > 0) {
		return -1;
	}
	else {
		return 1.0f / (1 + std::abs(s2 / s1));
	}
}

/*
	if collide, (implicitly) return the cross point
	if not, return false
*/
inline bool segmentCollide(Eigen::Vector2f& center1, Eigen::Vector2f& center2, 
	float a1, float a2, float semi_major, Eigen::Vector2f& res_center, Eigen::Vector2f& res_v) 
{
	Eigen::Vector2f u1 = semi_major * Eigen::Vector2f(cos(a1), sin(a1));
	Eigen::Vector2f u2 = semi_major * Eigen::Vector2f(cos(a2), sin(a2));
	Eigen::Vector2f p11 = center1 + u1, p12 = center1 - u1;
	Eigen::Vector2f p21 = center2 + u2, p22 = center2 - u2;
	float ratio = segmentCollide(p11, p12, p21, p22);
	if (ratio != -1) {
		res_center = center1 + (2 * ratio - 1) * u1;
		Eigen::Vector2f u_ave = u1 + u2; u_ave.normalize();
		res_v(0) = -u_ave(1); res_v(1) = u_ave(0);
		return true;
	}
	return false;
}

/*
	if there is not any interpenetration, return false
	use Eigen::MatrixXf to avoid stack overflow 
	(you can manually enlarge the stack, but Eigen still raises static assertion fails)
*/
template<int N>
bool cancelPenetrate(Vecf<3 * N>& q, float semi_major, float semi_minor) {
	bool flag = false;
	float center_dist_4sq = 4 * semi_major * semi_major;
	Vecf<N> x = q.template head<N>(), y = q.template segment<N>(N), a = q.template tail<N>();
	Eigen::MatrixXf dx = x.replicate(1, N) - x.replicate(1, N).transpose();
	Eigen::MatrixXf dy = y.replicate(1, N) - y.replicate(1, N).transpose();
	Eigen::MatrixXf rij2 = dx.cwiseProduct(dx) + dy.cwiseProduct(dy);
	for (int i = 0; i < N; i++) {
		for (int j = i + 1; j < N; j++) {
			if (rij2(i, j) < center_dist_4sq) {
				Eigen::Vector2f c1(x(i), y(i)); Eigen::Vector2f c2(x(j), y(j));
				Eigen::Vector2f cross_point;
				Eigen::Vector2f v;
				if (segmentCollide(c1, c2, a(i), a(j), semi_major, cross_point, v)) {
					flag = true;
					Eigen::Vector2f new_center1 = cross_point + semi_minor * v;
					Eigen::Vector2f new_center2 = cross_point - semi_minor * v;
					float new_orientation = atan2f(-v(1), v(0));
					q(i) = new_center1(0); q(i + N) = new_center1(1); q(i + 2 * N) = new_orientation;
					q(j) = new_center2(0); q(j + N) = new_center2(1); q(j + 2 * N) = new_orientation;
				}
			}
		}
	}
	return flag;
}

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

template<int m, int N> void RandomInit(StateC<m, N>* state) {
	randomInitSC<N>(state->q->data(), state->boundary->radius);
}
template<int m, int N> void RandomInit(StateE<m, N>* state) {
	randomInitSE<N>(state->q->data(), state->boundary->a, state->boundary->b);
}