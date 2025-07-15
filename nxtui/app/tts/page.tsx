'use client';

import { useState } from 'react';
import { ttsLanguages } from './constants/languages';
import { useTextToSpeech } from './hooks/useTextToSpeech';
import { LanguageSelect } from './components/LanguageSelect';
import { TextInput } from './components/TextInput';
import { AudioPlayer } from './components/AudioPlayer';
import { ActionButtons } from './components/ActionButtons';
import { ErrorDisplay } from './components/ErrorDisplay';

export default function TextToSpeechPage() {
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [inputText, setInputText] = useState('');

  const { 
    isLoading, 
    audioUrl, 
    error, 
    convertTextToAudio, 
    clearResults, 
    downloadAudio,
    setError 
  } = useTextToSpeech();

  const handleGenerate = () => {
    if (!inputText.trim()) {
      setError('Please enter some text to convert to speech');
      return;
    }
    convertTextToAudio(inputText.trim(), selectedLanguage);
  };

  const handleClear = () => {
    setInputText('');
    clearResults();
  };

  const sampleTexts = [
    { lang: 'en', text: 'Hello! This is a sample text for text-to-speech conversion.' },
    { lang: 'es', text: '¡Hola! Este es un texto de muestra para la conversión de texto a voz.' },
    { lang: 'fr', text: 'Bonjour! Ceci est un exemple de texte pour la conversion texte-parole.' },
    { lang: 'de', text: 'Hallo! Dies ist ein Beispieltext für die Text-zu-Sprache-Konvertierung.' },
    { lang: 'it', text: 'Ciao! Questo è un testo di esempio per la conversione da testo a voce.' },
  ];

  const handleSampleText = () => {
    const sample = sampleTexts.find(s => s.lang === selectedLanguage) || sampleTexts[0];
    setInputText(sample.text);
    clearResults();
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">
          Text to Speech Converter
        </h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="space-y-6">
            <LanguageSelect 
              value={selectedLanguage}
              onChange={setSelectedLanguage}
              languages={ttsLanguages}
            />

            <TextInput
              value={inputText}
              onChange={setInputText}
              disabled={isLoading}
              maxLength={1000}
            />

            {/* Sample Text Button */}
            <div className="flex justify-center">
              <button
                type="button"
                onClick={handleSampleText}
                disabled={isLoading}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Use Sample Text
              </button>
            </div>

            <ActionButtons
              onGenerate={handleGenerate}
              onClear={handleClear}
              isLoading={isLoading}
              hasText={inputText.trim().length > 0}
            />
          </div>
        </div>

        <ErrorDisplay error={error} />
        
        <AudioPlayer 
          audioUrl={audioUrl}
          onDownload={downloadAudio}
        />

        {/* Instructions */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
          <h3 className="text-lg font-medium text-blue-900 dark:text-blue-400 mb-2">
            How to Use:
          </h3>
          <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
            <li>• Select your preferred language from the dropdown</li>
            <li>• Enter or paste the text you want to convert to speech</li>
            <li>• Click "Generate Audio" to create the audio file</li>
            <li>• Play the generated audio directly in your browser</li>
            <li>• Download the MP3 file to save it locally</li>
            <li>• Use "Sample Text" to try different languages</li>
          </ul>
        </div>

        {/* Features */}
        <div className="mt-4 bg-gray-50 dark:bg-gray-800 rounded-md p-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Features:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700 dark:text-gray-300">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Multiple Languages
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              High Quality Audio
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Instant Playback
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              MP3 Download
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}