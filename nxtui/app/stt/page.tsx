'use client';

import { useState } from 'react';
import { languages } from './constants/languages';
import { useSpeechToText } from './hooks/useSpeechToText';
import { useAudioConversion } from './hooks/useAudioConversion';
import { useAudioRecording } from './hooks/useAudioRecording';
import { LanguageSelect } from './components/LanguageSelect';
import { FileUpload } from './components/FileUpload';
import { AudioRecorder } from './components/AudioRecorder';
import { AudioPreview } from './components/AudioPreview';
import { ActionButtons } from './components/ActionButtons';
import { ErrorDisplay } from './components/ErrorDisplay';
import { ResultDisplay } from './components/ResultDisplay';

export default function SpeechToTextPage() {
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string>('');

  const { 
    isLoading, 
    result, 
    error, 
    convertAudioToText, 
    clearResults, 
    setError 
  } = useSpeechToText();

  const { 
    isConverting, 
    handleFileConversion 
  } = useAudioConversion();

  const {
    isRecording,
    recordingTime,
    formatTime,
    startRecording,
    stopRecording,
    resetRecording
  } = useAudioRecording();

  const handleFileSelect = (file: File) => {
    clearResults();
    setError('');
    
    handleFileConversion(file, {
      onSuccess: (convertedFile) => {
        setAudioFile(convertedFile);
        const url = URL.createObjectURL(convertedFile);
        setAudioUrl(url);
      },
      onError: (error) => {
        setError(error);
      }
    });
  };

  const handleStartRecording = () => {
    startRecording(
      (file) => {
        setAudioFile(file);
        const url = URL.createObjectURL(file);
        setAudioUrl(url);
      },
      (error) => {
        setError(error);
      }
    );
    clearResults();
    setError('');
  };

  const handleSubmit = () => {
    if (!audioFile) {
      setError('Please select an audio file');
      return;
    }
    convertAudioToText(audioFile, selectedLanguage);
  };

  const handleClear = () => {
    setAudioFile(null);
    setAudioUrl('');
    clearResults();
    setError('');
    resetRecording();
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">
          Speech to Text Converter
        </h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="space-y-6">
            <LanguageSelect 
              value={selectedLanguage}
              onChange={setSelectedLanguage}
              languages={languages}
            />

            <FileUpload
              onFileSelect={handleFileSelect}
              onError={setError}
              isConverting={isConverting}
            />

            {/* OR Divider */}
            <div className="flex items-center justify-center">
              <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
              <span className="px-4 text-sm text-gray-500 dark:text-gray-400">OR</span>
              <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
            </div>

            <AudioRecorder
              isRecording={isRecording}
              recordingTime={recordingTime}
              formatTime={formatTime}
              onStartRecording={handleStartRecording}
              onStopRecording={stopRecording}
            />

            <AudioPreview audioUrl={audioUrl} audioFile={audioFile!} />

            <ActionButtons
              onSubmit={handleSubmit}
              onClear={handleClear}
              isLoading={isLoading}
              hasAudioFile={!!audioFile}
            />
          </div>
        </div>

        <ErrorDisplay error={error} />
        <ResultDisplay result={result} />
      </div>
    </div>
  );
}