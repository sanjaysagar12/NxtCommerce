"use client";

import { useState } from "react";
import { 
  SparklesIcon,
  DocumentTextIcon,
  ArrowPathIcon
} from "@heroicons/react/24/outline";

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
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleProcessText = async (e?: React.FormEvent) => {
    console.log("Processing text:", textInput);
    if (e) e.preventDefault();
    
    if (!textInput.trim()) {
      return;
    }
    
    const userMessage = { role: 'user', content: textInput };
    setMessages(prev => [...prev, userMessage]);
    setTextInput("");
    setLoading(true);
    
    try {
      const response = await fetch("http://localhost:5000/catalog/process-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textInput,
          action: "summary",
          page: 1,
          limit: 10,
          sortBy: "createdAt",
          sortOrder: "desc"
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        const aiMessage = { 
          role: 'assistant', 
          content: data.text_summary || "No summary available",
          fullData: data
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          role: 'assistant',
          content: data.message || "Failed to process text.",
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (err: any) {
      const errorMessage = {
        role: 'assistant',
        content: err.message || "An error occurred while processing text.",
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const examplePrompts = [
    "Show me current inventory status",
    "I sold 10 products offline today",
    "What products are low in stock?",
    "Add a blue cotton shirt for men priced at ₹799",
    "Find products under 1000 rupees",
    "Generate a business report for the catalog"
  ];

  return (
    <div className="h-screen bg-gradient-to-br from-slate-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      {/* Professional Header */}
      <header className="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700 backdrop-blur-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg">
                <DocumentTextIcon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-200 bg-clip-text text-transparent">
                  Catalog AI Assistant
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                  Professional Inventory Management Solution
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-sm font-medium">
                <span className="w-2 h-2 bg-green-500 rounded-full inline-block mr-2"></span>
                Online
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Container - Full Screen */}
      <div className="flex-1 flex">
        <div className="w-full max-w-6xl mx-auto flex flex-col h-full">
          
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
            {messages.length === 0 && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center max-w-3xl mx-auto">
                  <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-xl mb-8 mx-auto w-fit">
                    <DocumentTextIcon className="w-16 h-16 text-white mx-auto" />
                  </div>
                  <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                    Welcome to Catalog AI
                  </h3>
                  <p className="text-lg text-gray-600 dark:text-gray-400 mb-12 leading-relaxed">
                    Your intelligent inventory management assistant. Ask me anything about your products, stock levels, sales analytics, or catalog operations.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
                    {examplePrompts.map((prompt, index) => (
                      <button
                        key={index}
                        onClick={() => setTextInput(prompt)}
                        className="p-4 text-left bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200 group"
                        disabled={loading}
                      >
                        <div className="flex items-start gap-3">
                          <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
                            <SparklesIcon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                              {prompt}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              Try this example query
                            </p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className="flex items-start gap-3 max-w-[85%]">
                  {message.role === 'assistant' && (
                    <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-md flex-shrink-0">
                      <DocumentTextIcon className="w-5 h-5 text-white" />
                    </div>
                  )}
                  <div
                    className={`px-6 py-4 rounded-2xl shadow-sm ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                        : message.isError
                        ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
                        : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    ) : (
                      <div className="text-sm leading-relaxed">
                        {message.isError ? (
                          <p>{message.content}</p>
                        ) : (
                          <div className="prose dark:prose-invert max-w-none prose-sm">
                            {renderMarkdown(message.content)}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  {message.role === 'user' && (
                    <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-md flex-shrink-0">
                      <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-blue-600">U</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-md">
                    <DocumentTextIcon className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-6 py-4 rounded-2xl shadow-sm">
                    <div className="flex items-center gap-3">
                      <ArrowPathIcon className="w-5 h-5 animate-spin text-blue-600" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Processing your request...
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Professional Input Area */}
          <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4">
            <form onSubmit={handleProcessText} className="flex gap-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Ask about your inventory, products, analytics, or catalog operations..."
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white shadow-sm text-sm placeholder-gray-500 dark:placeholder-gray-400"
                  disabled={loading}
                />
              </div>
              <button
                type="submit"
                disabled={loading || !textInput.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none flex items-center gap-2 font-medium"
              >
                {loading ? (
                  <>
                    <ArrowPathIcon className="w-5 h-5 animate-spin" />
                    Processing
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5" />
                    Send
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}