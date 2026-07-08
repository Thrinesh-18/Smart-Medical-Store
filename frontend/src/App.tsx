import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

type Result = {
  medicine_id: number;
  medicine_name: string;
  generic_name: string;
  uses: string;
  symptoms: string[];
  price: number;
  stock_status: string;
  bm25_score: number;
  semantic_score: number;
  final_score: number;
  why_matched: {
    matching_keywords: string[];
    retrieval_source: string;
    alias_match: boolean;
    symptom_overlap: string[];
  };
};

type PopularQuery = {
  query: string;
  count: number;
};

type AnalyticsSnapshot = {
  total_queries: number;
  failed_queries: number;
  average_latency_ms: number;
  popular_queries: PopularQuery[];
};

export default function App() {
  const [query, setQuery] = useState("fever medicine");
  const [results, setResults] = useState<Result[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [latency, setLatency] = useState<number>(0);
  const [category, setCategory] = useState("");
  const [availability, setAvailability] = useState("");
  const [analytics, setAnalytics] = useState<AnalyticsSnapshot | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const search = async () => {
    try {
      setIsSearching(true);
      setSearchError("");
      const payload = {
        query,
        top_k: 10,
        use_hybrid: true,
        filters: {
          category: category || null,
          availability: availability || null
        }
      };
      const { data } = await axios.post(`${API_BASE}/search`, payload);
      setResults(data.results);
      setLatency(data.latency_ms);
    } catch {
      setSearchError("Unable to search right now. Please check if backend is running.");
    } finally {
      setIsSearching(false);
    }
  };

  const fetchAutocomplete = async (q: string) => {
    if (!q.trim()) {
      setSuggestions([]);
      return;
    }
    const { data } = await axios.get(`${API_BASE}/autocomplete`, { params: { q } });
    setSuggestions(data.suggestions);
  };

  const loadAnalytics = async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/metrics`);
      setAnalytics(data);
    } catch {
      setAnalytics(null);
    }
  };

  useEffect(() => {
    void search();
    void loadAnalytics();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-md sticky top-0 z-40">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 p-2.5 text-white shadow-lg">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                  MediFind
                </h1>
                <p className="text-xs text-gray-500">Smart Medicine Discovery</p>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 text-xs text-gray-600">
              <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full font-medium">
                ⚡ AI-Powered Search
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        {/* Hero Section */}
        <div className="mb-10 text-center">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-3">
            Find Your Medicine <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">Instantly</span>
          </h2>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Search by symptoms, brand names, or generic medicines. Our intelligent hybrid system finds exactly what you need.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3 mb-8">
          {/* Search Panel */}
          <div className="lg:col-span-2">
            <div className="rounded-2xl bg-white shadow-xl overflow-hidden border border-gray-100">
              {/* Search Bar */}
              <div className="bg-gradient-to-r from-cyan-500 to-blue-600 p-8 text-white">
                <div className="relative mb-4">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <svg className="w-5 h-5 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <input
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value);
                      void fetchAutocomplete(e.target.value);
                    }}
                    onKeyDown={(e) => e.key === "Enter" && void search()}
                    className="w-full pl-12 pr-4 py-4 rounded-xl bg-white/20 text-white placeholder-white/60 outline-none transition focus:bg-white/30 border border-white/30 focus:border-white/50"
                    placeholder="Search medicines, symptoms, or brands..."
                  />
                </div>

                {/* Suggestions */}
                {suggestions.length > 0 && (
                  <div className="mb-4 flex flex-wrap gap-2">
                    <span className="text-xs font-semibold text-white/70 w-full">💡 Suggestions:</span>
                    {suggestions.map((s) => (
                      <button
                        key={s}
                        className="px-3 py-1.5 rounded-full bg-white/20 text-white text-sm hover:bg-white/30 transition border border-white/30"
                        onClick={() => {
                          setQuery(s);
                          setSuggestions([]);
                        }}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                )}

                {/* Filter Toggle */}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="text-sm font-medium text-white/80 hover:text-white transition flex items-center gap-2"
                >
                  <svg className={`w-4 h-4 transition ${showFilters ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                  Advanced Filters
                </button>
              </div>

              {/* Filters */}
              {showFilters && (
                <div className="border-t border-gray-100 p-6 bg-gray-50">
                  <div className="grid sm:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                      <input
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        placeholder="e.g. Antibiotic, Painkiller"
                        className="w-full px-4 py-2.5 rounded-lg border border-gray-300 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Availability</label>
                      <select
                        value={availability}
                        onChange={(e) => setAvailability(e.target.value)}
                        className="w-full px-4 py-2.5 rounded-lg border border-gray-300 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                      >
                        <option value="">All</option>
                        <option value="in_stock">In Stock</option>
                        <option value="out_of_stock">Out of Stock</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Search Button & Status */}
              <div className="px-6 py-4 bg-white border-t border-gray-100 flex items-center justify-between gap-4">
                <button
                  onClick={() => void search()}
                  disabled={isSearching}
                  className="flex-1 sm:flex-none px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-lg hover:shadow-lg transition disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {isSearching ? "Searching..." : "Search"}
                </button>
                <div className="flex items-center gap-3 text-sm">
                  <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 font-medium">
                    {results.length} results
                  </span>
                  <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-600">
                    {latency.toFixed(0)}ms
                  </span>
                </div>
              </div>

              {/* Error Message */}
              {searchError && (
                <div className="px-6 py-4 border-t border-gray-100 bg-red-50 flex items-start gap-3">
                  <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="font-medium text-red-900">Connection Error</p>
                    <p className="text-sm text-red-700 mt-1">{searchError}</p>
                  </div>
                </div>
              )}

              {/* Results */}
              <div className="p-6 border-t border-gray-100">
                {isSearching && (
                  <div className="flex justify-center py-12">
                    <div className="space-y-4 w-full max-w-md">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-32 bg-gradient-to-r from-gray-100 to-gray-50 rounded-lg animate-pulse" />
                      ))}
                    </div>
                  </div>
                )}

                {!isSearching && results.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-5xl mb-4">🔍</div>
                    <p className="text-gray-500">No medicines found. Try a different search term.</p>
                  </div>
                )}

                {!isSearching && results.length > 0 && (
                  <div className="space-y-4">
                    {results.map((r) => (
                      <div
                        key={r.medicine_id}
                        className="group rounded-xl border border-gray-200 bg-white p-5 hover:shadow-lg hover:border-blue-300 transition duration-300"
                      >
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <div>
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition">
                              💊 {r.medicine_name}
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">Generic: <span className="font-medium text-gray-900">{r.generic_name}</span></p>
                          </div>
                          <span
                            className={`whitespace-nowrap rounded-full px-4 py-1.5 text-xs font-semibold ${
                              r.stock_status.toLowerCase().includes("in")
                                ? "bg-emerald-100 text-emerald-700"
                                : "bg-amber-100 text-amber-700"
                            }`}
                          >
                            {r.stock_status === "in_stock" ? "✓ In Stock" : "✗ Out of Stock"}
                          </span>
                        </div>

                        <p className="text-gray-700 mb-3">{r.uses}</p>

                        <div className="mb-4 flex flex-wrap gap-2">
                          {r.symptoms.slice(0, 5).map((symptom) => (
                            <span key={symptom} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                              {symptom}
                            </span>
                          ))}
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3 pb-3 border-t border-gray-100">
                          <div>
                            <p className="text-xs text-gray-500">Price</p>
                            <p className="font-bold text-gray-900">₹{r.price}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Score</p>
                            <p className="font-bold text-blue-600">{r.final_score.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">BM25</p>
                            <p className="font-mono text-sm text-gray-900">{r.bm25_score.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Semantic</p>
                            <p className="font-mono text-sm text-gray-900">{r.semantic_score.toFixed(2)}</p>
                          </div>
                        </div>

                        <div className="text-xs text-gray-600 bg-gray-50 rounded-lg p-2">
                          <span className="font-medium">Why matched:</span> {r.why_matched.matching_keywords.join(", ") || "semantic similarity"}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Analytics Sidebar */}
          <div className="rounded-2xl bg-white shadow-xl overflow-hidden border border-gray-100 h-fit">
            <div className="bg-gradient-to-br from-emerald-500 to-teal-600 p-6 text-white">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">📊</span>
                <h2 className="text-xl font-bold">Analytics</h2>
              </div>
              <p className="text-sm text-white/80">Real-time System Performance</p>
            </div>

            {!analytics ? (
              <div className="p-6 text-center">
                <div className="inline-block rounded-full bg-gray-100 p-3 mb-3 animate-spin">
                  <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <p className="text-sm text-gray-500">Loading metrics...</p>
              </div>
            ) : (
              <div className="p-6 space-y-4">
                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 p-4 border border-blue-200">
                    <p className="text-xs text-blue-600 font-medium">Total Queries</p>
                    <p className="text-2xl font-bold text-blue-900 mt-1">{analytics.total_queries}</p>
                  </div>
                  <div className="rounded-xl bg-gradient-to-br from-red-50 to-red-100 p-4 border border-red-200">
                    <p className="text-xs text-red-600 font-medium">Failed</p>
                    <p className="text-2xl font-bold text-red-900 mt-1">{analytics.failed_queries}</p>
                  </div>
                </div>

                <div className="rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100 p-4 border border-emerald-200">
                  <p className="text-xs text-emerald-600 font-medium">⚡ Avg Latency</p>
                  <p className="text-3xl font-bold text-emerald-900 mt-1">{analytics.average_latency_ms}<span className="text-lg">ms</span></p>
                </div>

                {/* Popular Queries */}
                <div className="pt-4 border-t border-gray-200">
                  <p className="text-sm font-bold text-gray-900 mb-3">🔥 Trending Searches</p>
                  {analytics.popular_queries.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-3">No searches yet</p>
                  ) : (
                    <div className="space-y-2">
                      {analytics.popular_queries.slice(0, 5).map((item, idx) => (
                        <div key={item.query} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 hover:bg-gray-100 transition">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="font-bold text-gray-900">#{idx + 1}</span>
                            <span className="text-sm text-gray-700 truncate">{item.query}</span>
                          </div>
                          <span className="ml-2 inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700 whitespace-nowrap">
                            {item.count}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
