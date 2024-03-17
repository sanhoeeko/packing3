#pragma once

#include"defs.h"
#include<math.h>
#include<iostream>

/*
	All inputs should be in range [0, 2). If not, it will return a default value: 0.
*/
template<int bin_digit>
class FastScalar { public:
	float* arr;
	float scale;
	FastScalar() { ; }
	FastScalar(float (*scalar_func)(float)) {
		long long len = (long long)1 << bin_digit;
		arr = new float[len];
		float inv_scale = 2.0f / len;
		scale = 1 / inv_scale;
		for (int i = 0; i < len; i++) {
			arr[i] = scalar_func(i * inv_scale);
		}
		std::cout << "Successfully initialize a fast scalar function."<< std::endl;
	}
	float operator()(const float x) {
		if (x < 0 || x >= 2) return 0;
		return arr[(int)(x * scale)];
	}
};

template<int bin_digit>
class UnsignedTrigonometric{ public:
	float* arr;
	float scale;
	UnsignedTrigonometric() {
		// data: sin(x) in [0, pi / 2]
		long long len = (long long)1 << bin_digit;
		arr = new float[len];
		float inv_scale = PI / 2.0f / len;
		scale = 1 / inv_scale;
		for (int i = 0; i < len; i++) {
			arr[i] = std::sin(i * inv_scale);	// use std::sin to avoid repetition of name
		}
		std::cout << "Successfully initialize a fast unsigned trigonometric function." << std::endl;
	}
	float sin(float x) {
		while (x >= PI) x -= PI;
		while (x < 0) x += PI;
		if (x >= PI / 2) x = PI - x;
		return arr[(int)(x * scale)];
	}
	float cos(float x) {
		return this->sin(x + PI / 2);
	}
};

/*
	Interfaces:
	Without loss of generality, we use [rij] as the input variable of potential pp, and [L - ri] for potential pw.
*/

template<ScalarF sca> class ScalarPotential {};

template<> class ScalarPotential<ScalarF::Power>{
	FastScalar<SCALAR_RESOLUTION> fpp;
	FastScalar<SCALAR_RESOLUTION> fpw;
	FastScalar<SCALAR_RESOLUTION> dfpp;
	FastScalar<SCALAR_RESOLUTION> dfpw;
public:
	ScalarPotential() {
		fpp = FastScalar<SCALAR_RESOLUTION>([](float r)->float {return r > 0 && r < 2 ? powf(2 - r, 2.5f) : 0; });
		fpw = FastScalar<SCALAR_RESOLUTION>([](float h)->float {return h > 0 && h < 1 ? SQRT8 * powf(1 - h, 2.5f) : 0; });
		dfpp = FastScalar<SCALAR_RESOLUTION>([](float r)->float {return r > 0 && r < 2 ? powf(2 - r, 1.5f) / r : 0; });
		dfpw = FastScalar<SCALAR_RESOLUTION>([](float h)->float {return h > 0 && h < 1 ? SQRT8 * powf(1 - h, 1.5f) : 0; });
	}
	float pp(float r) { return fpp(r); }
	float pw(float h) { return fpw(h); }
	float dpp_r(float r) { return dfpp(r); }
	float dpw(float h) { return dfpw(h); }	// pitfall: divided by r manually
};

template<> class ScalarPotential<ScalarF::Exp> {
	FastScalar<SCALAR_RESOLUTION> fpp;
	FastScalar<SCALAR_RESOLUTION> fpw;
	FastScalar<SCALAR_RESOLUTION> dfpp;
	FastScalar<SCALAR_RESOLUTION> dfpw;
public:
	ScalarPotential() {
		fpp = FastScalar<SCALAR_RESOLUTION>([](float r)->float {return r > 0 && r < 2 ? expf(-r / 2.0f) - EXP_N1 : 0; });
		fpw = FastScalar<SCALAR_RESOLUTION>([](float h)->float {return h > 0 && h < 1 ? expf(-h / 1.0f) - EXP_N1 : 0; });
		dfpp = FastScalar<SCALAR_RESOLUTION>([](float r)->float {return r > 0 && r < 2 ? expf(-r / 2.0f) / (2.0f * r) : 0; });
		dfpw = FastScalar<SCALAR_RESOLUTION>([](float h)->float {return h > 0 && h < 1 ? expf(-h / 1.0f) : 0; });
	}
	float pp(float r) { return fpp(r); }
	float pw(float h) { return fpw(h); }
	float dpp_r(float r) { return dfpp(r); }
	float dpw(float h) { return dfpw(h); } // pitfall: divided by r manually
};

// Instant

ScalarPotential<SCALAR_POTENTIAL_TYPE> V;