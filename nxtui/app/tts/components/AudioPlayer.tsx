interface AudioPlayerProps {
  audioUrl: string;
  onDownload: () => void;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioUrl, onDownload }) => {
  if (!audioUrl) return null;

  return (
    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
      <h3 className="text-lg font-medium text-green-900 dark:text-green-400 mb-3">
        Generated Audio:
      </h3>
      
      <div className="bg-white dark:bg-gray-800 rounded-md p-4 border mb-3">
        <audio 
          controls 
          src={audioUrl}
          className="w-full"
          preload="metadata"
        >
          Your browser does not support the audio element.
        </audio>
      </div>
      
      <div className="flex gap-3">
        <button
          onClick={onDownload}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download MP3
        </button>
        
        <button
          onClick={() => {
            const audio = new Audio(audioUrl);
            audio.play();
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10v4a1 1 0 001 1h4a1 1 0 001-1v-4M9 10V9a1 1 0 011-1h4a1 1 0 011 1v1" />
          </svg>
          Play Audio
        </button>
      </div>
    </div>
  );
};