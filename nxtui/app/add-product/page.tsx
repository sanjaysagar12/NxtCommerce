"use client";

import { useState, useRef, useEffect } from "react";
import { 
  PlusCircleIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon, 
  SparklesIcon,
  DocumentDuplicateIcon,
  EyeIcon,
  MicrophoneIcon,
  SpeakerWaveIcon,
  StopIcon,
  PlayIcon,
  PauseIcon
} from "@heroicons/react/24/outline";

// Custom hooks for speech functionality
const useSpeechToText = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const convertAudioToText = async (audioFile: File, language: string = 'en-US') => {
    setIsLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('language', language);

      const response = await fetch('http://localhost:5000/audio-to-text', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.success && data.text) {
        return data.text;
      } else {
        setError(data.error || data.message || 'Failed to convert audio to text');
        return null;
      }
    } catch (err) {
      setError('Network error. Please make sure the backend server is running.');
      console.error('Error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    convertAudioToText,
    setError
  };
};

const useAudioRecording = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async (onSuccess: (file: File) => void, onError: (error: string) => void) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create MediaRecorder with high quality settings
      let mediaRecorder;
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      } else {
        mediaRecorder = new MediaRecorder(stream);
      }
      
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };
      
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: mediaRecorder.mimeType });
        
        try {
          // Convert to WAV format for better compatibility
          const wavFile = await convertToWav(blob);
          onSuccess(wavFile);
        } catch (error) {
          console.error('Error converting recording:', error);
          onError('Failed to process recording. Please try again.');
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      onError('Error accessing microphone. Please ensure microphone permissions are granted.');
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  const resetRecording = () => {
    setRecordingTime(0);
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
    }
  };

  // Convert audio blob to WAV format
  const convertToWav = async (audioBlob: Blob): Promise<File> => {
    return new Promise((resolve, reject) => {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const fileReader = new FileReader();
      
      fileReader.onload = async (e) => {
        try {
          const arrayBuffer = e.target?.result as ArrayBuffer;
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          
          // Convert to WAV format
          const wavBuffer = audioBufferToWav(audioBuffer);
          const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });
          const wavFile = new File([wavBlob], 'recording.wav', { type: 'audio/wav' });
          
          resolve(wavFile);
        } catch (error) {
          reject(error);
        }
      };
      
      fileReader.onerror = () => reject(new Error('Failed to read file'));
      fileReader.readAsArrayBuffer(audioBlob);
    });
  };

  const audioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
    const length = buffer.length;
    const numberOfChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const bytesPerSample = 2;
    const blockAlign = numberOfChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = length * blockAlign;
    const bufferSize = 44 + dataSize;
    
    const arrayBuffer = new ArrayBuffer(bufferSize);
    const view = new DataView(arrayBuffer);
    
    // WAV header
    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, bufferSize - 8, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, dataSize, true);
    
    // Write audio data
    let offset = 44;
    for (let i = 0; i < length; i++) {
      for (let channel = 0; channel < numberOfChannels; channel++) {
        const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
        view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        offset += 2;
      }
    }
    
    return arrayBuffer;
  };

  return {
    isRecording,
    recordingTime,
    formatTime,
    startRecording,
    stopRecording,
    resetRecording
  };
};

const useTextToSpeech = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');
  const [error, setError] = useState('');

  const convertTextToAudio = async (text: string, language: string = 'en-US') => {
    setIsLoading(true);
    setError('');
    setAudioUrl('');

    try {
      const response = await fetch('http://localhost:5000/text-to-audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          language
        }),
      });

      const data = await response.json();
      
      if (data.success && data.audio_file_id) {
        const audioFileUrl = `http://localhost:5000/download-audio/${data.audio_file_id}`;
        setAudioUrl(audioFileUrl);
        return audioFileUrl;
      } else {
        setError(data.error || data.message || 'Failed to convert text to audio');
        return null;
      }
    } catch (err) {
      setError('Network error. Please make sure the backend server is running.');
      console.error('Error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    audioUrl,
    error,
    convertTextToAudio,
    setError
  };
};

export default function AddProductPage() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showJson, setShowJson] = useState(false);
  
  // Use custom hooks for speech functionality
  const speechToText = useSpeechToText();
  const audioRecording = useAudioRecording();
  const textToSpeech = useTextToSpeech();
  
  // Additional states for audio playback
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleAddProduct = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError("");
    setResult(null);
    if (!prompt.trim()) {
      setError("Please enter a product description.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/add-product", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: prompt }),
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.message || "Failed to add product.");
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  // Handle speech to text recording
  const handleStartRecording = () => {
    audioRecording.startRecording(
      async (audioFile: File) => {
        const text = await speechToText.convertAudioToText(audioFile);
        if (text) {
          setPrompt(prev => prev + (prev ? ' ' : '') + text);
        }
      },
      (error: string) => {
        speechToText.setError(error);
      }
    );
  };

  // Handle text to speech
  const handleTextToSpeech = async () => {
    if (!prompt.trim()) return;
    
    const audioUrl = await textToSpeech.convertTextToAudio(prompt);
    if (audioUrl) {
      // Play the audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => {
        setIsPlaying(false);
        textToSpeech.setError('Failed to play audio');
      };
      
      audio.play();
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const examplePrompts = [
    "Add a red cotton kurta for women priced at ₹999 with 20% discount, available in sizes S and M. 10 in stock. Category: Ethnic Wear. Fabric: Cotton. Sleeve: 3/4th.",
    "Add a blue denim jacket for men priced at ₹1499 with 15% discount, available in sizes M, L, XL. 25 in stock. Category: Casual Wear. Fabric: Denim.",
    "Add a black silk saree for women priced at ₹2499 with 10% discount, available in one size. 15 in stock. Category: Traditional Wear. Fabric: Silk.",
    "Add a white cotton t-shirt for men priced at ₹599 with 25% discount, available in sizes S, M, L, XL. 50 in stock. Category: Casual Wear. Fabric: Cotton."
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-sm border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                Add New Product
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Create products with natural language descriptions
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                <SparklesIcon className="h-4 w-4" />
                <span>AI-Powered</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Input Form */}
          <div className="space-y-6">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-xl">
                  <PlusCircleIcon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Product Description</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Describe your product in natural language</p>
                </div>
              </div>

              <form onSubmit={handleAddProduct} className="space-y-4">
                <div className="relative">
                  <textarea
                    className="w-full px-4 py-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none transition-all duration-200 shadow-sm"
                    placeholder="Describe the product you want to add... (e.g., 'Add a red cotton kurta for women priced at ₹999 with 20% discount, available in sizes S and M. 10 in stock. Category: Ethnic Wear. Fabric: Cotton. Sleeve: 3/4th.')"
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    disabled={loading}
                    rows={8}
                  />
                  <div className="absolute bottom-3 right-3 flex items-center space-x-2">
                    <span className="text-xs text-gray-400">{prompt.length}/1000</span>
                    {/* Speech to Text Button */}
                    <button
                      type="button"
                      onClick={audioRecording.isRecording ? audioRecording.stopRecording : handleStartRecording}
                      className={`p-2 rounded-lg transition-all duration-200 ${
                        audioRecording.isRecording 
                          ? 'bg-red-500 text-white hover:bg-red-600' 
                          : 'bg-blue-500 text-white hover:bg-blue-600'
                      }`}
                      title={audioRecording.isRecording ? "Stop Recording" : "Start Recording"}
                      disabled={speechToText.isLoading}
                    >
                      {audioRecording.isRecording ? (
                        <StopIcon className="h-4 w-4" />
                      ) : (
                        <MicrophoneIcon className="h-4 w-4" />
                      )}
                    </button>
                    {/* Text to Speech Button */}
                    <button
                      type="button"
                      onClick={handleTextToSpeech}
                      disabled={!prompt.trim() || isPlaying || textToSpeech.isLoading}
                      className="p-2 rounded-lg bg-green-500 text-white hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                      title="Read Text Aloud"
                    >
                      {textToSpeech.isLoading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      ) : (
                        <SpeakerWaveIcon className="h-4 w-4" />
                      )}
                    </button>
                    {/* Stop Audio Button */}
                    {isPlaying && (
                      <button
                        type="button"
                        onClick={stopAudio}
                        className="p-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-all duration-200"
                        title="Stop Audio"
                      >
                        <StopIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Speech Status Indicators */}
                {audioRecording.isRecording && (
                  <div className="flex items-center space-x-2 text-sm text-red-600 dark:text-red-400">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span>Recording... {audioRecording.formatTime(audioRecording.recordingTime)}</span>
                  </div>
                )}

                {speechToText.isLoading && (
                  <div className="flex items-center space-x-2 text-sm text-blue-600 dark:text-blue-400">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                    <span>Converting speech to text...</span>
                  </div>
                )}

                {isPlaying && (
                  <div className="flex items-center space-x-2 text-sm text-green-600 dark:text-green-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span>Playing audio...</span>
                  </div>
                )}

                {textToSpeech.isLoading && (
                  <div className="flex items-center space-x-2 text-sm text-yellow-600 dark:text-yellow-400">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-yellow-500 border-t-transparent"></div>
                    <span>Converting text to speech...</span>
                  </div>
                )}

                {/* Speech Errors */}
                {speechToText.error && (
                  <div className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded-lg">
                    {speechToText.error}
                  </div>
                )}

                {textToSpeech.error && (
                  <div className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded-lg">
                    {textToSpeech.error}
                  </div>
                )}
                
                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-8 py-3 bg-gradient-to-r from-emerald-600 to-blue-600 text-white font-semibold rounded-xl hover:from-emerald-700 hover:to-blue-700 transition-all duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        <span>Adding Product...</span>
                      </>
                    ) : (
                      <>
                        <PlusCircleIcon className="h-5 w-5" />
                        <span>Add Product</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* Example Prompts */}
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <SparklesIcon className="h-5 w-5 mr-2 text-emerald-600" />
                Example Prompts
              </h3>
              <div className="space-y-3">
                {examplePrompts.map((example, index) => (
                  <div 
                    key={index}
                    className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-pointer"
                    onClick={() => setPrompt(example)}
                  >
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                      {example}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 backdrop-blur-sm border border-red-200 dark:border-red-800 rounded-2xl p-6 shadow-lg">
                <div className="flex items-center space-x-3">
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-500 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-red-900 dark:text-red-400">Error</h3>
                    <p className="text-red-700 dark:text-red-300 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Success Result */}
            {result && (
              <div className="bg-green-50 dark:bg-green-900/20 backdrop-blur-sm border border-green-200 dark:border-green-800 rounded-2xl shadow-lg overflow-hidden">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                      <div>
                        <h3 className="text-lg font-semibold text-green-900 dark:text-green-400">
                          Product Added Successfully!
                        </h3>
                        <p className="text-green-700 dark:text-green-300 text-sm mt-1">
                          {result.message}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowJson(!showJson)}
                      className="p-2 text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300 transition-colors"
                      title={showJson ? "Hide JSON" : "Show JSON"}
                    >
                      <EyeIcon className="h-5 w-5" />
                    </button>
                  </div>

                  {/* Product Preview */}
                  {result.product_json && (
                    <div className="bg-white/60 dark:bg-gray-800/60 rounded-xl p-4 border border-green-200 dark:border-green-700 mb-4">
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Product Preview</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Name:</span>
                          <span className="font-medium text-gray-900 dark:text-white">{result.product_json.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Price:</span>
                          <span className="font-medium text-gray-900 dark:text-white">₹{result.product_json.price}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Discount:</span>
                          <span className="font-medium text-green-600 dark:text-green-400">{result.product_json.discount}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Stock:</span>
                          <span className="font-medium text-gray-900 dark:text-white">{result.product_json.stock}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">SKU:</span>
                          <span className="font-medium text-gray-900 dark:text-white">{result.product_json.sku}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* JSON Display */}
                  {showJson && result.product_json && (
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-green-900 dark:text-green-400">Generated JSON</h4>
                        <button
                          onClick={() => copyToClipboard(JSON.stringify(result.product_json, null, 2))}
                          className="flex items-center space-x-1 text-xs text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300 transition-colors"
                        >
                          <DocumentDuplicateIcon className="h-4 w-4" />
                          <span>Copy</span>
                        </button>
                      </div>
                      <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-96">
                        <pre className="text-xs text-green-400 whitespace-pre-wrap">
                          {JSON.stringify(result.product_json, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tips Card */}
            <div className="bg-blue-50 dark:bg-blue-900/20 backdrop-blur-sm border border-blue-200 dark:border-blue-800 rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-400 mb-4 flex items-center">
                <SparklesIcon className="h-5 w-5 mr-2" />
                Tips for Better Results
              </h3>
              <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-300">
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Include specific details like color, material, size, and price</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Mention stock quantity and discount percentage if applicable</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Specify the target audience (men, women, kids)</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                  <span>Add category information for better organization</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
