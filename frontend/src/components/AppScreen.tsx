import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Stethoscope,
  PlusCircle,
  Users,
  FileText,
  Clock,
  Settings,
  User,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { AudioRecorder } from './AudioRecorder';
import { TranscriptPanel } from './TranscriptPanel';
import { ClinicalNotePanel } from './ClinicalNotePanel';
import {
  api,
  type TranscriptSegment,
  type ClinicalNote,
  type Patient,
  SAMPLE_TRANSCRIPT,
  SAMPLE_NOTE
} from '../services/api';

interface AppScreenProps {
  embedded?: boolean;
  onNavigateHome?: () => void;
}

export const AppScreen: React.FC<AppScreenProps> = ({
  embedded = false,
  onNavigateHome,
}) => {
  const { t, i18n } = useTranslation();

  // Patients state
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // Consultation state: mock sample shown only in embedded preview, empty in real app
  const [segments, setSegments] = useState<TranscriptSegment[]>(() => (embedded ? SAMPLE_TRANSCRIPT : []));
  const [note, setNote] = useState<ClinicalNote | null>(() => (embedded ? SAMPLE_NOTE : null));
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<'consultation' | 'patients' | 'notes'>('consultation');
  const [systemNotice, setSystemNotice] = useState<string | null>(null);

  // Load demo patients on mount
  useEffect(() => {
    api.getPatients().then((data) => {
      setPatients(data);
      if (data.length > 0) setSelectedPatient(data[0]);
    }).catch(() => {
      // fallback
    });
  }, []);

  const handleTranscribeSampleAudio = async (filename: string) => {
    setIsTranscribing(true);
    setSystemNotice(null);
    try {
      const res = await api.transcribeSampleAudio(filename, i18n.language);
      setSegments(res.segments);
      // Auto-trigger note generation on transcription completion
      handleGenerateNote(res.segments);
    } catch (err: any) {
      setSystemNotice(err.message || 'Audio transcription error.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleAudioReady = async (file: File) => {
    setIsTranscribing(true);
    setSystemNotice(null);
    try {
      const res = await api.transcribeAudio(file, i18n.language);
      setSegments(res.segments);
      // Auto-trigger note generation on audio completion
      handleGenerateNote(res.segments);
    } catch (err: any) {
      setSystemNotice(err.message || 'Audio transcription error.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleGenerateNote = async (transcriptSegments = segments) => {
    if (transcriptSegments.length === 0) return;
    setIsGenerating(true);
    setSystemNotice(null);
    try {
      const res = await api.generateNote(
        transcriptSegments,
        i18n.language,
        selectedPatient?.id
      );
      setNote(res);
    } catch (err: any) {
      setSystemNotice(err.message || 'Failed to generate clinical note.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUpdateNote = async (updated: Partial<ClinicalNote>) => {
    if (!note) return;
    try {
      const saved = await api.updateNote(note.id || 101, updated);
      setNote(saved);
    } catch {
      // Local optimistic update
      setNote((prev) => (prev ? { ...prev, ...updated } : null));
    }
  };

  const handleNewConsultation = () => {
    setSegments([]);
    setNote(null);
    setSystemNotice(null);
  };

  const handleLoadSample = () => {
    setSegments(SAMPLE_TRANSCRIPT);
    setNote(SAMPLE_NOTE);
  };

  return (
    <div className={`bg-[#F8FAFC] text-navy flex flex-col ${embedded ? 'h-full min-h-[640px]' : 'min-h-screen'}`}>
      {/* Top Application Bar */}
      <header className="bg-white border-b border-surface-border px-4 sm:px-6 h-16 flex items-center justify-between shadow-soft flex-shrink-0 z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={onNavigateHome}
            className="flex items-center gap-2 font-extrabold text-xl text-navy hover:opacity-90 transition-opacity"
            aria-label="ScribeCare Logo"
          >
            <div className="w-8 h-8 rounded-lg bg-navy flex items-center justify-center text-teal-100">
              <Stethoscope className="w-4 h-4" />
            </div>
            <span>ScribeCare</span>
          </button>
          <span className="hidden md:inline-block text-xs bg-teal-100 text-teal-800 font-semibold px-2.5 py-0.5 rounded-full">
            Clinical Suite
          </span>
        </div>

        {/* Right Avatar & Clinician Info */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 text-xs font-semibold text-slate-subtle border-r border-surface-border pr-4">
            <ShieldCheck className="w-4 h-4 text-teal" />
            <span>HIPAA Ready</span>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-full bg-navy text-teal-200 flex items-center justify-center font-bold text-xs ring-2 ring-teal-100">
              JD
            </div>
            <div className="hidden sm:block text-left leading-tight">
              <p className="text-xs font-bold text-navy">{t('app.clinician')}</p>
              <p className="text-[11px] text-slate">{t('app.specialty')}</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Layout Area: Left Sidebar + Center Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Navigation Sidebar */}
        <aside className="w-16 sm:w-56 bg-white border-r border-surface-border p-3 flex flex-col justify-between flex-shrink-0">
          <div className="space-y-1.5">
            <button
              onClick={handleNewConsultation}
              className="w-full bg-teal-100 hover:bg-teal-200 text-teal-800 font-bold text-xs px-3 py-2.5 rounded-btn flex items-center gap-2.5 transition-colors"
            >
              <PlusCircle className="w-4 h-4 text-teal flex-shrink-0" />
              <span className="hidden sm:inline">{t('app.newConsultation')}</span>
            </button>

            <button
              onClick={() => setActiveTab('consultation')}
              className={`w-full font-semibold text-xs px-3 py-2 rounded-btn flex items-center gap-2.5 transition-colors ${
                activeTab === 'consultation'
                  ? 'bg-navy-50 text-navy'
                  : 'text-slate hover:bg-surface-alt hover:text-navy'
              }`}
            >
              <FileText className="w-4 h-4 flex-shrink-0 text-teal" />
              <span className="hidden sm:inline">Active Scribe</span>
            </button>

            <button
              onClick={() => setActiveTab('patients')}
              className={`w-full font-semibold text-xs px-3 py-2 rounded-btn flex items-center gap-2.5 transition-colors ${
                activeTab === 'patients'
                  ? 'bg-navy-50 text-navy'
                  : 'text-slate hover:bg-surface-alt hover:text-navy'
              }`}
            >
              <Users className="w-4 h-4 flex-shrink-0" />
              <span className="hidden sm:inline">{t('app.patients')}</span>
            </button>

            <button
              onClick={() => setActiveTab('notes')}
              className={`w-full font-semibold text-xs px-3 py-2 rounded-btn flex items-center gap-2.5 transition-colors ${
                activeTab === 'notes'
                  ? 'bg-navy-50 text-navy'
                  : 'text-slate hover:bg-surface-alt hover:text-navy'
              }`}
            >
              <Clock className="w-4 h-4 flex-shrink-0" />
              <span className="hidden sm:inline">{t('app.history')}</span>
            </button>
          </div>

          <div className="pt-4 border-t border-surface-border">
            <button className="w-full text-slate hover:text-navy text-xs font-semibold px-3 py-2 rounded-btn flex items-center gap-2.5">
              <Settings className="w-4 h-4 flex-shrink-0" />
              <span className="hidden sm:inline">{t('app.settings')}</span>
            </button>
          </div>
        </aside>

        {/* Center Workspace */}
        <main className="flex-1 flex flex-col overflow-y-auto p-4 sm:p-6 space-y-4">
          {/* Patient Context Banner Header */}
          <div className="bg-white border border-surface-border rounded-card px-5 py-3.5 flex flex-wrap items-center justify-between gap-3 shadow-soft">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-surface-alt border border-surface-border flex items-center justify-center text-teal">
                <User className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-extrabold text-navy">
                    {selectedPatient
                      ? `${selectedPatient.name} (${selectedPatient.age}y, ${selectedPatient.gender})`
                      : 'Sarah Jenkins (42y, Female)'}
                  </span>
                  <span className="text-[11px] font-mono text-slate-subtle">
                    {selectedPatient?.medical_record_number || 'MRN-10492'}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate">
                  <span>{t('app.sessionTime')}</span>
                  <span>•</span>
                  <span>Exam Room 3</span>
                </div>
              </div>
            </div>

            {/* Select Patient Dropdown */}
            <div className="flex items-center gap-3">
              <select
                aria-label="Select Patient"
                value={selectedPatient?.id || 1}
                onChange={(e) => {
                  const p = patients.find((p) => p.id === Number(e.target.value));
                  if (p) setSelectedPatient(p);
                }}
                className="text-xs bg-surface-alt border border-surface-border rounded-btn px-2.5 py-1.5 font-medium text-slate hover:text-navy focus:bg-white"
              >
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.age}y {p.gender})
                  </option>
                ))}
              </select>

              <span className="bg-teal-100 text-teal-800 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-teal animate-pulse" />
                {t('app.inConsultation')}
              </span>
            </div>
          </div>

          {/* System Notice Alert */}
          {systemNotice && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-card flex items-start gap-2.5 text-xs text-amber-900">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-amber-600 mt-0.5" />
              <div className="flex-1">
                <span className="font-semibold">Notice: </span>
                <span>{systemNotice}</span>
              </div>
              <button onClick={() => setSystemNotice(null)} className="font-bold text-amber-900">×</button>
            </div>
          )}

          {/* Recorder Controls Bar */}
          <AudioRecorder
            onAudioReady={handleAudioReady}
            isProcessing={isTranscribing}
          />

          {/* Two-Pane Consultation Workspace: Transcript on Left, Clinical Note on Right */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            {/* Live Conversation Transcript Panel */}
            <TranscriptPanel
              segments={segments}
              onGenerateNote={() => handleGenerateNote(segments)}
              isGenerating={isGenerating}
              isTranscribing={isTranscribing}
              onLoadSample={handleLoadSample}
              onTranscribeSampleAudio={handleTranscribeSampleAudio}
            />

            {/* Generated Clinical Note Panel */}
            <ClinicalNotePanel
              note={note}
              onUpdateNote={handleUpdateNote}
              isLoading={isGenerating}
            />
          </div>
        </main>
      </div>
    </div>
  );
};
