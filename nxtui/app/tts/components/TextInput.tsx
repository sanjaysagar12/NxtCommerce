interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  maxLength?: number;
  disabled?: boolean;
}

export const TextInput: React.FC<TextInputProps> = ({ 
  value, 
  onChange, 
  placeholder = "Enter text to convert to speech...",
  maxLength = 1000,
  disabled = false
}) => {
  return (
    <div>
      <label htmlFor="textInput" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Text to Convert
      </label>
      <textarea
        id="textInput"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        maxLength={maxLength}
        disabled={disabled}
        rows={6}
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <div className="flex justify-between items-center mt-1">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Enter the text you want to convert to speech
        </p>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {value.length}/{maxLength}
        </span>
      </div>
    </div>
  );
};