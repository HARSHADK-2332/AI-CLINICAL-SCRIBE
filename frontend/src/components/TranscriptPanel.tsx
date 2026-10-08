import React from 'react';
import { useTranslation } from 'react-i18next';
import { Stethoscope, User, Sparkles, MessageSquare, Loader2, PlayCircle, FileAudio } from 'lucide-react';
import type { TranscriptSegment } from '../services/api';

interface TranscriptPanelProps {
  segments: TranscriptSegment[];
  onGenerateNote: () => void;
  isGenerating: boolean;
  isTranscribing?: boolean;
  onLoadSample: () => void;
  onTranscribeSampleAudio?: (filename: string) => void;
}

export const TranscriptPanel: React.FC<TranscriptPanelProps> = ({
  segments,
  onGenerateNote,
  isGenerating,
  isTranscribing = false,
  onLoadSample,
  onTranscribeSampleAudio,
}) => {
  const { t } = useTranslation();

  const formatTimestamp = (start: number, end: number) => {
    const f = (val: number) => {
      const m = Math.floor(val / 60);
      const s = Math.floor(val % 60);
      return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };
    return `${f(start)} - ${f(end)}`;
  };

  return (
    <div className="bg-white border border-surface-border rounded-card flex flex-col h-[520px] shadow-soft">
      {/* Panel Header */}
      <div className="px-5 py-3.5 border-b border-surface-border flex items-center justify-between bg-surface-alt/60 rounded-t-card">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-teal" />
          <h3 className="text-sm font-bold text-navy">
            {t('app.liveConversation')}
          </h3>
          <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full font-semibold">
            {segments.length} {segments.length === 1 ? 'turn' : 'turns'}
          </span>
        </div>

        {segments.length > 0 && (
          <button
            onClick={() => onTranscribeSampleAudio && onTranscribeSampleAudio('test_audio.wav')}
            disabled={isTranscribing}
            className="text-[11px] text-teal hover:text-teal-700 font-semibold underline underline-offset-2 flex items-center gap-1 disabled:opacity-50"
          >
            <PlayCircle className="w-3.5 h-3.5" />
            <span>Re-run test audio</span>
          </button>
        )}
      </div>

      {/* Speaker Turns Feed */}
      <div
        className="flex-1 p-4 overflow-y-auto space-y-4 text-sm"
        aria-live="polite"
        aria-label="Conversation Transcript"
      >
        {isTranscribing ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate space-y-3">
            <Loader2 className="w-8 h-8 text-teal animate-spin" />
            <div>
              <p className="font-bold text-navy text-sm">Transcribing Audio with Whisper…</p>
              <p className="text-xs text-slate mt-1 max-w-xs">
                Running speech-to-text inference locally via PyTorch and FFmpeg.
              </p>
            </div>
          </div>
        ) : segments.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate">
            <div className="w-12 h-12 rounded-full bg-teal-50 border border-teal-200 flex items-center justify-center mb-3 text-teal">
              <FileAudio className="w-6 h-6" />
            </div>
            <p className="font-bold text-navy text-sm">Ready for Clinical Consultation</p>
            <p className="text-xs text-slate mt-1 max-w-xs">
              Record via your microphone above, upload an audio file, or click a test recording below to run real local Whisper transcription:
            </p>

            <div className="mt-4 flex flex-col gap-2 w-full max-w-xs">
              {onTranscribeSampleAudio && (
                <>
                  <button
                    onClick={() => onTranscribeSampleAudio('test_audio.wav')}
                    className="bg-navy hover:bg-navy-800 text-white text-xs font-semibold py-2 px-3 rounded-btn shadow-soft flex items-center justify-center gap-2 transition-all active:scale-[0.99]"
                  >
                    <PlayCircle className="w-3.5 h-3.5 text-teal-300" />
                    <span>Run Real Whisper on "test_audio.wav"</span>
                  </button>

                  <button
                    onClick={() => onTranscribeSampleAudio('multilingual_conversation.wav')}
                    className="bg-surface-alt hover:bg-slate-100 text-navy border border-surface-border text-xs font-semibold py-2 px-3 rounded-btn flex items-center justify-center gap-2 transition-colors"
                  >
                    <PlayCircle className="w-3.5 h-3.5 text-teal" />
                    <span>Run Real Whisper on "multilingual.wav"</span>
                  </button>
                </>
              )}

              <button
                onClick={onLoadSample}
                className="text-slate-subtle hover:text-navy text-[11px] underline underline-offset-2 mt-1"
              >
                Or preview with sample text dialogue
              </button>
            </div>
          </div>
        ) : (
          segments.map((seg, idx) => {
            const isDoc = seg.speaker === 'Doctor';
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-card border transition-all ${
                  isDoc
                    ? 'bg-navy-50/60 border-navy-100/80 mr-4'
                    : 'bg-teal-50/60 border-teal-100/80 ml-4'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        isDoc
                          ? 'bg-navy text-white'
                          : 'bg-teal text-white'
                      }`}
                    >
                      {isDoc ? <Stethoscope className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
                    </div>
                    <span className="font-bold text-xs text-navy tracking-tight">
                      {seg.speaker}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-subtle">
                    {formatTimestamp(seg.start, seg.end)}
                  </span>
                </div>
                <p className="text-slate-dark text-[13.5px] leading-relaxed pl-8">
                  {seg.text}
                </p>
              </div>
            );
          })
        )}
      </div>

      {/* Bottom Action */}
      <div className="p-3.5 border-t border-surface-border bg-white rounded-b-card">
        <button
          onClick={onGenerateNote}
          disabled={segments.length === 0 || isGenerating}
          className="w-full bg-navy hover:bg-navy-800 disabled:opacity-50 text-white font-semibold text-xs py-2.5 px-4 rounded-btn shadow-soft flex items-center justify-center gap-2 transition-all active:scale-[0.99]"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-teal" />
              <span>{t('app.recorder.generating')}</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-teal" />
              <span>{t('app.recorder.generateNote')}</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
