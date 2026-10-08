import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { X, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { api, type DemoRequestData } from '../services/api';

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DemoModal: React.FC<DemoModalProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<DemoRequestData>({
    name: '',
    email: '',
    organization: '',
    role: '',
    message: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Basic email regex validation before submitting
    const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    if (!emailPattern.test(formData.email.trim())) {
      setError('Please provide a valid corporate or clinical email address.');
      return;
    }

    try {
      setLoading(true);
      await api.submitDemoRequest(formData);
      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Failed to submit demo request.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSubmitted(false);
    setFormData({ name: '', email: '', organization: '', role: '', message: '' });
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 z-50 overflow-y-auto bg-navy-950/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6"
    >
      <div className="relative bg-white rounded-card shadow-card max-w-lg w-full border border-surface-border p-6 sm:p-8 animate-in fade-in zoom-in-95 duration-200">
        {/* Close Button */}
        <button
          onClick={handleReset}
          className="absolute top-5 right-5 p-2 rounded-btn text-slate hover:text-navy hover:bg-surface-alt transition-colors"
          aria-label={t('demoModal.close')}
        >
          <X className="w-5 h-5" />
        </button>

        {submitted ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 rounded-full bg-teal-100 text-teal flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-9 h-9" />
            </div>
            <h3 id="modal-title" className="text-2xl font-bold text-navy mb-2">
              {t('demoModal.successTitle')}
            </h3>
            <p className="text-slate mb-6 leading-relaxed">
              {t('demoModal.successMessage')}
            </p>
            <button
              onClick={handleReset}
              className="bg-navy hover:bg-navy-800 text-white font-semibold px-6 py-2.5 rounded-btn transition-colors"
            >
              {t('demoModal.close')}
            </button>
          </div>
        ) : (
          <div>
            <div className="mb-6">
              <span className="text-[11px] font-bold tracking-widest text-teal uppercase bg-teal-100 px-2.5 py-0.5 rounded-full">
                Clinical Enterprise
              </span>
              <h3 id="modal-title" className="mt-2 text-2xl font-extrabold text-navy tracking-tight">
                {t('demoModal.title')}
              </h3>
              <p className="mt-1 text-sm text-slate">
                {t('demoModal.subtitle')}
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-btn flex items-center gap-2.5 text-xs text-red-700">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  {t('demoModal.name')} *
                </label>
                <input
                  type="text"
                  required
                  placeholder={t('demoModal.namePlaceholder')}
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3.5 py-2.5 text-sm bg-surface-alt border border-surface-border rounded-btn focus:bg-white focus:border-teal transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  {t('demoModal.email')} *
                </label>
                <input
                  type="email"
                  required
                  placeholder={t('demoModal.emailPlaceholder')}
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3.5 py-2.5 text-sm bg-surface-alt border border-surface-border rounded-btn focus:bg-white focus:border-teal transition-colors"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                    {t('demoModal.organization')} *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder={t('demoModal.organizationPlaceholder')}
                    value={formData.organization}
                    onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-sm bg-surface-alt border border-surface-border rounded-btn focus:bg-white focus:border-teal transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                    {t('demoModal.role')} *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder={t('demoModal.rolePlaceholder')}
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full px-3.5 py-2.5 text-sm bg-surface-alt border border-surface-border rounded-btn focus:bg-white focus:border-teal transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  {t('demoModal.message')}
                </label>
                <textarea
                  rows={2}
                  placeholder={t('demoModal.messagePlaceholder')}
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  className="w-full px-3.5 py-2 text-sm bg-surface-alt border border-surface-border rounded-btn focus:bg-white focus:border-teal transition-colors resize-none"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-navy hover:bg-navy-800 disabled:opacity-70 text-white font-semibold py-3 px-4 rounded-btn shadow-soft flex items-center justify-center gap-2 transition-all active:scale-[0.99]"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-teal" />
                      <span>{t('demoModal.submitting')}</span>
                    </>
                  ) : (
                    <span>{t('demoModal.submit')}</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
