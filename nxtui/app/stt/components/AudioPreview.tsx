interface AudioPreviewProps {
  audioUrl: string;
  audioFile: File;
}

export const AudioPreview: React.FC<AudioPreviewProps> = ({ audioUrl, audioFile }) => {
  return (
    <>
      {/* Audio Preview */}
      {audioUrl && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Audio Preview
          </label>
          <audio 
            controls 
            src={audioUrl} 
            className="w-full"
            preload="metadata"
          />
        </div>
      )}

      {/* Selected File Info */}
      {audioFile && (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            <span className="font-medium">Selected file:</span> {audioFile.name}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Size: {(audioFile.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
      )}
    </>
  );
};