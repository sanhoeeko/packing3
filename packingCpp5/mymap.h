#pragma once

#include<functional>
#include<tuple>

/*
	an analog of unordered_map<std::pair<int, int>, t>
*/
template<int n, int threads, typename t>
struct IntPairMap{
	/*
		elements in [secs]: (int j, int shift)
	*/
	std::pair<int, int>* secs;
	int* sizes;
	t* data;
	int cnt;
	
	IntPairMap() {
		int capacity = n * threads;
		secs = (std::pair<int, int>*)malloc(capacity * sizeof(std::pair<int, int>));
		sizes = (int*)malloc(n * sizeof(int)); memset(sizes, 0, n * sizeof(int));
		data = (t*)malloc(capacity * sizeof(t));	// use malloc: do not call the construct function of t. dangerous operation here.
		cnt = 0;
	}
	IntPairMap(const IntPairMap<n, threads, t>& src) {
		int capacity = n * threads;
		secs = (std::pair<int, int>*)malloc(capacity * sizeof(std::pair<int, int>));
		sizes = (int*)malloc(n * sizeof(int));
		data = (t*)malloc(capacity * sizeof(t));
		memcpy(secs, src.secs, capacity * sizeof(std::pair<int, int>));
		memcpy(sizes, src.sizes, n * sizeof(int));
		memcpy(data, src.data, capacity * sizeof(t));
		cnt = src.cnt;
	}
	IntPairMap& operator=(const IntPairMap& src) {
		int capacity = n * threads;
		memcpy(secs, src.secs, capacity * sizeof(std::pair<int, int>));
		memcpy(sizes, src.sizes, n * sizeof(int));
		memcpy(data, src.data, capacity * sizeof(t));
		cnt = src.cnt;
		return *this;
	}
	~IntPairMap() {
		free(secs);
		free(sizes);
		free(data);
	}
	int size() {
		return cnt;
	}
	void clear() {
		cnt = 0;
		memset(sizes, 0, n * sizeof(int));
	}
	void insert(int i, int j, const t& obj) {
		// Note: make sure that key (i, j) does not exist
		data[cnt] = obj;
		secs[i * threads + sizes[i]] = { j, cnt };
		sizes[i]++; cnt++;
	}
	t& operator()(int i, int j) {
		// Note: make sure that key (i, j) exists
		// Do not use it if possible, because random access is O(threads)
		int start = i * threads;
		for (int k = 0; k < threads; k++) {
			if (secs[start + k].first == j) {
				return data[secs[start + k].second];
			}
		}
		throw "Key not exists";
	}
	template<typename s>
	IntPairMap<n, threads, s> apply(std::function<s(t&)> f) const & {
		int capacity = n * threads;
		IntPairMap<n, threads, s> res;
		memcpy(res.secs, this->secs, capacity * sizeof(std::pair<int, int>));
		memcpy(res.sizes, this->sizes, n * sizeof(int));
		for (int i = 0; i < cnt; i++) {
			res.data[i] = f(this->data[i]);
		}
		res.cnt = this->cnt;
		return res;
	}
};

template<int n, int threads, typename t>
struct IntPairMapIterator {
	IntPairMap<n, threads, t>* ptr;
	int i;
	int kth;
	t* value_ptr;

	IntPairMapIterator(IntPairMap<n, threads, t>& map) {
		ptr = &map;
		i = 0;
		while (ptr->sizes[i] == 0)i++;
		kth = 0;
		value_ptr = ptr->data;
	}
	void operator++() {
		kth++;
		while (i < n && kth >= ptr->sizes[i]) {
			kth = 0; i++;
		}
	}
	bool goes() {
		return i < n;
	}
	std::tuple<int, int, t*> val() {
		int start = i * threads;
		int j = ptr->secs[start + kth].first;
		int shift = ptr->secs[start + kth].second;
		return std::make_tuple(i, j, value_ptr + shift);
	}
};

/*
	an analog of unordered_map<int, t>
*/
template<int n, typename t>
struct IntMap{
	bool* occupied;
	t* data;

	IntMap() {
		occupied = new bool[n]; memset(occupied, false, n * sizeof(bool));
		data = new t[n];
	}
	IntMap(const IntMap& src) {
		occupied = new bool[n];
		data = new t[n];
		memcpy(occupied, src.occupied, n * sizeof(bool));
		memcpy(data, src.data, n * sizeof(t));
	}
	IntMap& operator=(const IntMap& src) {
		memcpy(occupied, src.occupied, n * sizeof(bool));
		memcpy(data, src.data, n * sizeof(t));
		return *this;
	}
	~IntMap() {
		delete[] occupied; delete[] data;
	}

	void clear() {
		memset(occupied, false, n * sizeof(bool));
	}
	int size() {
		bool* ptr = occupied;
		bool* pend = occupied + n;
		int s = 0;
		for (; ptr < pend; ptr++) {
			s += (int)(*ptr);
		}
		return s;
	}
	void insert(int i, const t& val) {
		// Note: make sure that key (i) does not exist
		occupied[i] = true;
		data[i] = val;
	}
	void add(int i, const t& val) {
		occupied[i] = true;
		data[i] += val;
	}
	void add_or_insert(int i, const t& val) {
		// slow?
		if (occupied[i]) {
			data[i] += val;
		}
		else {
			insert(i, val);
		}
	}
	template<typename s>
	IntMap<n, s> apply(std::function<s(t&)> f) const& {
		IntMap<n, s> res;
		memcpy(res.occupied, this->occupied, n * sizeof(bool));
		for (int i = 0; i < n; i++) {
			if (occupied[i]) {
				res.data[i] = f(this->data[i]);
			}
		}
		return res;
	}
};

template<int n, typename t>
struct IntMapIterator {
	IntMap<n, t>* ptr;
	int i;

	IntMapIterator(IntMap<n, t>& map) {
		ptr = &map;
		i = 0;
		while (i < n && !ptr->occupied[i]) {
			i++;
		}
	}
	void operator++() {
		i++;
		while (i < n && !ptr->occupied[i]) {
			i++;
		}
	}
	bool goes() {
		return i < n;
	}
	t* val() {
		return ptr->data + i;
	}
};