#pragma once

#include"defs.h"
#include"boundary.h"
#include"mymap.h"
#include"ivector.h"

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
    MySparseVector<Nm, result_t> apply(result_t(*f)(t&)) {
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
struct MySparseVector<Nm, v2> : MySparseVectorBase<Nm, v2> {

    MySparseVector<Nm, v2>() {
        memset(this->dict.data, 0, Nm * sizeof(v2));
    }
    Eigen::VectorXf toVector() {
        static Eigen::VectorXf res(2 * Nm); 
        res.setZero();
        for (IntMapIterator<Nm, v2> it(this->dict); it.goes(); ++it) {
            res(it.i) = it.val()->x;
            res(it.i + Nm) = it.val()->y;
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
    MySparseMatrix<Nm, result_t> apply(result_t(*f)(t&)) const & {
        // input: a function [fx, fy] = f(r, x, y) to calculate forces
        MySparseMatrix<Nm, result_t> res;
        res.dict = this->dict.apply(f);     // note this "=". [operator=] of [IntPairMap] must be overloaded!!
        return res;
    }
    template<typename result_t>
    void applyVectorized(void(*f)(t*, float*, int), MySparseMatrix<Nm, result_t>& dst){
        this->dict.template applyVectorized<result_t>(f, dst.dict);
    }
    MySparseVector<Nm, t> rowwiseSumAsym() {
        MySparseVector<Nm, t> res;
        for (IntPairMapIterator<Nm, MAX_CONTACT_NUMBER, t> it(dict); it.goes(); ++it) {
            int i, j; t* pvalue;
            std::tie(i, j, pvalue) = it.val();
            res.dict.sub(i, *pvalue);      // only for MySparseVector<Nm, t> t=v2, which has zero initialization
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

