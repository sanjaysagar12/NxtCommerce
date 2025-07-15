"use client";

import { useState } from "react";

export default function AddProductPage() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">Add Product (Prompt)</h1>
        <form onSubmit={handleAddProduct} className="flex flex-col gap-4 mb-8">
          <textarea
            className="flex-1 px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-base bg-white dark:bg-gray-900 dark:text-white min-h-[100px] resize-y"
            placeholder="Describe the product you want to add (e.g. 'Add a red cotton kurta for women priced at ₹999 with 20% discount, available in sizes S and M. 10 in stock. Category: Ethnic Wear. Fabric: Cotton. Sleeve: 3/4th. Includes 3 images.')"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="px-6 py-2 rounded-md bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors disabled:opacity-60 self-end"
            disabled={loading}
          >
            {loading ? "Adding..." : "Add Product"}
          </button>
        </form>
        {error && (
          <div className="mb-6 text-red-600 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-3 text-center">
            {error}
          </div>
        )}
        {result && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded p-4">
            <h2 className="text-lg font-semibold text-green-900 dark:text-green-400 mb-2">Product Added!</h2>
            <div className="overflow-x-auto text-xs">
              <pre className="whitespace-pre-wrap break-all text-green-800 dark:text-green-200">{JSON.stringify(result.product_json, null, 2)}</pre>
            </div>
            <div className="mt-2 text-green-700 dark:text-green-300">{result.message}</div>
          </div>
        )}
      </div>
    </div>
  );
}
