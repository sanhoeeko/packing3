#pragma once

#include"io.h"
#include"basic_op.h"

struct Simulation{
	StateInfo<ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE> state_info;
	ivector<float, MAX_INIT_ITERATIONS> _energy_curve;
	IvectorSampler<float, MAX_INIT_ITERATIONS, ENERGY_RESOLUTION>* energy_curve;
	Metadata<PARTICLE_NUM, BSHAPE>* meta;
	float current_step_size;	// for mutable step size

	Simulation() {
		state_info = CreateRandomState<ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE>(BOUNDARY_A, BOUNDARY_B);

		meta = new Metadata<PARTICLE_NUM, BSHAPE>();
		meta->output();
		energy_curve = new IvectorSampler<float, MAX_INIT_ITERATIONS, ENERGY_RESOLUTION>(&_energy_curve);
		current_step_size = MAX_STEP_SIZE;

		std::cout << "Simulation ID: " << meta->name << std::endl;
		InnerLoopData init_data = relaxAfterInit();
		while (cancelPenetrate<PARTICLE_NUM>(*(state_info.state->q), particle_radius, 1.0f)) {
			init_data = relaxAfterInit();
		}
		output(0, init_data);
	}
	InnerLoopData relaxAfterInit() {
		InnerLoopData data = loop_classic(MAX_INIT_ITERATIONS);
		std::cout << "Initialization finished. iterations: " << data.iterations
			<< ",\t energy: " << data.energy << std::endl;
		return data;
	}
	void simulate() {
		for (int t = 0; t < NUM_COMPRESSIONS; t++) {
			state_info.state->boundary->step(this->meta->boundary_compression_rate);
			current_step_size = MAX_STEP_SIZE;
			double tc;
			RecordTime(tc,
				InnerLoopData data = loop_custom(MAX_ITERATIONS);
			)
#ifdef RECORD_TIME
			double speed = data.iterations / tc;
			std::cout << "current speed: " << speed << " it/s." << std::endl;
#endif
			std::cout << "compression: " << t <<
				",\t boundary radius: " << state_info.state->boundary->scalar_radius <<
				",\t iterations: " << data.iterations <<
				",\t energy: " << data.energy << std::endl;
			std::cout << "current step size: " << current_step_size << std::endl;
			if (t % OUTPUT_STRIDE == 0)output(t + 1, data);
		}
		this->meta->output();
	}
	void output(int current_turn_idx, InnerLoopData& data) {
		meta->final_energy_curve.push_back(_energy_curve.top());
		OutputData<MAX_INIT_ITERATIONS, ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE>(current_turn_idx, meta,
			*(state_info.state), _energy_curve, data);
	}
	InnerLoopData loop_classic(int turns) {
		int i = 0;
		float energy = 0;
		current_step_size = CLASSIC_STEP_SIZE;
		for (; i < turns; i++) {
			energy = Step(state_info, current_step_size);
			energy_curve->push_back(energy);
			if (energy < ENERGY_EPS)break;
		}
		return { i, energy };
	}
	InnerLoopData loop_custom(int turns) {
		const float Ec = 1;
		const float k = log((MAX_STEP_SIZE - MIN_STEP_SIZE) / (CLASSIC_STEP_SIZE - MIN_STEP_SIZE)) / Ec;
		const float A = MAX_STEP_SIZE - MIN_STEP_SIZE;
		static auto step_size_func = [=](float x)->float {return MIN_STEP_SIZE + A * exp(-k * x); };
		int i = 0;
		float energy = 0;
		current_step_size = meta->final_energy_curve.empty()? 
			MAX_STEP_SIZE: 
			step_size_func(meta->final_energy_curve[meta->final_energy_curve.size() - 1]);
		for (; i < turns; i++) {
			energy = Step(state_info, current_step_size);
			current_step_size = step_size_func(energy);
			energy_curve->push_back(energy);
			if (energy < ENERGY_EPS)break;
		}
		return { i, energy };
	}
};