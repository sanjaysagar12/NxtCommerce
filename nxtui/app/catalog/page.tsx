"use client";

import { useState, useRef, useEffect } from "react";
import { 
  SparklesIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  MicrophoneIcon,
  StopIcon,
  LanguageIcon,
  SpeakerWaveIcon,
  ChevronDownIcon
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
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isTranslating, setIsTranslating] = useState(false);
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [ttsError, setTtsError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Supported languages
  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    {code:"ta", name:"Tamil", flag:"🇮🇳"},
    { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
    { code: 'es', name: 'Spanish', flag: '🇪🇸' },
    { code: 'fr', name: 'French', flag: '🇫🇷' },
    { code: 'de', name: 'German', flag: '🇩🇪' },
    { code: 'it', name: 'Italian', flag: '🇮🇹' },
    { code: 'pt', name: 'Portuguese', flag: '🇵🇹' },
    { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
    { code: 'ko', name: 'Korean', flag: '🇰🇷' },
    { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
    { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
    { code: 'ru', name: 'Russian', flag: '🇷🇺' }
  ];

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      setSpeechSupported(true);
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = selectedLanguage === 'en' ? 'en-US' : 
                                    selectedLanguage === 'ta' ? 'ta-IN' :
                                  selectedLanguage === 'hi' ? 'hi-IN' :
                                  selectedLanguage === 'es' ? 'es-ES' :
                                  selectedLanguage === 'fr' ? 'fr-FR' :
                                  selectedLanguage === 'de' ? 'de-DE' :
                                  selectedLanguage === 'it' ? 'it-IT' :
                                  selectedLanguage === 'pt' ? 'pt-PT' :
                                  selectedLanguage === 'ja' ? 'ja-JP' :
                                  selectedLanguage === 'ko' ? 'ko-KR' :
                                  selectedLanguage === 'zh' ? 'zh-CN' :
                                  selectedLanguage === 'ar' ? 'ar-SA' :
                                  selectedLanguage === 'ru' ? 'ru-RU' : 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setTextInput(transcript);
        setIsListening(false);
        setSpeechError(null);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        
        // Handle different types of speech recognition errors
        switch(event.error) {
          case 'no-speech':
            setSpeechError('No speech detected. Please try speaking again.');
            break;
          case 'audio-capture':
            setSpeechError('Audio capture failed. Please check your microphone.');
            break;
          case 'not-allowed':
            setSpeechError('Microphone access denied. Please allow microphone access.');
            break;
          case 'network':
            setSpeechError('Network error. Please check your connection.');
            break;
          case 'aborted':
            setSpeechError('Speech recognition was aborted.');
            break;
          default:
            setSpeechError(`Speech recognition error: ${event.error}`);
        }
        
        // Clear error after 5 seconds
        setTimeout(() => setSpeechError(null), 5000);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        // Don't set error here as it might be a normal end
      };

      recognitionRef.current.onstart = () => {
        setSpeechError(null);
      };
    }
  }, [selectedLanguage]);

  const startListening = () => {
    if (recognitionRef.current && speechSupported) {
      setSpeechError(null);
      setIsListening(true);
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        setIsListening(false);
        setSpeechError('Failed to start speech recognition. Please try again.');
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping speech recognition:', error);
      }
      setIsListening(false);
    }
  };

  const handleProcessText = async (e?: React.FormEvent) => {
    console.log("Processing text:", textInput);
    if (e) e.preventDefault();
    
    if (!textInput.trim()) {
      return;
    }
    
    let processedText = textInput;
    
    // Translate to English if not already in English
    if (selectedLanguage !== 'en') {
      setIsTranslating(true);
      try {
        const translateResponse = await fetch("http://localhost:5000/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: textInput,
            target_language: "en",
            source_language: selectedLanguage
          }),
        });
        
        const translateData = await translateResponse.json();
        if (translateData.success) {
          processedText = translateData.translated_text;
        }
      } catch (error) {
        console.error("Translation error:", error);
      } finally {
        setIsTranslating(false);
      }
    }
    
    const userMessage = { role: 'user', content: textInput, language: selectedLanguage };
    setMessages(prev => [...prev, userMessage]);
    setTextInput("");
    setLoading(true);
    
    try {
      const response = await fetch("http://localhost:5000/catalog/process-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: processedText, // Use translated text for processing
          action: "summary",
          page: 1,
          limit: 10,
          sortBy: "createdAt",
          sortOrder: "desc"
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        let aiResponse = data.text_summary || "No summary available";
        
        // Translate AI response back to user's language if not English
        if (selectedLanguage !== 'en') {
          try {
            const translateResponse = await fetch("http://localhost:5000/translate", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                text: aiResponse,
                target_language: selectedLanguage,
                source_language: "en"
              }),
            });
            
            const translateData = await translateResponse.json();
            if (translateData.success) {
              aiResponse = translateData.translated_text;
            }
          } catch (error) {
            console.error("Translation error:", error);
          }
        }
        
        const aiMessage = { 
          role: 'assistant', 
          content: aiResponse,
          language: selectedLanguage,
          fullData: data
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        let errorMessage = data.message || "Failed to process text.";
        
        // Translate error message if needed
        if (selectedLanguage !== 'en') {
          try {
            const translateResponse = await fetch("http://localhost:5000/translate", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                text: errorMessage,
                target_language: selectedLanguage,
                source_language: "en"
              }),
            });
            
            const translateData = await translateResponse.json();
            if (translateData.success) {
              errorMessage = translateData.translated_text;
            }
          } catch (error) {
            console.error("Translation error:", error);
          }
        }
        
        const errorMsg = {
          role: 'assistant',
          content: errorMessage,
          language: selectedLanguage,
          isError: true
        };
        setMessages(prev => [...prev, errorMsg]);
      }
    } catch (err: any) {
      let errorMessage = err.message || "An error occurred while processing text.";
      
      // Translate error message if needed
      if (selectedLanguage !== 'en') {
        try {
          const translateResponse = await fetch("http://localhost:5000/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: errorMessage,
              target_language: selectedLanguage,
              source_language: "en"
            }),
          });
          
          const translateData = await translateResponse.json();
          if (translateData.success) {
            errorMessage = translateData.translated_text;
          }
        } catch (error) {
          console.error("Translation error:", error);
        }
      }
      
      const errorMsg = {
        role: 'assistant',
        content: errorMessage,
        language: selectedLanguage,
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // Text-to-speech function
  const playTextToSpeech = async (text: string) => {
    if (isPlayingAudio) return;
    
    try {
      setIsPlayingAudio(true);
      setTtsError(null);
      
      const response = await fetch("http://localhost:5000/text-to-audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          language: selectedLanguage
        }),
      });
      
      const data = await response.json();
      if (data.success && data.audio_file_id) {
        // Play the audio
        const audioUrl = `http://localhost:5000/download-audio/${data.audio_file_id}`;
        if (audioRef.current) {
          audioRef.current.src = audioUrl;
          await audioRef.current.play();
        }
      } else {
        setTtsError(data.message || "Failed to generate speech");
        setIsPlayingAudio(false);
      }
    } catch (error) {
      console.error("Text-to-speech error:", error);
      setTtsError("Text-to-speech service is not available");
      setIsPlayingAudio(false);
      
      // Clear TTS error after 5 seconds
      setTimeout(() => setTtsError(null), 5000);
    }
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
    <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex flex-col">
      {/* Professional Header */}
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-lg border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-10">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg">
                <DocumentTextIcon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Catalog AI Assistant
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                  Professional Inventory Management Solution
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* Language Selector */}
              <div className="relative">
                <button
                  onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                  className="flex items-center gap-2 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm font-medium hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                  <LanguageIcon className="w-4 h-4" />
                  <span>{languages.find(l => l.code === selectedLanguage)?.flag}</span>
                  <span className="hidden sm:inline">{languages.find(l => l.code === selectedLanguage)?.name}</span>
                  <ChevronDownIcon className="w-3 h-3" />
                </button>
                
                {showLanguageDropdown && (
                  <div className="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                    <div className="p-2 max-h-60 overflow-y-auto">
                      {languages.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => {
                            setSelectedLanguage(lang.code);
                            setShowLanguageDropdown(false);
                          }}
                          className={`w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                            selectedLanguage === lang.code ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'
                          }`}
                        >
                          <span className="text-lg">{lang.flag}</span>
                          <span className="text-sm">{lang.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
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
                        className="p-4 text-left bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 dark:border-gray-700/50 hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200 group"
                        disabled={loading}
                      >
                        <div className="flex items-start gap-3">
                          <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
                            <SparklesIcon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                              {prompt}
                            </p>
                            <div className="flex items-center justify-between">
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                Try this example query
                              </p>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  playTextToSpeech(prompt);
                                }}
                                disabled={isPlayingAudio}
                                className="flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors text-xs opacity-0 group-hover:opacity-100"
                              >
                                <SpeakerWaveIcon className="w-3 h-3" />
                                {isPlayingAudio ? 'Playing...' : 'Listen'}
                              </button>
                            </div>
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
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : message.isError
                        ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
                        : 'bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm text-gray-900 dark:text-white border border-gray-200/50 dark:border-gray-700/50'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <div>
                        <p className="text-sm leading-relaxed mb-3">{message.content}</p>
                        {/* Text-to-speech button for user messages */}
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => playTextToSpeech(message.content)}
                            disabled={isPlayingAudio}
                            className="flex items-center gap-1 px-2 py-1 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors text-xs"
                          >
                            <SpeakerWaveIcon className="w-3 h-3" />
                            {isPlayingAudio ? 'Playing...' : 'Listen'}
                          </button>
                          <span className="text-xs text-white/70">
                            {languages.find(l => l.code === message.language)?.name}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="text-sm leading-relaxed">
                        {message.isError ? (
                          <p>{message.content}</p>
                        ) : (
                          <div>
                            <div className="prose dark:prose-invert max-w-none prose-sm">
                              {renderMarkdown(message.content)}
                            </div>
                            {/* Text-to-speech button for AI responses */}
                            <div className="mt-3 flex items-center gap-2">
                              <button
                                onClick={() => playTextToSpeech(message.content)}
                                disabled={isPlayingAudio}
                                className="flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors text-xs"
                              >
                                <SpeakerWaveIcon className="w-3 h-3" />
                                {isPlayingAudio ? 'Playing...' : 'Listen'}
                              </button>
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {languages.find(l => l.code === message.language)?.name}
                              </span>
                            </div>
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
                  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 px-6 py-4 rounded-2xl shadow-sm">
                    <div className="flex items-center gap-3">
                      <ArrowPathIcon className="w-5 h-5 animate-spin text-blue-600" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {isTranslating ? 'Translating...' : 'Processing your request...'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Professional Input Area */}
          <div className="border-t border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm px-6 py-4">
            {/* Speech Error Display */}
            {speechError && (
              <div className="mb-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-700 dark:text-yellow-300">{speechError}</p>
              </div>
            )}
            
            {/* TTS Error Display */}
            {ttsError && (
              <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-700 dark:text-red-300">{ttsError}</p>
              </div>
            )}
            
            <form onSubmit={handleProcessText} className="flex gap-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Ask about your inventory, products, analytics, or catalog operations..."
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700/80 dark:text-white shadow-sm text-sm placeholder-gray-500 dark:placeholder-gray-400 bg-white/80 backdrop-blur-sm"
                  disabled={loading}
                />
              </div>
              
              {/* Voice Input Button */}
              {speechSupported && (
                <button
                  type="button"
                  onClick={isListening ? stopListening : startListening}
                  disabled={loading}
                  className={`px-4 py-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none flex items-center gap-2 font-medium ${
                    isListening
                      ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white'
                      : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white'
                  }`}
                >
                  {isListening ? (
                    <>
                      <StopIcon className="w-5 h-5" />
                      <span className="hidden sm:inline">Stop</span>
                    </>
                  ) : (
                    <>
                      <MicrophoneIcon className="w-5 h-5" />
                      <span className="hidden sm:inline">Speak</span>
                    </>
                  )}
                </button>
              )}
              
              <button
                type="submit"
                disabled={loading || !textInput.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none flex items-center gap-2 font-medium"
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

      {/* Hidden audio element for text-to-speech */}
      <audio ref={audioRef} onEnded={() => setIsPlayingAudio(false)} />
    </div>
  );
}