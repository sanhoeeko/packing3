#pragma once

#include"defs.h"
#include"boundary.h"
#include<unordered_map>
#include<functional>

struct Triplet{
    float r, x, y;
};
struct TripletB {
    float h, x, y;
};

struct pair_hash {
    std::size_t operator () (const std::pair<int, int>& key) const {
        return ((std::size_t)key.first << 32) | key.second;
    }
};

template<typename t> struct MySparseVector;

template<typename t>
struct MySparseVectorBase {
    std::unordered_map<int, t> dict;    // int type does not need a hash function

    void clear() {
        dict.clear();
    }
    template<typename result_t>
    MySparseVector<result_t> apply(std::function<result_t(t&)> f) {
        MySparseVector<result_t> res; res.dict.reserve(this->dict.size());
        for (auto& kv : dict) {
            res.dict[kv.first] = f(kv.second);
        }
        return res;
    }
};

template<typename t> struct MySparseVector : MySparseVectorBase<t> {};

template<>
struct MySparseVector<TripletB> : MySparseVectorBase<TripletB> {
    void link(int i, float h, float x, float y) {
        dict[i] = { h, x, y };
    }
    Eigen::ArrayXf get_h_array() {
        Eigen::ArrayXf res(dict.size());
        float* ptr = res.data();
        for (auto& kv : dict) {
            *ptr++ = kv.second.h;
        }
        return res;
    }
};

template<>
struct MySparseVector<Eigen::Vector2f> : MySparseVectorBase<Eigen::Vector2f> {

    template<int N, int m>
    Vecf<2 * N * m> toVector() {
        Vecf<2 * N * m> res; res.setZero();
        for (auto& kv : dict) {
            int i = kv.first;
            res(i) = kv.second(0);
            res(i + N * m) = kv.second(1);
        }
        return res;
    }
};


template<typename t> struct MySparseMatrix;

template<typename t>
struct MySparseMatrixBase {
	std::unordered_map<std::pair<int, int>, t, pair_hash> dict;

    t& operator()(int i, int j) {
        return dict[{i, j}];
    }
    void clear() {
        dict.clear();
    }
    template<typename result_t>
    MySparseMatrix<result_t> apply(std::function<result_t(t&)> f) {
        // input: a function [fx, fy] = f(r, x, y) to calculate forces
        MySparseMatrix<result_t> res; res.dict.reserve(this->dict.size());
        for (auto& kv : dict) {
            res.dict[kv.first] = f(kv.second);
        }
        return res;
    }
    MySparseVector<t> rowwiseSumAsym() {
        MySparseVector<t> res; res.dict.reserve(this->dict.size());
        for (auto& kv : dict) {
            t& value = kv.second;
            auto iterator_and_success = res.dict.insert({kv.first.first, -value});
            if (!iterator_and_success.second) {                                     // If the key already exists
                iterator_and_success.first->second -= value;                        // Add to the existing value
            }
            iterator_and_success = res.dict.insert({ kv.first.second, value });
            if (!iterator_and_success.second) {
                iterator_and_success.first->second += value;
            }
        }
        return res;
    }
};

template<typename t> struct MySparseMatrix : MySparseMatrixBase<t>{};

template<>
struct MySparseMatrix<Triplet> : MySparseMatrixBase<Triplet> {
    // inherit
    void link(int i, int j, float r, float x, float y) {
        dict[{i, j}] = { r,x,y };
    }
    Eigen::ArrayXf get_r_array() {
        Eigen::ArrayXf res(dict.size());
        float* ptr = res.data();
        for (auto& kv : dict) {
            *ptr++ = kv.second.r;
        }
        return res;
    }
};

