"use client";

import { useState } from "react";
import { MagnifyingGlassIcon, ExclamationTriangleIcon, HeartIcon, ShoppingCartIcon } from "@heroicons/react/24/outline";
import { HeartIcon as HeartIconSolid } from "@heroicons/react/24/solid";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

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

  const toggleFavorite = (productId: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(productId)) {
      newFavorites.delete(productId);
    } else {
      newFavorites.add(productId);
    }
    setFavorites(newFavorites);
  };

  const quickSearches = [
    "Red cotton kurta under ₹1000",
    "Women's dresses",
    "Men's shirts",
    "Silk sarees",
    "Ethnic wear",
    "Formal wear"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-sm border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Smart Search
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Find exactly what you're looking for
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {results && `${results.length} result${results.length !== 1 ? 's' : ''}`}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="mb-12">
          <form onSubmit={handleSearch} className="max-w-4xl mx-auto">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="w-full pl-12 pr-32 py-4 text-lg rounded-2xl border-2 border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg transition-all duration-200"
                placeholder="Describe what you're looking for (e.g. 'red cotton kurta under ₹1000')"
                value={query}
                onChange={e => setQuery(e.target.value)}
                disabled={loading}
              />
              <button
                type="submit"
                className="absolute inset-y-0 right-0 flex items-center pr-3"
                disabled={loading}
              >
                <div className="px-6 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
                  {loading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                      Searching...
                    </div>
                  ) : (
                    "Search"
                  )}
                </div>
              </button>
            </div>
          </form>

          {/* Quick Search Tags */}
          <div className="max-w-4xl mx-auto mt-6">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">Quick searches:</p>
            <div className="flex flex-wrap gap-2">
              {quickSearches.map((quickSearch, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(quickSearch);
                    // Auto-search on click
                    setTimeout(() => {
                      const event = new Event('submit', { bubbles: true, cancelable: true });
                      document.querySelector('form')?.dispatchEvent(event);
                    }, 100);
                  }}
                  className="px-4 py-2 bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm border border-gray-200 dark:border-gray-600 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-600 transition-all duration-200 shadow-sm"
                >
                  {quickSearch}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 max-w-4xl mx-auto">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-3 flex-shrink-0" />
              <span className="text-red-700 dark:text-red-300">{error}</span>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="mb-8">
            {results.length === 0 ? (
              <div className="text-center py-12">
                <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 dark:border-gray-700 shadow-lg max-w-md mx-auto">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                    <MagnifyingGlassIcon className="h-8 w-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No products found</h3>
                  <p className="text-gray-600 dark:text-gray-400">Try adjusting your search terms or browse our categories</p>
                </div>
              </div>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {results.map((product: any, idx: number) => (
                  <div 
                    key={product.id || product.sku || idx} 
                    className="group bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                  >
                    {/* Product Image */}
                    <div className="relative aspect-square bg-gray-100 dark:bg-gray-700 overflow-hidden">
                      {product.thumbnail ? (
                        <img
                          src={product.thumbnail}
                          alt={product.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          loading="lazy"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <div className="w-16 h-16 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center">
                            <MagnifyingGlassIcon className="h-8 w-8 text-gray-400" />
                          </div>
                        </div>
                      )}
                      
                      {/* Favorite Button */}
                      <button
                        onClick={() => toggleFavorite(product.id || product.sku || idx.toString())}
                        className="absolute top-3 right-3 p-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full shadow-md hover:bg-white dark:hover:bg-gray-800 transition-all duration-200"
                      >
                        {favorites.has(product.id || product.sku || idx.toString()) ? (
                          <HeartIconSolid className="h-5 w-5 text-red-500" />
                        ) : (
                          <HeartIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                        )}
                      </button>

                      {/* Discount Badge */}
                      {product.discount && (
                        <div className="absolute top-3 left-3 bg-gradient-to-r from-green-500 to-green-600 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-md">
                          {product.discount}% OFF
                        </div>
                      )}
                    </div>

                    {/* Product Info */}
                    <div className="p-4">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        {product.name}
                      </h3>
                      
                      {/* Price */}
                      {product.price && (
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <span className="text-2xl font-bold text-gray-900 dark:text-white">
                              ₹{product.price.toLocaleString()}
                            </span>
                            {product.discount && (
                              <span className="text-sm text-gray-500 dark:text-gray-400 line-through">
                                ₹{Math.round(product.price / (1 - product.discount / 100)).toLocaleString()}
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Description */}
                      {product.description && (
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-3 line-clamp-2">
                          {product.description}
                        </p>
                      )}

                      {/* Stock and Add to Cart */}
                      <div className="flex items-center justify-between">
                        {product.stock !== undefined && (
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            product.stock > 0 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                              : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                          }`}>
                            {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                          </span>
                        )}
                        
                        <button 
                          className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-md disabled:opacity-50"
                          disabled={product.stock === 0}
                        >
                          <ShoppingCartIcon className="h-4 w-4" />
                          <span>Add to Cart</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
