#include "simulation.h"

int main() {
	double time_consumption;
	RecordTime(time_consumption,
		Simulation simu(false);
		// simu.getStateAt(END_BOUNDARY_B);
		simu.simulate(END_BOUNDARY_B);
	);
	std::cout << "Total time consumption: " << time_consumption / 60 << " min." << std::endl;
	return 0;
}