#pragma once

#include"io.h"
#include"basic_op.h"

const int descent_curve_capacity = std::max(MAX_INIT_ITERATIONS, MAX_ITERATIONS);

struct Simulation{
	StateInfo<ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE> state_info;
	ivector<float, descent_curve_capacity> _energy_curve;
	IvectorSampler<float, descent_curve_capacity, ENERGY_RESOLUTION>* energy_curve;
	Metadata<PARTICLE_NUM, BSHAPE>* meta;
	float current_step_size;	// for mutable step size

	Simulation(bool output_init_data) {
		state_info = CreateRandomState<ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE>(BOUNDARY_A, BOUNDARY_B);

		meta = new Metadata<PARTICLE_NUM, BSHAPE>();
		meta->output();
		energy_curve = new IvectorSampler<float, descent_curve_capacity, ENERGY_RESOLUTION>(&_energy_curve);
		current_step_size = CLASSIC_STEP_SIZE;

		std::cout << "Simulation ID: " << meta->name << std::endl;
		InnerLoopData init_data = relaxAfterInit();
		while (cancelPenetrate<PARTICLE_NUM>(*(state_info.state->q), particle_radius, 1.0f)) {
			init_data = relaxAfterInit();
		}
		if (output_init_data) {
			output(0, init_data);
		}
	}
	InnerLoopData relaxAfterInit() {
		InnerLoopData data = loop_classic(MAX_INIT_ITERATIONS);
		std::cout << "Initialization finished. iterations: " << data.iterations
			<< ",\t energy: " << data.energy << std::endl;
		return data;
	}
	void getStateAt(float scalar_radius) {
		/*
			Quickly compress to the radius required, 
			and then relax for a long time to decrease residual force in order to find an equilibrium state.
		*/
		float init_radius = state_info.state->boundary->scalar_radius;
		int steps = (init_radius - scalar_radius) / this->meta->boundary_compression_rate;
		// relax to the target scalar radius. no output.
		for (int t = 1; t < steps; t++) {
			// "set" the boundary radius, rather than substract.
			state_info.state->boundary->setScalarRadius(init_radius - t * this->meta->boundary_compression_rate);
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
			clearButNoOutput();
		}
		// full relax at the target scalar radius
		InnerLoopData data = loop_custom(FINE_ITERATIONS);
		std::cout << "final:\t iterations: " << data.iterations <<
			",\t energy: " << data.energy << std::endl;
		OutputData<descent_curve_capacity, ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE>(0, meta, data,
			*(state_info.state), _energy_curve);
	}
	void simulate(int num_compressions) {
		/*
			A full procedure simulation
		*/
		for (int t = 0; t < num_compressions; t++) {
			state_info.state->boundary->step(this->meta->boundary_compression_rate);
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
		OutputData<descent_curve_capacity, ASSEMBLY_NUM, PARTICLE_NUM, BSHAPE>(current_turn_idx, meta, data,
			*(state_info.state), _energy_curve);
	}
	void clearButNoOutput() {
		_energy_curve.clear();
	}
	InnerLoopData loop_classic(int turns) {
		int i = 0;
		float energy = 0;
		current_step_size = CLASSIC_STEP_SIZE;
		for (; i < turns; i++) {
			energy = Step(state_info, current_step_size);
			energy_curve->push_back(energy);
			if (energy < ENERGY_EPS) {
				break;
			}
		}
		return { i, energy };
	}
	InnerLoopData loop_custom(int turns) {
		current_step_size = FINE_STEP_SIZE;
		float best_energy = FLT_MAX;
		int early_stop_counter = 0;
		int i = 0;
		float energy = 0;
		for (; i < turns; i++) {
			energy = Step(state_info, current_step_size);
			energy_curve->push_back(energy);
			if (energy < ENERGY_EPS) {
				break;
			}
			if (i % ENERGY_RESOLUTION == 0) {
				if (energy / best_energy - 1 > -EARLY_STOP_COEF * FINE_STEP_SIZE) {
					early_stop_counter++;
					if (early_stop_counter == EARLY_STOP_PATIENCE) {
						break;
					}
				}
				else {
					early_stop_counter = 0;
				}
				if (energy < best_energy) {
					best_energy = energy;
				}
			}
		}
		return { i, energy };
	}
};