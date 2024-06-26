#include "boundary.h"

void Boundary::define_scalar_radius(float r)
{
    this->scalar_radius = r;
    this->initial_scalar_radius = this->scalar_radius;
}

void Boundary::step(float compression_rate)
{
    setScalarRadius(this->scalar_radius - compression_rate);
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

void BoundaryC::setScalarRadius(float scalar_radius)
{
    this->scalar_radius = scalar_radius;
    this->radius = scalar_radius;
}

std::tuple<float, float, float> BoundaryC::h(float x, float y)
{
    // return format: h, x, y
    float r = sqrt(x * x + y * y);
    return { this->radius - r, -x / r, -y / r };
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

void BoundaryE::setScalarRadius(float scalar_radius)
{
    this->scalar_radius = scalar_radius;
    this->b = scalar_radius;
    this->a = aspect_ratio * scalar_radius;
    sol = BESolver(a, b);   // Do not forget to update the solver since there is one!
}

/*
    Deprecated. For (x,y) can be outside the ellipse
*/
/*
std::tuple<float, float, float> BoundaryE::h(float x, float y)
{
    // return format: h, x, y
    static float Tx, Ty;
    if (sol.gate(x, y)) {
        bool is_in_ellipse = sol.h(x, y, Tx, Ty);
        float dx = std::abs(x - Tx), dy = std::abs(y - Ty);
        float abs_h = std::sqrt(dx * dx + dy * dy);
        if (abs_h < 1e-4) {
            float nx, ny; sol.normalVector(x, y, nx, ny);
            return { 0, nx, ny };
        }
        else {
            if (is_in_ellipse) {
                return{ abs_h, (x > 0 ? -dx / abs_h : dx / abs_h), (y > 0 ? -dy / abs_h : dy / abs_h) };
            }
            else {
                return{ -abs_h, (x > 0 ? -dx / abs_h : dx / abs_h), (y > 0 ? -dy / abs_h : dy / abs_h) };
            }
        }
    }
    else {
        return { 2.0f, 0, 0 };
    }
}
*/

std::tuple<float, float, float> BoundaryE::h(float x, float y)
{
    // return format: h, x, y
    static float dx, dy;
    if (sol.gate(x, y)) {
        sol.h_easy(x, y, dx, dy);
        float abs_h = std::sqrt(dx * dx + dy * dy);
        return{ abs_h, (x > 0 ? -dx / abs_h : dx / abs_h), (y > 0 ? -dy / abs_h : dy / abs_h) };
    }
    else {
        return { 2.0f, 0, 0 };
    }
}