import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FileText,
  Copy,
  Check,
  Download,
  CheckCircle2,
  AlertTriangle,
  Edit3,
  Info,
  ChevronDown
} from 'lucide-react';
import { type ClinicalNote, api } from '../services/api';

interface ClinicalNotePanelProps {
  note: ClinicalNote | null;
  onUpdateNote: (updated: Partial<ClinicalNote>) => void;
  isLoading: boolean;
}

export const ClinicalNotePanel: React.FC<ClinicalNotePanelProps> = ({
  note,
  onUpdateNote,
  isLoading,
}) => {
  const { t, i18n } = useTranslation();
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Editable local state
  const [draftCC, setDraftCC] = useState('');
  const [draftHPI, setDraftHPI] = useState('');
  const [draftAssessment, setDraftAssessment] = useState('');
  const [draftPlan, setDraftPlan] = useState<string[]>([]);

  // Synchronize local edit state when note arrives or changes
  React.useEffect(() => {
    if (note) {
      setDraftCC(note.chief_complaint);
      setDraftHPI(note.history_of_present_illness);
      setDraftAssessment(note.assessment);
      setDraftPlan(note.plan || []);
    }
  }, [note]);

  if (isLoading) {
    return (
      <div className="bg-white border border-surface-border rounded-card p-6 h-[520px] flex flex-col justify-between shadow-soft animate-pulse">
        <div className="space-y-4">
          <div className="h-6 bg-slate/10 rounded w-1/3"></div>
          <div className="h-4 bg-slate/10 rounded w-1/2"></div>
          <div className="space-y-2 pt-4">
            <div className="h-4 bg-slate/10 rounded w-full"></div>
            <div className="h-4 bg-slate/10 rounded w-5/6"></div>
            <div className="h-4 bg-slate/10 rounded w-4/6"></div>
          </div>
          <div className="space-y-2 pt-4">
            <div className="h-4 bg-slate/10 rounded w-3/4"></div>
            <div className="h-4 bg-slate/10 rounded w-2/3"></div>
          </div>
        </div>
        <div className="h-10 bg-slate/10 rounded"></div>
      </div>
    );
  }

  if (!note) {
    return (
      <div className="bg-white border border-surface-border rounded-card h-[520px] flex flex-col items-center justify-center p-8 text-center shadow-soft">
        <div className="w-14 h-14 rounded-full bg-surface-alt border border-surface-border flex items-center justify-center text-slate-subtle mb-4">
          <FileText className="w-7 h-7" />
        </div>
        <h3 className="text-base font-bold text-navy">No Clinical Note Yet</h3>
        <p className="text-xs text-slate mt-1.5 max-w-sm">
          Run or load a consultation conversation and click "Generate Clinical Note" to extract structured SOAP documentation.
        </p>
      </div>
    );
  }

  const isReviewed = note.status === 'reviewed';

  const handleSaveEdits = () => {
    onUpdateNote({
      chief_complaint: draftCC,
      history_of_present_illness: draftHPI,
      assessment: draftAssessment,
      plan: draftPlan,
    });
    setIsEditing(false);
  };

  const handleCopy = () => {
    const text = `CLINICAL NOTE
Status: ${note.status.toUpperCase()}
Chief Complaint: ${note.chief_complaint}
History of Present Illness: ${note.history_of_present_illness}
Assessment: ${note.assessment}
Plan:
${note.plan.map((p) => `- ${p}`).join('\n')}
${note.negated_findings?.length ? `Pertinent Negatives: ${note.negated_findings.join(', ')}` : ''}
`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExport = async (format: 'txt' | 'json' | 'soap' | 'fhir') => {
    setExportError(null);
    setExportOpen(false);
    try {
      if (!note.id) throw new Error('Note must have an ID to export.');
      const res = await api.exportNote(note.id, format);
      const url = window.URL.createObjectURL(res.blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = res.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setExportError(err.message || 'Export failed.');
    }
  };

  const toggleApproval = () => {
    const newStatus = isReviewed ? 'draft' : 'reviewed';
    onUpdateNote({ status: newStatus });
  };

  return (
    <div className="bg-white border border-surface-border rounded-card flex flex-col h-[520px] shadow-soft">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-surface-border flex items-center justify-between bg-surface-alt/60 rounded-t-card">
        <div className="flex items-center gap-2.5">
          <FileText className="w-4 h-4 text-teal" />
          <h3 className="text-sm font-bold text-navy">Generated Clinical Note</h3>
          <span
            className={`text-xs px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1 ${
              isReviewed
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-teal-100 text-teal-800'
            }`}
          >
            {isReviewed ? <CheckCircle2 className="w-3 h-3" /> : null}
            {isReviewed ? t('app.note.reviewed') : t('app.note.draftReady')}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {isEditing ? (
            <button
              onClick={handleSaveEdits}
              className="text-xs bg-navy text-white px-3 py-1 rounded-btn font-semibold hover:bg-navy-800 transition-colors"
            >
              {t('app.note.done')}
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="text-xs text-slate hover:text-navy border border-surface-border px-2.5 py-1 rounded-btn font-medium bg-white transition-colors flex items-center gap-1"
            >
              <Edit3 className="w-3 h-3 text-teal" />
              <span>{t('app.note.edit')}</span>
            </button>
          )}
        </div>
      </div>

      {/* Notice Banners */}
      <div className="px-5 pt-3 space-y-2">
        {/* Clinician Review Warning */}
        <div className="bg-amber-50/80 border border-amber-200/80 rounded-lg p-2.5 flex items-center gap-2 text-xs text-amber-900">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
          <span>{t('app.note.reviewNotice')}</span>
        </div>

        {/* Multilingual English synthesis banner if Hindi or Telugu is selected */}
        {i18n.language !== 'en' && (
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-2 flex items-center gap-2 text-xs text-teal-900">
            <Info className="w-3.5 h-3.5 text-teal flex-shrink-0" />
            <span>{t('app.note.languageNotice')}</span>
          </div>
        )}

        {/* Export Error Alert */}
        {exportError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-2 text-xs text-red-700 flex items-center justify-between">
            <span>{exportError}</span>
            <button onClick={() => setExportError(null)} className="text-red-900 font-bold ml-2">×</button>
          </div>
        )}
      </div>

      {/* Note Sections Body */}
      <div className="flex-1 p-5 overflow-y-auto space-y-5 text-sm">
        {/* Chief Complaint */}
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-teal block mb-1">
            {t('app.note.chiefComplaint')}
          </label>
          {isEditing ? (
            <input
              type="text"
              value={draftCC}
              onChange={(e) => setDraftCC(e.target.value)}
              className="w-full text-sm font-semibold text-navy bg-surface-alt border border-surface-border rounded-btn p-2 focus:bg-white"
            />
          ) : (
            <p className="font-semibold text-navy text-[14px]">
              {note.chief_complaint || 'Not documented'}
            </p>
          )}
        </div>

        {/* History of Present Illness */}
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-teal block mb-1">
            {t('app.note.hpi')}
          </label>
          {isEditing ? (
            <textarea
              rows={3}
              value={draftHPI}
              onChange={(e) => setDraftHPI(e.target.value)}
              className="w-full text-sm text-slate-dark bg-surface-alt border border-surface-border rounded-btn p-2 focus:bg-white"
            />
          ) : (
            <p className="text-slate-dark text-[13.5px] leading-relaxed">
              {note.history_of_present_illness || 'Not documented'}
            </p>
          )}
        </div>

        {/* Pertinent Negatives */}
        {note.capabilities?.negation && note.negated_findings?.length > 0 && (
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-teal block mb-1">
              {t('app.note.pertinentNegatives')}
            </label>
            <div className="flex flex-wrap gap-1.5">
              {note.negated_findings.map((item, i) => (
                <span
                  key={i}
                  className="bg-navy-50 text-navy-800 text-xs px-2.5 py-0.5 rounded-full border border-navy-100 font-medium"
                >
                  No {item}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Assessment */}
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-teal block mb-1">
            {t('app.note.assessment')}
          </label>
          {isEditing ? (
            <textarea
              rows={2}
              value={draftAssessment}
              onChange={(e) => setDraftAssessment(e.target.value)}
              className="w-full text-sm text-slate-dark bg-surface-alt border border-surface-border rounded-btn p-2 focus:bg-white"
            />
          ) : (
            <p className="text-slate-dark text-[13.5px] leading-relaxed">
              {note.assessment || 'Requires doctor review.'}
            </p>
          )}
        </div>

        {/* Plan */}
        <div>
          <label className="text-xs font-bold uppercase tracking-wider text-teal block mb-1">
            {t('app.note.plan')}
          </label>
          {isEditing ? (
            <textarea
              rows={3}
              value={draftPlan.join('\n')}
              onChange={(e) => setDraftPlan(e.target.value.split('\n').filter((l) => l.trim().length > 0))}
              placeholder="Enter plan items (one per line)"
              className="w-full text-sm text-slate-dark bg-surface-alt border border-surface-border rounded-btn p-2 focus:bg-white"
            />
          ) : (
            <ul className="list-disc list-inside space-y-1 text-slate-dark text-[13.5px]">
              {note.plan?.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          )}
        </div>

        {/* Conditional Roadmap Sections: Allergies / Medications */}
        {note.capabilities?.allergies && (
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-teal block mb-1">
              {t('app.note.allergies')}
            </label>
            <p className="text-xs text-slate">None reported</p>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-3.5 border-t border-surface-border bg-white rounded-b-card flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="text-xs font-semibold text-slate hover:text-navy border border-surface-border bg-surface-alt px-3 py-2 rounded-btn flex items-center gap-1.5 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-teal" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? t('app.note.copied') : t('app.note.copy')}</span>
          </button>

          {/* Export Dropdown */}
          <div className="relative">
            <button
              onClick={() => setExportOpen(!exportOpen)}
              className="text-xs font-semibold text-slate hover:text-navy border border-surface-border bg-surface-alt px-3 py-2 rounded-btn flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-teal" />
              <span>{t('app.note.export')}</span>
              <ChevronDown className="w-3 h-3 text-slate-subtle" />
            </button>

            {exportOpen && (
              <div className="absolute left-0 bottom-full mb-1.5 w-44 bg-white border border-surface-border rounded-card shadow-card py-1 z-20">
                <button
                  onClick={() => handleExport('txt')}
                  className="w-full text-left px-3.5 py-1.5 text-xs text-slate hover:bg-surface-alt hover:text-navy"
                >
                  Plain Text (.txt)
                </button>
                <button
                  onClick={() => handleExport('soap')}
                  className="w-full text-left px-3.5 py-1.5 text-xs text-slate hover:bg-surface-alt hover:text-navy"
                >
                  SOAP Markdown (.md)
                </button>
                <button
                  onClick={() => handleExport('json')}
                  className="w-full text-left px-3.5 py-1.5 text-xs text-slate hover:bg-surface-alt hover:text-navy"
                >
                  Full JSON (.json)
                </button>
                <button
                  onClick={() => handleExport('fhir')}
                  className="w-full text-left px-3.5 py-1.5 text-xs text-slate hover:bg-surface-alt hover:text-navy border-t border-surface-border/60 flex items-center justify-between"
                >
                  <span>FHIR R4 Bundle</span>
                  <span className="text-[10px] bg-slate/10 px-1 rounded text-slate">Phase 4</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Approve & Sign Status Toggle */}
        <button
          onClick={toggleApproval}
          className={`text-xs font-semibold px-4 py-2 rounded-btn flex items-center gap-1.5 transition-all shadow-soft active:scale-95 ${
            isReviewed
              ? 'bg-emerald-600 text-white hover:bg-emerald-700'
              : 'bg-teal hover:bg-teal-600 text-white'
          }`}
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{isReviewed ? t('app.note.approved') : t('app.note.approveSign')}</span>
        </button>
      </div>
    </div>
  );
};
