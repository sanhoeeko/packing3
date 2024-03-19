#pragma once

#include"defs.h"
#include <vector>
#include <cmath>
#include <functional>

const float precision = 1e-2f;
const int tangents_num = 3;

struct BESolver {
    float a, b;
    float a2, b2, a4, b4, a6, b6;
    float x02, y02;
    float sub_a2, sub_b2;

    BESolver() { ; }
    BESolver(float a, float b) : a(a), b(b) {
        a2 = a * a; b2 = b * b;
        a4 = a2 * a2; b4 = b2 * b2;
        a6 = a2 * a4; b6 = b2 * b4;
        sub_a2 = (a - 2) * (a - 2); sub_b2 = (b - 2) * (b - 2);
    }

    bool gate(float x0, float y0) {
        /*
            If gate -> false, the particle is not possible be to in contact with the wall.
        */
        return x0 * x0 / sub_a2 + y0 * y0 / sub_b2 > 1;
    }

    std::pair<float,float> make_first_estimate(float x0, float y0) {
        float k = (a * b) / std::sqrt(b2 * x02 + a2 * y02);
        return std::make_pair(k * x0, k * y0);
    }

    std::pair<float,float> innerIteration(float x1, float y1, float x0, float y0) {
        float x1sq = x1 * x1, y1sq = y1 * y1;
        float sq_delta = std::sqrt(
            b6 * x1sq - b4 * x1sq * y02 +
            2 * a2 * b2 * x0 * x1 * y0 * y1 +
            a4 * (a2 - x02) * y1sq);
        float k = 1 / (b6 * x1sq + a6 * y1sq);
        float x20 = k * (-a4 * b2 * x1 * y0 * y1 + a6 * x0 * y1sq);
        float y20 = k * (b6 * x1sq * y0 - a2 * b4 * x0 * y1 * x1);
        float abs_det = std::abs(k * a * b * sq_delta);
        return std::make_pair(x20 + b2 * x1 * abs_det, y20 + a2 * y1 * abs_det);
    }

    std::pair<float,float> inner(float x0, float y0) {
        if (x0 == 0 && y0 == 0) {
            return std::make_pair(0, b);
        }
        float x1, y1, x2, y2;
        std::tie(x1, y1) = make_first_estimate(x0, y0);
        for (int i = 0; i < tangents_num; ++i) {
            std::tie(x2, y2) = innerIteration(x1, y1, x0, y0);
            if (std::max(std::abs(x2 - x1), std::abs(y2 - y1)) < precision) {
                return std::make_pair(x2, y2);
            }
        }
        return std::make_pair(x2, y2);
    }
    std::pair<float, float> outerIteration(float x1, float y1) {
        float x1sq = x1 * x1, y1sq = y1 * y1;
        float sq_delta = std::sqrt(
            b6 * x1sq - b4 * x1sq * y1sq +
            2 * a2 * b2 * x1sq * y1sq +
            a4 * (a2 - x1sq) * y1sq);
        float k = 1 / (b6 * x1sq + a6 * y1sq);
        float kx = k * x1;
        float ky = k * y1;
        float x20 = kx * (a6 * y1sq - a4 * b2 * y1sq);
        float y20 = ky * (b6 * x1sq - a2 * b4 * x1sq);
        float abs_det = std::abs(sq_delta);
        return std::make_pair(x20 + (a * b * b2) * kx * abs_det, y20 + (b * a * a2) * ky * abs_det);
    }
    std::pair<float, float> outer(float x0, float y0) {
        float x1, y1, x2, y2;
        std::tie(x1, y1) = make_first_estimate(x0, y0);
        for (int i = 0; i < tangents_num; ++i) {
            std::tie(x2, y2) = outerIteration(x1, y1);
            if (std::max(std::abs(x2 - x1), std::abs(y2 - y1)) < precision) {
                return std::make_pair(x2, y2);
            }
        }
        return std::make_pair(x1, y1);
    }

    float h(float x0, float y0) {
        x0 = std::abs(x0); y0 = std::abs(y0);
        x02 = x0 * x0; y02 = y0 * y0;           // update x02, y02 at once, before the first estimation.
        float x1, y1;
        if (x02 / a2 + y02 / b2 < 1) {
            std::tie(x1, y1) = inner(x0, y0);
            float dx = x0 - x1, dy = y0 - y1;
            return std::sqrt(dx * dx + dy * dy);
        }
        else {
            std::tie(x1, y1) = outer(x0, y0);
            float dx = x0 - x1, dy = y0 - y1;
            return -std::sqrt(dx * dx + dy * dy);
        }
    }
};