#pragma once

#include<nlohmann/json.hpp>
#include<string>
#include<vector>
#include<fstream>
#include "states.h"
using json = nlohmann::json;

// tool functions

std::string randomString(int length) {
	char* cstr = new char[length + 1];
	for (int i = 0; i < length; i++) {
		cstr[i] = 'a' + rand() % 26;
	}
	cstr[length] = '\0';
	std::string str(cstr);
	delete[] cstr;
	return str;
}

std::string getDateTime() {
	time_t now = time(0);
	tm* gmtm = gmtime(&now);
	long int res = 0;
	res += (gmtm->tm_mon + 1) * 1000000;
	res += gmtm->tm_mday * 10000;
	int hour = gmtm->tm_hour + 8;			// [+8]: GMT+8
	if (hour > 23) {
		hour -= 24;
		res += 10000;						// the date may be larger than the number of days of a month,
		// but we don't care about that.
	}
	res += hour * 100;
	res += gmtm->tm_min;
	std::string str = std::to_string(res);
	if (str.size() < 8) {
		return "0" + str;
	}
	else {
		return str;
	}
}

/*
	Metadata types
*/

template<typename BoundaryType> std::string BoundaryName();
template<> std::string BoundaryName<BoundaryC>() { return "CircleBoundary"; }
template<> std::string BoundaryName<BoundaryE>() { return "EllipticBoundary"; }

template<ScalarF sca> std::string PotentialName();
template<> std::string PotentialName<ScalarF::Power>() { return "Power"; }
template<> std::string PotentialName<ScalarF::Exp>() { return "Exp"; }

template<int N, typename bt>
class Metadata {
public:
	std::string name;
	std::string datetime;		// MM DD hh mm

	float step_size;
	float initial_boundary_radius;
	float boundary_compression_rate;

	std::vector<float> final_energy_curve;

	Metadata(){
		srand(time(0));
		this->datetime = getDateTime();
		this->name = randomString(4);
		this->step_size = CLASSIC_STEP_SIZE;
		this->initial_boundary_radius = INIT_BOUNDARY;
		this->boundary_compression_rate = COMPRESSION_RATE;
	}
	void output() {
		json js;
		// Name
		js["name"] = name;
		js["datetime"] = datetime;

		// Enums
		js["boundary shape"] = BoundaryName<bt>();
		js["potential type"] = PotentialName<SCALAR_POTENTIAL_TYPE>();

		// Macros
		js["particle number"] = N;
		js["assembly number"] = ASSEMBLY_NUM;
		js["sphere distance"] = SPHERE_DIST;
		js["particle aspect ratio"] = (float)(ASSEMBLY_NUM - 1) / 2;
		js["particle size a"] = (float)(ASSEMBLY_NUM - 1) / 2;
		js["particle size b"] = 1;
		js["step size"] = step_size;
		js["initial boundary radius"] = initial_boundary_radius;
		js["boundary compression rate"] = boundary_compression_rate;
		std::vector<float> temp(final_energy_curve.begin(), final_energy_curve.end());
		js["energy curve"] = temp;
		std::ofstream file(name + ".metadata.json");
		file << js << std::endl;
	}
};

template<int N>
void OutputConfiguration(json& js, Vecf<3 * N>& q) {
	static std::string dof_name[3] = { "x", "y","a" };
	std::vector<float> temp(N);
	for (int i = 0; i < 3; i++) {
		memcpy(&temp[0], q.data() + i * N, N * sizeof(float));
		json j_vec(temp);
		js[dof_name[i]] = j_vec;
	}
}

template<int energy_curve_capacity>
void OutputEnergyCurve(json& js, ivector<float, energy_curve_capacity>& energy_curve) {
	std::vector<float> temp(energy_curve.begin(), energy_curve.end());
	json j_vec(temp);
	js["energy curve"] = j_vec;
	energy_curve.clear();
}

struct InnerLoopData { int iterations; float energy; };

template<int energy_curve_capacity, int m, int N, typename BoundaryType>
void OutputData(
	int step, Metadata<N, BoundaryType>* meta,
	State<m, N, BoundaryType>& cf, 
	ivector<float, energy_curve_capacity>& energy_curve,
	InnerLoopData& loop_data) 
{
	json js;
	js["id"] = step;
	js["scalar radius"] = cf.boundary->scalar_radius;
	js["energy"] = loop_data.energy;
	js["iterations"] = loop_data.iterations;

	OutputConfiguration<N>(js, *(cf.q));
	OutputEnergyCurve(js, energy_curve);

	std::ofstream file(meta->name + ".json", std::ios::app);
	file << js << std::endl;
	file.close();
}

// deprecated

void OutputDenseDynamic(Eigen::MatrixXf& mat) {
	std::ofstream outfile("matrix.txt");
	outfile << mat.format(Eigen::IOFormat(Eigen::StreamPrecision, Eigen::DontAlignCols, ", ", "\n", "", "", "", ""));
	outfile.close();
}

void OutputVectorDynamic(Eigen::VectorXf& vec) {
	std::ofstream outfile("matrix.txt");
	outfile << vec.format(Eigen::IOFormat(Eigen::StreamPrecision, Eigen::DontAlignCols, ", ", "\n", "", "", "", ""));
	outfile.close();
}