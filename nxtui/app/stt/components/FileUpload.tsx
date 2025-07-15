import { useRef } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onError: (error: string) => void;
  isConverting?: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, onError, isConverting }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check file type
      const allowedTypes = ['audio/wav', 'audio/flac', 'audio/aiff', 'audio/mp3', 'audio/mpeg'];
      if (!allowedTypes.includes(file.type)) {
        onError('Please select a valid audio file (WAV, FLAC, AIFF, MP3)');
        return;
      }
      
      // Check file size (16MB limit)
      if (file.size > 16 * 1024 * 1024) {
        onError('File size must be less than 16MB');
        return;
      }

      onFileSelect(file);
    }
  };

  const clearFile = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <label htmlFor="audioFile" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Upload Audio File
      </label>
      <input
        ref={fileInputRef}
        type="file"
        id="audioFile"
        accept="audio/*"
        onChange={handleFileSelect}
        disabled={isConverting}
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {isConverting ? 'Converting to WAV format...' : 'Supported formats: WAV, FLAC, AIFF, MP3 (Max size: 16MB)'}
      </p>
    </div>
  );
};