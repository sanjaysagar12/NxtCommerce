"use client";

import { useState } from "react";
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
  { value: 'summary', label: 'Inventory Summary', icon: ChartBarIcon, description: 'Get detailed stock and inventory analysis' },
  { value: 'search', label: 'Search Products', icon: MagnifyingGlassIcon, description: 'Find products in your catalog' },
  { value: 'add-product', label: 'Add Product', icon: PlusCircleIcon, description: 'Add new product from description' },
  { value: 'analyze', label: 'Analyze', icon: SparklesIcon, description: 'Get insights and recommendations' }
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

// Simple markdown renderer for basic formatting
const renderMarkdown = (text: string) => {
  if (!text) return <div>No content available</div>;
  
  // Split by lines to preserve structure
  const lines = text.split('\n');
  const elements: React.ReactElement[] = [];
  
  lines.forEach((line, index) => {
    // Headers
    if (line.startsWith('# ')) {
      elements.push(<h1 key={index} className="text-2xl font-bold text-gray-900 dark:text-white mb-4">{line.substring(2)}</h1>);
    } else if (line.startsWith('## ')) {
      elements.push(<h2 key={index} className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">{line.substring(3)}</h2>);
    } else if (line.startsWith('### ')) {
      elements.push(<h3 key={index} className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">{line.substring(4)}</h3>);
    }
    // Bold text
    else if (line.includes('**')) {
      const parts = line.split('**');
      const formatted = parts.map((part, i) => 
        i % 2 === 1 ? <strong key={i} className="font-semibold text-gray-900 dark:text-white">{part}</strong> : part
      );
      elements.push(<p key={index} className="text-gray-700 dark:text-gray-300 mb-2">{formatted}</p>);
    }
    // Bullet points
    else if (line.trim().startsWith('• ') || line.trim().startsWith('- ')) {
      elements.push(<li key={index} className="text-gray-700 dark:text-gray-300 ml-4 mb-1">{line.trim().substring(2)}</li>);
    }
    // Code blocks or preformatted text
    else if (line.startsWith('    ') || line.includes('```')) {
      elements.push(<pre key={index} className="bg-gray-100 dark:bg-gray-800 text-sm p-2 rounded font-mono text-gray-800 dark:text-gray-200 mb-2">{line}</pre>);
    }
    // Dividers
    else if (line.includes('━━━') || line.includes('---')) {
      elements.push(<hr key={index} className="border-gray-300 dark:border-gray-600 my-4" />);
    }
    // Empty lines
    else if (line.trim() === '') {
      elements.push(<br key={index} />);
    }
    // Regular text
    else {
      elements.push(<p key={index} className="text-gray-700 dark:text-gray-300 mb-2">{line}</p>);
    }
  });
  
  return <div className="space-y-1">{elements}</div>;
};

export default function CatalogPage() {
  const [textInput, setTextInput] = useState("");
  const [selectedAction, setSelectedAction] = useState("summary");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showJsonView, setShowJsonView] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // Simplified pagination and sorting
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
    "Show me current inventory status",
    "I sold 10 products offline today",
    "What products are low in stock?",
    "Add a blue cotton shirt for men priced at ₹799",
    "Find products under 1000 rupees",
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
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <CheckCircleIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {actionTypes.find(a => a.value === selectedAction)?.label}
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
              {showJsonView ? 'Hide JSON' : 'View JSON'}
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

        {/* Processed Query */}
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Query:</p>
          <p className="text-gray-900 dark:text-white font-medium">"{processed_text}"</p>
        </div>

        {/* Result Content */}
        <div className="space-y-4">
          {showJsonView ? (
            <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          ) : (
            <div className="prose dark:prose-invert max-w-none">
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                {renderMarkdown(text_summary || "No summary available")}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-600 rounded-lg">
              <DocumentTextIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Catalog AI Assistant
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Intelligent inventory management and catalog processing
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Process Request
              </h2>

              <form onSubmit={handleProcessText} className="space-y-4">
                {/* Action Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Action Type
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {actionTypes.map((action) => {
                      const IconComponent = action.icon;
                      return (
                        <button
                          key={action.value}
                          type="button"
                          onClick={() => setSelectedAction(action.value)}
                          className={`p-2 rounded-lg border text-left transition-all ${
                            selectedAction === action.value
                              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                              : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <IconComponent className="w-4 h-4" />
                            <span className="text-sm font-medium">{action.label}</span>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
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
                    Your Request
                  </label>
                  <textarea
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    rows={4}
                    placeholder="Enter your request here..."
                    disabled={loading}
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {textInput.length}/1000 characters
                  </p>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading || !textInput.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <ArrowPathIcon className="w-4 h-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      {getActionIcon(selectedAction)}
                      Process Request
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Example Prompts */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Example Requests
              </h3>
              <div className="space-y-2">
                {examplePrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setTextInput(prompt)}
                    className="w-full text-left p-2 text-sm text-gray-600 dark:text-gray-400 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    disabled={loading}
                  >
                    "{prompt}"
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2">
            {/* Error Display */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-2">
                  <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
                  <div>
                    <h3 className="font-medium text-red-800 dark:text-red-200">Error</h3>
                    <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {result && renderResult()}

            {/* Placeholder when no results */}
            {!result && !error && !loading && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
                <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Ready to Process
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Select an action and enter your request to get started with AI-powered catalog processing.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}