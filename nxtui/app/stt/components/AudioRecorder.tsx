interface AudioRecorderProps {
  isRecording: boolean;
  recordingTime: number;
  formatTime: (seconds: number) => string;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  isRecording,
  recordingTime,
  formatTime,
  onStartRecording,
  onStopRecording
}) => {
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Record Audio
      </label>
      
      {/* Recording Controls */}
      <div className="flex items-center gap-4">
        {!isRecording ? (
          <button
            type="button"
            onClick={onStartRecording}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
            Start Recording
          </button>
        ) : (
          <button
            type="button"
            onClick={onStopRecording}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
            </svg>
            Stop Recording
          </button>
        )}
        
        {isRecording && (
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Recording: {formatTime(recordingTime)}
            </span>
          </div>
        )}
      </div>
      
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Click "Start Recording" to capture audio from your microphone
      </p>
    </div>
  );
};