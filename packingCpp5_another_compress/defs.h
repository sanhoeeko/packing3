#pragma once

#include"settings.h"

// disable Eigen's static assert
#define EIGEN_NO_DEBUG

/*
	// call Eigen's MKL acceleration (require: MKL library installed)
	// this must be before any #include
	#define EIGEN_USE_MKL_ALL
	#define EIGEN_VECTORIZE_SSE4_2
*/

#ifdef _WIN32
#include<windows.h>
	#undef max
#include<Eigen/Dense>
#include<Eigen/Sparse>
#pragma warning(disable : 4996)
#else
#include"eigen3/Eigen/Dense"
#include"eigen3/Eigen/Sparse"
#include<unistd.h>
#endif

template<int rows>
using Vecf = Eigen::Matrix<float, rows, 1>;

template<int rows>
using Vecft = Eigen::Matrix<float, 1, rows>;

template<int rows, int cols>
using Matf = Eigen::Matrix<float, rows, cols>;

#define PI 3.14159265359f
#define SQRT8 2.8284271247f
#define SQRT3_3 0.5773502692f
#define EXP_N1 0.3678794412f
#define NANF 114514.0f

#ifdef RECORD_TIME
	#define RecordTime(__t, __code__) clock_t _t_start, _t_end; _t_start = clock(); \
		__code__; _t_end = clock(); __t = (double)(_t_end - _t_start)/CLOCKS_PER_SEC;
#else
	#define RecordTime(__t, __code__) __code__;
#endif

#include<iostream>
#include<cfloat> 
