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
		state_info = CreateRandomState<ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE>(INIT_BOUNDARY, INIT_BOUNDARY);

		meta = new Metadata<PARTICLE_NUM, BSHAPE>();
		meta->output();
		energy_curve = new IvectorSampler<float, MAX_INIT_ITERATIONS, ENERGY_RESOLUTION>(&_energy_curve);
		current_step_size = meta->step_size;

		InnerLoopData data = loop_classic(MAX_INIT_ITERATIONS);
		std::cout << "Simulation ID: " << meta->name << std::endl;
		std::cout << "Initialization finished. iterations: " << data.iterations
			<< ",\t energy: " << data.energy << std::endl;
		output(0, data);
	}
	void simulate() {
		for (int t = 0; t < NUM_COMPRESSIONS; t++) {
			state_info.state->boundary->step(this->meta->boundary_compression_rate);
			current_step_size = meta->step_size;
			double tc;
			RecordTime(tc,
				InnerLoopData data = loop_classic(MAX_ITERATIONS);
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
		OutputData<MAX_INIT_ITERATIONS, ASSEMBLY_NUM, PARTICLE_NUM, BoundaryC>(current_turn_idx, meta,
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
			float gm = GradientMaxAbs<PARTICLE_NUM>(state_info.gradient);
			// if (gm < CEASE_FORCE)break;
		}
		return { i, energy };
	}
};