import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Mic, Square, Play, Pause, Upload, AlertCircle } from 'lucide-react';

interface AudioRecorderProps {
  onAudioReady: (file: File) => void;
  isProcessing: boolean;
  disabled?: boolean;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onAudioReady,
  isProcessing,
  disabled = false,
}) => {
  const { t } = useTranslation();
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [uploadedName, setUploadedName] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Timer ticker
  useEffect(() => {
    if (isRecording && !isPaused) {
      timerRef.current = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording, isPaused]);

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainder = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remainder.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    setErrorMsg(null);
    setUploadedName(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone audio recording is not supported in this browser.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
        const audioFile = new File([audioBlob], `consultation_${Date.now()}.wav`, { type: 'audio/wav' });
        onAudioReady(audioFile);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start(250);
      setIsRecording(true);
      setIsPaused(false);
      setSeconds(0);
    } catch (err: any) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMsg('Microphone access was denied. Please allow microphone permissions in browser settings or use audio file upload.');
      } else {
        setErrorMsg(err.message || 'Unable to access microphone.');
      }
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
      } else {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setErrorMsg(null);
      setUploadedName(file.name);
      onAudioReady(file);
    }
  };

  return (
    <div className="bg-white border border-surface-border rounded-card p-4 sm:p-5 shadow-soft">
      {errorMsg && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-btn flex items-start gap-2.5 text-xs text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">Microphone Error</p>
            <p>{errorMsg}</p>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Left: Recording State & Waveform */}
        <div className="flex items-center gap-4 w-full sm:w-auto">
          {/* Animated Waveform Indicator */}
          <div className="flex items-center gap-1 h-8 px-2 bg-surface-alt rounded-lg border border-surface-border">
            {[6, 14, 22, 12, 28, 18, 10, 24, 16, 8].map((initialHeight, i) => (
              <span
                key={i}
                className={`w-1 rounded-full transition-all duration-300 ${
                  isRecording && !isPaused
                    ? 'bg-teal wave-bar'
                    : 'bg-slate/30'
                }`}
                style={{
                  height: isRecording && !isPaused ? undefined : `${initialHeight}px`,
                  animationDelay: `${i * 0.12}s`,
                }}
              />
            ))}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  isRecording
                    ? isPaused
                      ? 'bg-amber-400'
                      : 'bg-red-500 animate-pulse'
                    : 'bg-slate/40'
                }`}
              />
              <span className="text-sm font-bold text-navy">
                {isRecording
                  ? isPaused
                    ? t('app.recorder.paused')
                    : t('app.recorder.listening')
                  : uploadedName
                  ? 'Audio Loaded'
                  : 'Ambient Mic Ready'}
              </span>
            </div>
            <div className="text-xs font-mono text-slate">
              {isRecording ? formatTime(seconds) : uploadedName ? uploadedName : '00:00 (Idle)'}
            </div>
          </div>
        </div>

        {/* Right: Controls */}
        <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".wav,.mp3,.ogg,.webm,.m4a"
            className="hidden"
          />

          {!isRecording ? (
            <>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled || isProcessing}
                className="text-xs font-semibold text-slate hover:text-navy bg-surface-alt hover:bg-slate-100 border border-surface-border px-3.5 py-2 rounded-btn flex items-center gap-1.5 transition-colors disabled:opacity-50"
              >
                <Upload className="w-3.5 h-3.5 text-teal" />
                <span>{t('app.recorder.uploadAudio')}</span>
              </button>

              <button
                type="button"
                onClick={startRecording}
                disabled={disabled || isProcessing}
                className="bg-navy hover:bg-navy-800 disabled:opacity-50 text-white text-xs font-semibold px-4 py-2 rounded-btn flex items-center gap-1.5 shadow-soft transition-colors"
              >
                <Mic className="w-3.5 h-3.5 text-teal-300" />
                <span>{t('app.recorder.startRecording')}</span>
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={pauseRecording}
                className="text-xs font-semibold text-slate hover:text-navy bg-surface-alt border border-surface-border px-3 py-2 rounded-btn flex items-center gap-1"
              >
                {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
                <span>{isPaused ? t('app.recorder.resume') : t('app.recorder.pause')}</span>
              </button>

              <button
                type="button"
                onClick={stopRecording}
                className="bg-red-600 hover:bg-red-700 text-white text-xs font-semibold px-4 py-2 rounded-btn flex items-center gap-1.5 shadow-sm transition-colors"
              >
                <Square className="w-3 h-3 fill-current" />
                <span>{t('app.recorder.stop')}</span>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
