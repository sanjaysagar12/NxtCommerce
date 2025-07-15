import { useState } from 'react';

export interface TranslateResponse {
  success: boolean;
  message: string;
  translated_text?: string;
  source_language?: string;
  target_language?: string;
  error?: string;
}

export interface DetectLanguageResponse {
  success: boolean;
  message: string;
  detected_language?: string;
  error?: string;
}

export const useTranslator = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [translatedText, setTranslatedText] = useState<string>('');
  const [detectedLanguage, setDetectedLanguage] = useState<string>('');
  const [error, setError] = useState<string>('');

  const translateText = async (text: string, targetLanguage: string, sourceLanguage: string = 'auto') => {
    setIsLoading(true);
    setError('');
    setTranslatedText('');

    try {
      const response = await fetch('http://localhost:5000/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          target_language: targetLanguage,
          source_language: sourceLanguage
        }),
      });

      const data: TranslateResponse = await response.json();
      console.log('Translation Response:', data);
      
      if (data.success && data.translated_text) {
        setTranslatedText(data.translated_text);
        if (data.source_language) {
          setDetectedLanguage(data.source_language);
        }
      } else {
        setError(data.error || data.message || 'Failed to translate text');
      }
    } catch (err) {
      setError('Network error. Please make sure the backend server is running.');
      console.error('Translation Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const detectLanguage = async (text: string) => {
    setIsDetecting(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/detect-language', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      const data: DetectLanguageResponse = await response.json();
      console.log('Detection Response:', data);
      
      if (data.success && data.detected_language) {
        setDetectedLanguage(data.detected_language);
        return data.detected_language;
      } else {
        setError(data.error || data.message || 'Failed to detect language');
        return null;
      }
    } catch (err) {
      setError('Network error. Please make sure the backend server is running.');
      console.error('Detection Error:', err);
      return null;
    } finally {
      setIsDetecting(false);
    }
  };

  const clearResults = () => {
    setTranslatedText('');
    setDetectedLanguage('');
    setError('');
  };

  const swapLanguages = (sourceLanguage: string, targetLanguage: string, sourceText: string) => {
    // Return swapped values for the parent component to handle
    return {
      newSourceLanguage: targetLanguage,
      newTargetLanguage: sourceLanguage,
      newSourceText: translatedText,
      newTargetText: sourceText
    };
  };

  return {
    isLoading,
    isDetecting,
    translatedText,
    detectedLanguage,
    error,
    translateText,
    detectLanguage,
    clearResults,
    swapLanguages,
    setError
  };
};