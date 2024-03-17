#pragma once

#include<iostream>

template<typename ty, int limit>
class ivector {
public:
	ty* arr;
	int cnt;

	ivector() {
		arr = new ty[limit];
		cnt = 0;
	}
	~ivector() {
		delete[] arr;
	}
	void push_back(const ty& obj) {
		arr[cnt++] = obj;
		if (cnt > limit) {					// This judge almost costs nothing (<0.01%)
			std::cout << "ivector: Too short." << std::endl;
			throw "ivector: Too short.";	// If this occurs, see the macro [IVECTOR_LENGTH] in [defs.h]
		}
	}
	void push_back(ty&& obj) {
		arr[cnt++] = obj;
		if (cnt > limit) {					// This judge almost costs nothing (<0.01%)
			std::cout << "ivector: Too short." << std::endl;
			throw "ivector: Too short.";	// If this occurs, see the macro [IVECTOR_LENGTH] in [defs.h]
		}
	}
	void push_back_and_copy(ty obj) {
		/*
			In this method, the parameter is not a reference type,
			which means the parameter is copied. This is much slower but safer.
		*/
		arr[cnt++] = obj;
		if (cnt > limit) {
			std::cout << "ivector: Too short." << std::endl;
			throw "ivector: Too short.";	
		}
	}
	ty& operator[](int index) {
		return arr[index];
	}
	int& size() {
		return cnt;
	}
	void clear() {
		cnt = 0;
	}
	ty* begin() {
		return arr;
	}
	ty* end() {
		return arr + cnt;
	}
	ty top() {
		return arr[cnt - 1];
	}
};

template<typename ty, int limit, int resolution>
class IvectorSampler {
public:
	ivector<ty, limit>* iv;
	int cnt;
	IvectorSampler(ivector<ty, limit>* iv) {
		this->iv = iv;
		cnt = 0;
	}
	void push_back(const ty& obj) {
		cnt++;
		if (cnt == resolution) {
			cnt = 0;
			iv->push_back(obj);
		}
	}
	void push_back(ty&& obj) {
		cnt++;
		if (cnt == resolution) {
			cnt = 0;
			iv->push_back(obj);
		}
	}
};

template<typename ty, int limit>
void CopyIVector(ivector<ty, limit>& dst, ivector<ty, limit>& src) {
	dst.cnt = src.cnt;
	memcpy(dst.arr, src.arr, src.cnt * sizeof(ty));
}