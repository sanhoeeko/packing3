#pragma once

#include"defs.h"
#include"boundary.h"
#include"mymap.h"
#include"ivector.h"
#include<functional>

struct Triplet{
    float r, x, y;
};
struct TripletB {
    float h, x, y;
};

template<int Nm, typename t> struct MySparseVector;

template<int Nm, typename t>
struct MySparseVectorBase {
    IntMap<Nm, t> dict;

    void clear() {
        dict.clear();
    }
    template<typename result_t>
    MySparseVector<Nm, result_t> apply(std::function<result_t(t&)> f) {
        MySparseVector<Nm, result_t> res;
        res.dict = dict.apply(f);
        return res;
    }
};

template<int Nm, typename t> struct MySparseVector : MySparseVectorBase<Nm, t> {};

template<int Nm>
struct MySparseVector<Nm, TripletB> : MySparseVectorBase<Nm, TripletB> {
    void link(int i, float h, float x, float y) {
        this->dict.insert(i, { h, x, y });
    }
    Eigen::ArrayXf get_h_array() {
        Eigen::ArrayXf res(this->dict.size());
        float* ptr = res.data();
        for (IntMapIterator<Nm, TripletB> it(this->dict); it.goes(); ++it) {
            *ptr++ = it.val()->h;
        }
        return res;
    }
};

template<int Nm>
struct MySparseVector<Nm, Eigen::Vector2f> : MySparseVectorBase<Nm, Eigen::Vector2f> {

    MySparseVector<Nm, Eigen::Vector2f>() {
        memset(this->dict.data, 0, Nm * sizeof(Eigen::Vector2f));
    }
    Vecf<2 * Nm> toVector() {
        Vecf<2 * Nm> res; res.setZero();
        for (IntMapIterator<Nm, Eigen::Vector2f> it(this->dict); it.goes(); ++it) {
            res(it.i) = (*it.val())(0);
            res(it.i + Nm) = (*it.val())(1);
        }
        return res;
    }
};


template<int Nm, typename t> struct MySparseMatrix;

template<int Nm, typename t>
struct MySparseMatrixBase {
    IntPairMap<Nm, MAX_CONTACT_NUMBER, t> dict;

    void clear() {
        dict.clear();
    }
    template<typename result_t>
    MySparseMatrix<Nm, result_t> apply(std::function<result_t(t&)> f) const & {
        // input: a function [fx, fy] = f(r, x, y) to calculate forces
        MySparseMatrix<Nm, result_t> res;
        res.dict = this->dict.apply(f);     // note this "=". [operator=] of [IntPairMap] must be overloaded!!
        return res;
    }
    MySparseVector<Nm, t> rowwiseSumAsym() {
        MySparseVector<Nm, t> res;
        for (IntPairMapIterator<Nm, MAX_CONTACT_NUMBER, t> it(dict); it.goes(); ++it) {
            int i, j; t* pvalue;
            std::tie(i, j, pvalue) = it.val();
            res.dict.add(i, -*pvalue);      // only for MySparseVector<Nm, t> t=Eigen::Vector2f, which has zero initialization
            res.dict.add(j, *pvalue);
        }
        return res;
    }
};

template<int Nm, typename t> struct MySparseMatrix : MySparseMatrixBase<Nm, t>{};

template<int Nm>
struct MySparseMatrix<Nm, Triplet> : MySparseMatrixBase<Nm, Triplet> {
    // inherit
    void link(int i, int j, float r, float x, float y) {
        this->dict.insert(i, j, { r,x,y });
    }
    Eigen::ArrayXf get_r_array() {
        Eigen::ArrayXf res(this->dict.size());
        Triplet* ptr = this->dict.data;
        Triplet* pend = ptr + this->dict.size();
        float* dst = res.data();
        for (; ptr < pend; ptr++) {
            *dst++ = ptr->r;
        }
        return res;
    }
};

