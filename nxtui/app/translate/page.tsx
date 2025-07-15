'use client';

import { useState } from 'react';
import { translateLanguages, targetLanguages } from './constants/languages';
import { useTranslator } from './hooks/useTranslator';
import { LanguageSelector } from './components/LanguageSelector';
import { TranslationPanel } from './components/TranslationPanel';
import { ActionButtons } from './components/ActionButtons';
import { ErrorDisplay } from './components/ErrorDisplay';

export default function TranslatePage() {
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [sourceText, setSourceText] = useState('');

  const { 
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
  } = useTranslator();

  const handleTranslate = () => {
    if (!sourceText.trim()) {
      setError('Please enter some text to translate');
      return;
    }
    translateText(sourceText.trim(), targetLanguage, sourceLanguage);
  };

  const handleClear = () => {
    setSourceText('');
    clearResults();
  };

  const handleClearSource = () => {
    setSourceText('');
    setError('');
  };

  const handleDetectLanguage = () => {
    if (!sourceText.trim()) {
      setError('Please enter some text to detect language');
      return;
    }
    detectLanguage(sourceText.trim());
  };

  const handleSwapLanguages = () => {
    if (sourceLanguage === 'auto') return;
    
    const swapped = swapLanguages(sourceLanguage, targetLanguage, sourceText);
    setSourceLanguage(swapped.newSourceLanguage);
    setTargetLanguage(swapped.newTargetLanguage);
    setSourceText(swapped.newSourceText);
  };

  const handleCopyTranslation = () => {
    if (translatedText) {
      navigator.clipboard.writeText(translatedText);
    }
  };

  const sampleTexts = [
    { lang: 'en', text: 'Hello, how are you today? I hope you are doing well.' },
    { lang: 'es', text: 'Hola, ¿cómo estás hoy? Espero que estés bien.' },
    { lang: 'fr', text: 'Bonjour, comment allez-vous aujourd\'hui? J\'espère que vous allez bien.' },
    { lang: 'de', text: 'Hallo, wie geht es dir heute? Ich hoffe, es geht dir gut.' },
    { lang: 'it', text: 'Ciao, come stai oggi? Spero che tu stia bene.' },
    { lang: 'pt', text: 'Olá, como você está hoje? Espero que você esteja bem.' },
    { lang: 'ja', text: 'こんにちは、今日はお元気ですか？お元気であることを願っています。' },
    { lang: 'ko', text: '안녕하세요, 오늘 어떻게 지내세요? 잘 지내고 계시길 바랍니다.' },
    { lang: 'zh', text: '你好，你今天好吗？我希望你一切都好。' },
    { lang: 'hi', text: 'नमस्ते, आज आप कैसे हैं? मुझे उम्मीद है कि आप अच्छा कर रहे हैं।' },
    { lang: 'ar', text: 'مرحبا، كيف حالك اليوم؟ أتمنى أن تكون بخير.' },
    { lang: 'ru', text: 'Привет, как дела сегодня? Надеюсь, у тебя все хорошо.' },
  ];

  const handleSampleText = () => {
    const sample = sampleTexts[Math.floor(Math.random() * sampleTexts.length)];
    setSourceText(sample.text);
    setSourceLanguage('auto');
    clearResults();
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">
          Language Translator
        </h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="space-y-6">
            <LanguageSelector
              sourceLanguage={sourceLanguage}
              targetLanguage={targetLanguage}
              onSourceLanguageChange={setSourceLanguage}
              onTargetLanguageChange={setTargetLanguage}
              onSwapLanguages={handleSwapLanguages}
              sourceLanguages={translateLanguages}
              targetLanguages={targetLanguages}
              detectedLanguage={detectedLanguage}
            />

            <TranslationPanel
              sourceText={sourceText}
              translatedText={translatedText}
              onSourceTextChange={setSourceText}
              onClearSource={handleClearSource}
              onCopyTranslation={handleCopyTranslation}
              onDetectLanguage={handleDetectLanguage}
              isLoading={isLoading}
              isDetecting={isDetecting}
              maxLength={5000}
            />

            <div className="flex justify-center gap-4">
              <ActionButtons
                onTranslate={handleTranslate}
                onClear={handleClear}
                isLoading={isLoading}
                hasText={sourceText.trim().length > 0}
              />
              
              <button
                type="button"
                onClick={handleSampleText}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Random Sample
              </button>
            </div>
          </div>
        </div>

        <ErrorDisplay error={error} />

        {/* Instructions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
            <h3 className="text-lg font-medium text-blue-900 dark:text-blue-400 mb-2">
              How to Use:
            </h3>
            <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
              <li>• Select source and target languages</li>
              <li>• Enter text in the left panel</li>
              <li>• Use "Auto-detect" to automatically detect source language</li>
              <li>• Click "Translate" to get translation</li>
              <li>• Use swap button to reverse languages</li>
              <li>• Click "Detect Language" to identify source language</li>
            </ul>
          </div>

          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
            <h3 className="text-lg font-medium text-green-900 dark:text-green-400 mb-2">
              Features:
            </h3>
            <div className="text-sm text-green-800 dark:text-green-300 space-y-1">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                70+ Languages Supported
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Auto Language Detection
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Instant Translation
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Copy Translation
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Language Swap
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}