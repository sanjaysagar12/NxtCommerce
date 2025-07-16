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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <DocumentTextIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Catalog AI Assistant
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your intelligent inventory assistant
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-[600px] flex flex-col">
          
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Welcome to Catalog AI
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Ask me anything about your inventory, products, or catalog management.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl mx-auto">
                  {examplePrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => setTextInput(prompt)}
                      className="p-3 text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-left"
                      disabled={loading}
                    >
                      "{prompt}"
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.isError
                      ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                  }`}
                >
                  {message.role === 'user' ? (
                    <p className="text-sm">{message.content}</p>
                  ) : (
                    <div className="text-sm">
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
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white px-4 py-3 rounded-lg">
                  <div className="flex items-center gap-2">
                    <ArrowPathIcon className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Processing...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <form onSubmit={handleProcessText} className="flex gap-2">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Ask about your inventory, products, or catalog..."
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !textInput.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                {loading ? (
                  <ArrowPathIcon className="w-4 h-4 animate-spin" />
                ) : (
                  <SparklesIcon className="w-4 h-4" />
                )}
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}