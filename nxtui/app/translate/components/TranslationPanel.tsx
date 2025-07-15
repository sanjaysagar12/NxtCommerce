interface TranslationPanelProps {
  sourceText: string;
  translatedText: string;
  onSourceTextChange: (text: string) => void;
  onClearSource: () => void;
  onCopyTranslation: () => void;
  onDetectLanguage: () => void;
  isLoading: boolean;
  isDetecting: boolean;
  maxLength?: number;
}

export const TranslationPanel: React.FC<TranslationPanelProps> = ({
  sourceText,
  translatedText,
  onSourceTextChange,
  onClearSource,
  onCopyTranslation,
  onDetectLanguage,
  isLoading,
  isDetecting,
  maxLength = 5000
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Source Text Panel */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Source Text
          </label>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onDetectLanguage}
              disabled={!sourceText.trim() || isDetecting}
              className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDetecting ? 'Detecting...' : 'Detect Language'}
            </button>
            <button
              type="button"
              onClick={onClearSource}
              className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md"
            >
              Clear
            </button>
          </div>
        </div>
        
        <textarea
          value={sourceText}
          onChange={(e) => onSourceTextChange(e.target.value)}
          placeholder="Enter text to translate..."
          maxLength={maxLength}
          rows={12}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none"
        />
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {sourceText.length}/{maxLength}
          </span>
        </div>
      </div>

      {/* Translated Text Panel */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Translation
          </label>
          <button
            type="button"
            onClick={onCopyTranslation}
            disabled={!translatedText}
            className="text-xs px-2 py-1 bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800 text-green-700 dark:text-green-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Copy
          </button>
        </div>
        
        <div className="relative">
          <textarea
            value={translatedText}
            readOnly
            placeholder={isLoading ? "Translating..." : "Translation will appear here..."}
            rows={12}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none"
          />
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white dark:bg-gray-800 bg-opacity-75">
              <div className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="text-sm text-gray-600 dark:text-gray-400">Translating...</span>
              </div>
            </div>
          )}
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {translatedText.length} characters
          </span>
        </div>
      </div>
    </div>
  );
};