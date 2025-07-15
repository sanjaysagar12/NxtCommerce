import { useState } from 'react';

export interface TextToAudioResponse {
  success: boolean;
  message: string;
  audio_file_id?: string;
  audio_file_path?: string;
  error?: string;
}

export const useTextToSpeech = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [audioFileId, setAudioFileId] = useState<string>('');
  const [audioUrl, setAudioUrl] = useState<string>('');
  const [error, setError] = useState<string>('');

  const convertTextToAudio = async (text: string, language: string) => {
    setIsLoading(true);
    setError('');
    setAudioFileId('');
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

      const data: TextToAudioResponse = await response.json();
      console.log('Response:', data);
      
      if (data.success && data.audio_file_id) {
        setAudioFileId(data.audio_file_id);
        // Set the download URL for the audio file
        setAudioUrl(`http://localhost:5000/download-audio/${data.audio_file_id}`);
      } else {
        setError(data.error || data.message || 'Failed to convert text to audio');
      }
    } catch (err) {
      setError('Network error. Please make sure the backend server is running.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setAudioFileId('');
    setAudioUrl('');
    setError('');
  };

  const downloadAudio = () => {
    if (audioFileId) {
      const link = document.createElement('a');
      link.href = `http://localhost:5000/download-audio/${audioFileId}`;
      link.download = `${audioFileId}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return {
    isLoading,
    audioFileId,
    audioUrl,
    error,
    convertTextToAudio,
    clearResults,
    downloadAudio,
    setError
  };
};