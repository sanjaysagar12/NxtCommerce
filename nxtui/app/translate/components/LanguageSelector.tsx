interface LanguageSelectorProps {
  sourceLanguage: string;
  targetLanguage: string;
  onSourceLanguageChange: (language: string) => void;
  onTargetLanguageChange: (language: string) => void;
  onSwapLanguages: () => void;
  sourceLanguages: Array<{ code: string; name: string }>;
  targetLanguages: Array<{ code: string; name: string }>;
  detectedLanguage?: string;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  sourceLanguage,
  targetLanguage,
  onSourceLanguageChange,
  onTargetLanguageChange,
  onSwapLanguages,
  sourceLanguages,
  targetLanguages,
  detectedLanguage
}) => {
  const getLanguageName = (code: string) => {
    const lang = sourceLanguages.find(l => l.code === code) || targetLanguages.find(l => l.code === code);
    return lang ? lang.name : code;
  };

  return (
    <div className="flex items-center gap-4">
      <div className="flex-1">
        <label htmlFor="sourceLanguage" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          From
        </label>
        <select
          id="sourceLanguage"
          value={sourceLanguage}
          onChange={(e) => onSourceLanguageChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          {sourceLanguages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
        {detectedLanguage && sourceLanguage === 'auto' && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Detected: {getLanguageName(detectedLanguage)}
          </p>
        )}
      </div>
      
      <div className="flex-shrink-0 pt-6">
        <button
          type="button"
          onClick={onSwapLanguages}
          disabled={sourceLanguage === 'auto'}
          className="p-2 rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Swap languages"
        >
          <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        </button>
      </div>
      
      <div className="flex-1">
        <label htmlFor="targetLanguage" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          To
        </label>
        <select
          id="targetLanguage"
          value={targetLanguage}
          onChange={(e) => onTargetLanguageChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          {targetLanguages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};