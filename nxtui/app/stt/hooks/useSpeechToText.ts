import { useState } from 'react';

export interface AudioToTextResponse {
  success: boolean;
  message: string;
  text?: string;
  language?: string;
  error?: string;
}

export const useSpeechToText = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string>('');
  const [error, setError] = useState<string>('');

  const convertAudioToText = async (audioFile: File, language: string) => {
    setIsLoading(true);
    setError('');
    setResult('');

    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('language', language);

      const response = await fetch('http://localhost:5000/audio-to-text', {
        method: 'POST',
        body: formData,
      });

      const data: AudioToTextResponse = await response.json();
      console.log('Response:', data);
      
      if (data.success && data.text) {
        setResult(data.text);
      } else {
        setError(data.error || data.message || 'Failed to convert audio to text');
      }
    } catch (err) {
      setError('Network error. Please make sure the backend server is running.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResult('');
    setError('');
  };

  return {
    isLoading,
    result,
    error,
    convertAudioToText,
    clearResults,
    setError
  };
};