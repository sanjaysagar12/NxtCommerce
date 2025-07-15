"use client";

import { useState } from "react";
import { 
  PlusCircleIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon, 
  SparklesIcon,
  DocumentDuplicateIcon,
  EyeIcon
} from "@heroicons/react/24/outline";

export default function AddProductPage() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showJson, setShowJson] = useState(false);

  const handleAddProduct = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError("");
    setResult(null);
    if (!prompt.trim()) {
      setError("Please enter a product description.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/add-product", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: prompt }),
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.message || "Failed to add product.");
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const examplePrompts = [
    "Add a red cotton kurta for women priced at ₹999 with 20% discount, available in sizes S and M. 10 in stock. Category: Ethnic Wear. Fabric: Cotton. Sleeve: 3/4th.",
    "Add a blue denim jacket for men priced at ₹1499 with 15% discount, available in sizes M, L, XL. 25 in stock. Category: Casual Wear. Fabric: Denim.",
    "Add a black silk saree for women priced at ₹2499 with 10% discount, available in one size. 15 in stock. Category: Traditional Wear. Fabric: Silk.",
    "Add a white cotton t-shirt for men priced at ₹599 with 25% discount, available in sizes S, M, L, XL. 50 in stock. Category: Casual Wear. Fabric: Cotton."
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-sm border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                Add New Product
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Create products with natural language descriptions
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                <SparklesIcon className="h-4 w-4" />
                <span>AI-Powered</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Input Form */}
          <div className="space-y-6">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-xl">
                  <PlusCircleIcon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Product Description</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Describe your product in natural language</p>
                </div>
              </div>

              <form onSubmit={handleAddProduct} className="space-y-4">
                <div className="relative">
                  <textarea
                    className="w-full px-4 py-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none transition-all duration-200 shadow-sm"
                    placeholder="Describe the product you want to add... (e.g., 'Add a red cotton kurta for women priced at ₹999 with 20% discount, available in sizes S and M. 10 in stock. Category: Ethnic Wear. Fabric: Cotton. Sleeve: 3/4th.')"
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    disabled={loading}
                    rows={8}
                  />
                  <div className="absolute bottom-3 right-3 text-xs text-gray-400">
                    {prompt.length}/1000
                  </div>
                </div>
                
                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-8 py-3 bg-gradient-to-r from-emerald-600 to-blue-600 text-white font-semibold rounded-xl hover:from-emerald-700 hover:to-blue-700 transition-all duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        <span>Adding Product...</span>
                      </>
                    ) : (
                      <>
                        <PlusCircleIcon className="h-5 w-5" />
                        <span>Add Product</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* Example Prompts */}
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <SparklesIcon className="h-5 w-5 mr-2 text-emerald-600" />
                Example Prompts
              </h3>
              <div className="space-y-3">
                {examplePrompts.map((example, index) => (
                  <div 
                    key={index}
                    className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                    onClick={() => setPrompt(example)}
                  >
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                      {example}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 backdrop-blur-sm border border-red-200 dark:border-red-800 rounded-2xl p-6 shadow-lg">
                <div className="flex items-center space-x-3">
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-500 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-red-900 dark:text-red-400">Error</h3>
                    <p className="text-red-700 dark:text-red-300 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Success Result */}
            {result && (
              <div className="bg-green-50 dark:bg-green-900/20 backdrop-blur-sm border border-green-200 dark:border-green-800 rounded-2xl shadow-lg overflow-hidden">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                      <div>
                        <h3 className="text-lg font-semibold text-green-900 dark:text-green-400">
                          Product Added Successfully!
                        </h3>
                        <p className="text-green-700 dark:text-green-300 text-sm mt-1">
                          {result.message}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowJson(!showJson)}
                      className="p-2 text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300 transition-colors"
                      title={showJson ? "Hide JSON" : "Show JSON"}
                    >
                      <EyeIcon className="h-5 w-5" />
                    </button>
                  </div>

                  {/* Product Preview */}
                  {result.product_json && (
                    <div className="bg-white/60 dark:bg-gray-800/60 rounded-xl p-4 border border-green-200 dark:border-green-700 mb-4">
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Product Preview</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Name:</span>
                          <span className="font-medium text-gray-900 dark:text-white">{result.product_json.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Price:</span>
                          <span className="font-medium text-gray-900 dark:text-white">₹{result.product_json.price}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Discount:</span>
                          <span className="font-medium text-green-600 dark:text-green-400">{result.product_json.discount}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Stock:</span>
                          <span className="font-medium text-gray-900 dark:text-white">{result.product_json.stock}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">SKU:</span>
                          <span className="font-medium text-gray-900 dark:text-white">{result.product_json.sku}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* JSON Display */}
                  {showJson && result.product_json && (
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-green-900 dark:text-green-400">Generated JSON</h4>
                        <button
                          onClick={() => copyToClipboard(JSON.stringify(result.product_json, null, 2))}
                          className="flex items-center space-x-1 text-xs text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300 transition-colors"
                        >
                          <DocumentDuplicateIcon className="h-4 w-4" />
                          <span>Copy</span>
                        </button>
                      </div>
                      <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-96">
                        <pre className="text-xs text-green-400 whitespace-pre-wrap">
                          {JSON.stringify(result.product_json, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tips Card */}
            <div className="bg-blue-50 dark:bg-blue-900/20 backdrop-blur-sm border border-blue-200 dark:border-blue-800 rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-400 mb-4 flex items-center">
                <SparklesIcon className="h-5 w-5 mr-2" />
                Tips for Better Results
              </h3>
              <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-300">
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Include specific details like color, material, size, and price</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Mention stock quantity and discount percentage if applicable</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Specify the target audience (men, women, kids)</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Add category information for better organization</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
