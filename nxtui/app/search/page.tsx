"use client";

import { useState } from "react";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError("");
    setResults(null);
    if (!query.trim()) {
      setError("Please enter a search query.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/search-products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: query }),
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.message || "Search failed.");
        setResults(null);
      } else {
        // Try to find product list in common places
        let products = data.results?.products || data.results?.data || data.results || [];
        if (!Array.isArray(products) && products.items) products = products.items;
        setResults(products);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred.");
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">Product Search</h1>
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4 mb-8">
          <input
            type="text"
            className="flex-1 px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-base bg-white dark:bg-gray-900 dark:text-white"
            placeholder="Describe what you're looking for (e.g. 'red cotton kurta under ₹1000')"
            value={query}
            onChange={e => setQuery(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="px-6 py-2 rounded-md bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors disabled:opacity-60"
            disabled={loading}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
        {error && (
          <div className="mb-6 text-red-600 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-3 text-center">
            {error}
          </div>
        )}
        {results && (
          <div>
            {results.length === 0 ? (
              <div className="text-center text-gray-500">No products found.</div>
            ) : (
              <ul className="grid gap-6 sm:grid-cols-2">
                {results.map((product: any, idx: number) => (
                  <li key={product.id || product.sku || idx} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 flex flex-col gap-2 border border-gray-100 dark:border-gray-700">
                    {product.thumbnail && (
                      <img
                        src={product.thumbnail}
                        alt={product.name}
                        className="w-full h-40 object-cover rounded mb-2"
                        loading="lazy"
                      />
                    )}
                    <h2 className="text-lg font-semibold text-foreground">{product.name}</h2>
                    {product.price && (
                      <div className="text-blue-700 dark:text-blue-300 font-bold text-base">
                        ₹{product.price}
                        {product.discount && (
                          <span className="ml-2 text-green-600 dark:text-green-400 font-medium text-sm">
                            {product.discount}% off
                          </span>
                        )}
                      </div>
                    )}
                    {product.description && (
                      <p className="text-gray-700 dark:text-gray-300 text-sm line-clamp-3">{product.description}</p>
                    )}
                    {product.stock !== undefined && (
                      <div className="text-xs text-gray-500">Stock: {product.stock}</div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
