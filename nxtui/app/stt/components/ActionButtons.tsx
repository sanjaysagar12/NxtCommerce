interface ActionButtonsProps {
  onSubmit: () => void;
  onClear: () => void;
  isLoading: boolean;
  hasAudioFile: boolean;
}

export const ActionButtons: React.FC<ActionButtonsProps> = ({
  onSubmit,
  onClear,
  isLoading,
  hasAudioFile
}) => {
  return (
    <div className="flex gap-4">
      <button
        type="button"
        onClick={onSubmit}
        disabled={!hasAudioFile || isLoading}
        className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        {isLoading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Converting...
          </span>
        ) : (
          'Convert to Text'
        )}
      </button>
      
      <button
        type="button"
        onClick={onClear}
        className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
      >
        Clear
      </button>
    </div>
  );
};