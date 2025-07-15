interface ResultDisplayProps {
  result: string;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result }) => {
  if (!result) return null;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result);
  };

  return (
    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
      <h3 className="text-lg font-medium text-green-900 dark:text-green-400 mb-2">
        Transcribed Text:
      </h3>
      <div className="bg-white dark:bg-gray-800 rounded-md p-4 border">
        <p className="text-gray-900 dark:text-gray-100 leading-relaxed">
          {result}
        </p>
      </div>
      <button
        onClick={copyToClipboard}
        className="mt-3 text-sm text-green-700 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300 underline"
      >
        Copy to clipboard
      </button>
    </div>
  );
};