"use client";

import { useState, useRef, useEffect } from "react";
import { 
  MagnifyingGlassIcon, 
  SparklesIcon,
  DocumentTextIcon,
  PlusCircleIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClipboardDocumentIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowPathIcon
} from "@heroicons/react/24/outline";

// Action types for catalog processing
const actionTypes = [
  { value: 'summary', label: 'AI Summary', icon: SparklesIcon, description: 'Generate intelligent catalog summary' },
  { value: 'search', label: 'Search Products', icon: MagnifyingGlassIcon, description: 'Search through catalog' },
  { value: 'add-product', label: 'Add Product', icon: PlusCircleIcon, description: 'Add new product from text' },
  { value: 'analyze', label: 'Analyze Text', icon: ChartBarIcon, description: 'Analyze text for insights' }
];

// Sort options
const sortOptions = [
  { value: 'createdAt', label: 'Created Date' },
  { value: 'name', label: 'Product Name' },
  { value: 'price', label: 'Price' },
  { value: 'stock', label: 'Stock' }
];

const sortOrders = [
  { value: 'desc', label: 'Descending' },
  { value: 'asc', label: 'Ascending' }
];

export default function CatalogPage() {
  const [textInput, setTextInput] = useState("");
  const [selectedAction, setSelectedAction] = useState("summary");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showJsonView, setShowJsonView] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // Pagination and sorting states
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [sortBy, setSortBy] = useState("createdAt");
  const [sortOrder, setSortOrder] = useState("desc");

  const handleProcessText = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    setError("");
    setResult(null);
    
    if (!textInput.trim()) {
      setError("Please enter some text to process.");
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await fetch("http://localhost:5000/catalog/process-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textInput,
          action: selectedAction,
          page: page,
          limit: limit,
          sortBy: sortBy,
          sortOrder: sortOrder
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResult(data);
      } else {
        setError(data.message || "Failed to process text.");
        setResult(null);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred while processing text.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const examplePrompts = [
    "Show me products under 1000 rupees",
    "What are the most popular product categories?",
    "Add a blue cotton shirt for men priced at ₹799",
    "Analyze the current stock levels",
    "Find all products with low stock",
    "Generate a business report for the catalog"
  ];

  const getActionIcon = (action: string) => {
    const actionType = actionTypes.find(a => a.value === action);
    if (actionType) {
      const IconComponent = actionType.icon;
      return <IconComponent className="w-5 h-5" />;
    }
    return <DocumentTextIcon className="w-5 h-5" />;
  };

  const renderResult = () => {
    if (!result) return null;

    const { text_summary, processed_text, message } = result;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <CheckCircleIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Processing Complete
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {message}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowJsonView(!showJsonView)}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
            >
              {showJsonView ? <EyeSlashIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
              {showJsonView ? 'Hide' : 'Show'} JSON
            </button>
            <button
              onClick={() => copyToClipboard(text_summary || JSON.stringify(result, null, 2))}
              className="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors flex items-center gap-2"
            >
              <ClipboardDocumentIcon className="w-4 h-4" />
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </div>

        {/* Processed Text Display */}
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Processed Text:</p>
          <p className="text-gray-900 dark:text-white font-medium">"{processed_text}"</p>
        </div>

        {/* Result Content */}
        <div className="space-y-4">
          {showJsonView ? (
            <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          ) : (
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                {getActionIcon(selectedAction)}
                <h4 className="font-semibold text-blue-900 dark:text-blue-100">
                  {actionTypes.find(a => a.value === selectedAction)?.label} Result:
                </h4>
              </div>
              <div className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                {text_summary || "No summary available"}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-sm border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
                <DocumentTextIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Catalog AI
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Process text with AI-powered catalog intelligence
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full text-sm font-medium flex items-center gap-1">
                <SparklesIcon className="w-4 h-4" />
                AI-Powered
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Text Input & Processing
              </h2>

              <form onSubmit={handleProcessText} className="space-y-4">
                {/* Action Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Select Action
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {actionTypes.map((action) => {
                      const IconComponent = action.icon;
                      return (
                        <button
                          key={action.value}
                          type="button"
                          onClick={() => setSelectedAction(action.value)}
                          className={`p-3 rounded-lg border transition-all ${
                            selectedAction === action.value
                              ? 'border-purple-300 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                              : 'border-gray-200 dark:border-gray-600 hover:border-purple-200 dark:hover:border-purple-700'
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            <IconComponent className="w-5 h-5" />
                            <span className="text-sm font-medium">{action.label}</span>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {action.description}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Text Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Enter your text ({textInput.length}/2000)
                  </label>
                  <textarea
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    rows={6}
                    maxLength={2000}
                    placeholder="Enter your text here... For example: 'Show me products under 1000 rupees' or 'Add a blue cotton shirt for men'"
                    disabled={loading}
                  />
                </div>

                {/* Options */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Page
                    </label>
                    <input
                      type="number"
                      value={page}
                      onChange={(e) => setPage(parseInt(e.target.value) || 1)}
                      min="1"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      disabled={loading}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Limit
                    </label>
                    <input
                      type="number"
                      value={limit}
                      onChange={(e) => setLimit(parseInt(e.target.value) || 10)}
                      min="1"
                      max="50"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      disabled={loading}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Sort By
                    </label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      disabled={loading}
                    >
                      {sortOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Order
                    </label>
                    <select
                      value={sortOrder}
                      onChange={(e) => setSortOrder(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      disabled={loading}
                    >
                      {sortOrders.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading || !textInput.trim()}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-medium py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <ArrowPathIcon className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      {getActionIcon(selectedAction)}
                      Process Text
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Example Prompts */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Example Prompts
              </h3>
              <div className="space-y-2">
                {examplePrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setTextInput(prompt)}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all"
                    disabled={loading}
                  >
                    <span className="text-gray-700 dark:text-gray-300 text-sm">
                      "{prompt}"
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {/* Error Display */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
                <div className="flex items-center gap-3">
                  <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
                  <div>
                    <h3 className="font-semibold text-red-800 dark:text-red-200">Error</h3>
                    <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {result && renderResult()}

            {/* Placeholder when no results */}
            {!result && !error && !loading && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
                <DocumentTextIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Ready to Process
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Enter your text and select an action to get started with AI-powered catalog processing.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}