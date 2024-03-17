#pragma once

#include"defs.h"
#include <vector>
#include <cmath>
#include <functional>

// Helper function to find real roots using Newton's method
float findRealRootsNewton(
    std::function<float(float)> func, std::function<float(float)> deriv, float start) {

    float x0 = start, x1, y, dy;
    int iterations = 0;
    while (iterations < 100) {
        y = func(x0);
        dy = deriv(x0);

        // Avoid division by zero
        if (dy == 0) break;

        // Newton's method formula
        x1 = x0 - y / dy;

        // Check for convergence
        if (std::abs(x1 - x0) < 1e-5) {
            return x1;
        }
        x0 = x1;
        iterations++;
    }
    throw "Root Not Found Error";
}

// Function to solve quartic equation using Newton's method
float solveQuarticNewton(float a, float b, float c, float d, float e, float p0) {
    // Define the quartic function
    auto quarticFunc = [a, b, c, d, e](float x) -> float {
        return a * powf(x, 4) + b * powf(x, 3) + c * powf(x, 2) + d * x + e;
    };

    // Define the derivative of the quartic function
    auto quarticDeriv = [a, b, c, d](float x) -> float {
        return 4 * a * powf(x, 3) + 3 * b * powf(x, 2) + 2 * c * x + d;
    };

    // Find real roots in the interval [-100, 100] with a step of 0.1
    // These values can be adjusted based on the expected range and precision of the roots
    return findRealRootsNewton(quarticFunc, quarticDeriv, p0);
}
