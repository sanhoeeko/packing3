#include"grid.h"

Grid::Grid(float cell_size, float boundary_a, float boundary_b) {
	/*
		Input:
		A: semi major axis
		B: semi minor axis
	*/
	a = cell_size;
	m = (int)ceil(boundary_a / a);
	n = (int)ceil(boundary_b / a);
	xshift = m + 1; 
	yshift = n + 1;
	lines = 2 * yshift; 
	cols = 2 * xshift;
	size = lines * cols;
	p = new ivector<int, MAX_CONTACT_NUMBER>[size];
	collision_detect_region = new int[4]{1 - cols, 1, 1 + cols, cols };
	is_clear = true;
}
int Grid::xlocate(float x) {
	return (int)floor(x / a) + xshift;
}
int Grid::ylocate(float y) {
	return (int)floor(y / a) + yshift;
}
void Grid::add(int i, int j, int particle_id) {
	(this->p + i * cols + j)->push_back(particle_id);
}
ivector<int, MAX_CONTACT_NUMBER>* Grid::loc(int i, int j){
	// Do not use this, because it is slow.
	return this->p + i * cols + j;
}
void Grid::clear() {
	auto ptr = p;
	auto pend = p + size;
	while (ptr < pend){
		(ptr++)->clear();
	}
	is_clear = true;
}