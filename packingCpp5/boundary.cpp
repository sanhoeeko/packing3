#include "boundary.h"
#include "solver.h"

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
}

float BoundaryE::h(float x, float y)
{
    static float c2 = this->a * this->a - this->b * this->b;
    float estimate_alpha = atan(abs(y / (aspect_ratio * x)));   // |estimate_t - t| is a 
    float estimate_t = tan(estimate_alpha / 2);
    float by = this->b * y; 
    float a3 = 2 * (c2 + this->a * x);
    float a1 = 2 * (-c2 + this->a * x);
    float t = solveQuarticNewton(-by, a3, 0, a1, by, estimate_t);
    float dx = x - this->a * cos(t);
    float dy = y - this->b * sin(t);
    return sqrt(dx * dx + dy * dy);
}
