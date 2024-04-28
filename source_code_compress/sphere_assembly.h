#pragma once

#include"defs.h"

const float inertia = 1.0;

template<int m>
using Pos2d = Eigen::Matrix<float, 2, m>;

template<int m>
struct SphereAssembly {
	/*
		Definition of relative positions of spheres:
		[ x1, x2, ... xm ]
		[ y1, y2, ... ym ]
	*/
	Pos2d<m> pos;

	Vecf<2 * m> toCross() {
		// return [-y | x] (column vector)
		Vecf<2 * m> res;
		res.template head<m>() = -pos.row(1); res.template tail<m>() = pos.row(0);
		return res;
	}
};

template<int m>
struct SphereChain : SphereAssembly<m>{
	SphereChain(float R) {
		// R: distance between two neighbor spheres
		this->pos.setZero();
		float start = -(m - 1) * R / 2;
		for (int i = 0; i < m; i++) {
			this->pos(0, i) = start + i * R;
		}
	}
};

/*
	Lift: 3N (coordinate) space to 2Nm (coordinate) space
	Project: 2Nm (gradient) space to 3N (gradient) space
*/

template<int N, int m>
Eigen::MatrixXf flatten(Eigen::MatrixXf& mat) {
	/*
		transform the arrangement

			[ X(N, m) ]
			[ Y(N, m) ]

		to a column vector: 
			[ x(p1,1) x(p2,1) ... | x(p1,2) x(p2,2) ... | y(p1,1) y(p2,1) ... | ... ]
	*/
	Eigen::MatrixXf xmap = mat.template block<N, m>(0, 0);
	Eigen::MatrixXf ymap = mat.template block<N, m>(N, 0);
	static Eigen::VectorXf res(2 * m * N);
	memcpy(res.data(), xmap.data(), N * m * sizeof(float));
	memcpy(res.data() + N * m, ymap.data(), N * m * sizeof(float));
	return res;
}

/*
		2Nm vector:
		particle 1 -- p1

			[ x(p1,1) x(p2,1) ... | x(p1,2) x(p2,2) ... | y(p1,1) y(p2,1) ... | ... ]
			[ N                   | N               ... | N	                  | ... ] --length

		therefore, index % N is the id of particle.
*/
template<int N, int m>
struct SpaceTransformer {
	/*
		relative pos:
			[x(p1, 1) x(p2, 1) ...]
			[x(p1, 2) x(p2, 2) ...]
			[...                  ]
			[y(p1, 1) y(p2, 1) ...]
			[...                  ] .T(N, 2 * m)
	*/
	SphereAssembly<m>* sa;
	// Matf<2 * N, m> relative_pos;  // cause stack overflow
	Eigen::MatrixXf relative_pos;

	SpaceTransformer(SphereAssembly<m>* sa) {
		this->sa = sa;
		relative_pos = Eigen::MatrixXf(2 * N, m);
	}

	void init(Vecf<N>& angles) {
		// static Matf<2 * N, 2> rot_tensor;  // cause stack overflow
		static Eigen::MatrixXf rot_tensor(2 * N, 2);

		// Generate the rotation tensor (represented as a (2*N, 2) matrix)
		for (int i = 0; i < N; i++) {
			rot_tensor.template block<2, 2>(2 * i, 0) = Eigen::Rotation2Df(angles[i]).toRotationMatrix();
		}
		// do a matrix product to get all relative coordinates
		// Matf<2 * N, m> raw_relative_pos = rot_tensor * sa->pos;  // cause stack overflow
		Eigen::MatrixXf raw_relative_pos = rot_tensor * sa->pos;

		// swap lines to xxyy form and cache it
		for (int i = 0; i < N; i++) {
			relative_pos.row(i) = raw_relative_pos.row(2 * i);
			relative_pos.row(i + N) = raw_relative_pos.row(2 * i + 1);
		}
	}
	Eigen::MatrixXf toCross() {
		// Matf<N, 2 * m> cross;  // cause stack overflow
		static Eigen::MatrixXf cross(N, 2 * m);
		cross.template block<N, m>(0, 0) = -relative_pos.template block<N, m>(N, 0);
		cross.template block<N, m>(0, m) = relative_pos.template block<N, m>(0, 0);
		return cross;
	}

	Eigen::VectorXf lift(Vecf<3 * N>& q) {
		Vecf<2 * N> r = q.template head<2 * N>();
		Vecf<N> a = q.template tail<N>();
		// compute the relative position (cache)
		this->init(a);
		// do a repeat matrix summation
		// Matf<2 * N, m> absolute_pos = r.replicate(1, m) + relative_pos;   // cause stack overflow
		Eigen::MatrixXf absolute_pos = r.replicate(1, m) + relative_pos;

		// flatten the matrix (combine another two indices of the resultant tensor)
		return flatten<N, m>(absolute_pos);
	}

	Vecf<3 * N> project(Eigen::VectorXf& gs) {  // Vecf<2 * N * m>& gs
		/*
			do this kind of reshape: trnasform

				[ x(p1,1) x(p2,1) ... | x(p1,2) x(p2,2) ... | y(p1,1) y(p2,1) ... | ... ] (N * m * 2)

			to

				[ x(p1,1) x(p2,1) ... ]
				[ x(p1,2) x(p2,2) ... ]
				[ ...                 ]
				[ y(p1,1) y(p2,1) ... ]
				[ ...                 ].T (N, 2 * m)
		*/
		Eigen::Map<Matf<N, 2 * m>> gxy(gs.data());
		/*
			calculate torques:
			do a elementwise product and sum over [2m] columns
		*/
		Eigen::MatrixXf torque_to_sum = gxy.cwiseProduct(this->toCross());
		/*
			do this kind of reshape: trnasform

				[ x(p1,1) x(p2,1) ... ]
				[ x(p1,2) x(p2,2) ... ]
				[ ...                 ]
				[ y(p1,1) y(p2,1) ... ]
				[ ...                 ].T (N, 2 * m)

			to

				[ x(p1,1) x(p2,1) ... | y(p1,1) y(p2,1) ... ]
				[ x(p1,2) x(p2,2) ... | y(p1,2) y(p2,2) ... ]
				[ ...                 | ...                 ].T (2 * N, m)
		*/
		static Eigen::MatrixXf gradients(2 * N, m);
		gradients.template block<N, m>(0, 0) = gxy.template block<N, m>(0, 0);
		gradients.template block<N, m>(N, 0) = gxy.template block<N, m>(0, m);
		// concat
		Vecf<3 * N> res;
		// calculate forces: sum by row
		res.template block<2 * N, 1>(0, 0) = gradients.rowwise().sum();
		// res.template block<N, 1>(2 * N, 0) = inertia * torque_to_sum.rowwise().sum();
		res.template block<N, 1>(2 * N, 0) = torque_to_sum.rowwise().sum();
		return res;
	}
};