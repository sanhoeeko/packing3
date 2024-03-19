#include "boundary.h"

void Boundary::define_scalar_radius(float r)
{
    this->scalar_radius = r;
    this->initial_scalar_radius = this->scalar_radius;
}

// Circle Boundary

BoundaryC::BoundaryC(float initial_radius, float _)
{
    this->radius = initial_radius;
    define_scalar_radius(initial_radius);
}

Grid* BoundaryC::getGrid()
{
    return new Grid(2, radius + particle_radius, radius + particle_radius);
}

void BoundaryC::step(float compression_rate)
{
    this->scalar_radius -= compression_rate;
    this->radius = this->scalar_radius;
}

float BoundaryC::h(float x, float y)
{
    return this->radius - sqrt(x * x + y * y);
}

// Ellipse Boundary

BoundaryE::BoundaryE(float a, float b)
{
    this->a = a; this->b = b;
    define_scalar_radius(b);
    this->aspect_ratio = a / b;
    this->sol = BESolver(a, b);
}

Grid* BoundaryE::getGrid()
{
    return new Grid(2, a + particle_radius, b + particle_radius);
}

void BoundaryE::step(float compression_rate)
{
    this->scalar_radius -= compression_rate;
    this->b -= compression_rate;
    this->a -= aspect_ratio * compression_rate;
    sol = BESolver(a, b);   // Do not forget to update the solver since there is one!
}

float BoundaryE::h(float x, float y)
{
    if (sol.gate(x, y)) {
        return sol.h(x, y);
    }
    else {
        return 2.0f;
    }
}
