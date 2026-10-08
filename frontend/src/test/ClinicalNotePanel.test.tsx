import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ClinicalNotePanel } from '../components/ClinicalNotePanel';
import { SAMPLE_NOTE } from '../services/api';
import '../i18n';

describe('ClinicalNotePanel Component', () => {
  it('renders Chief Complaint, HPI, Assessment, and Plan', () => {
    render(
      <ClinicalNotePanel
        note={SAMPLE_NOTE}
        onUpdateNote={() => {}}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Cough and shortness of breath for 2 weeks/i)).toBeInTheDocument();
    expect(screen.getByText(/Patient reports a 2-week history of cough/i)).toBeInTheDocument();
    expect(screen.getByText(/Likely acute bronchitis/i)).toBeInTheDocument();
    expect(screen.getByText(/Chest X-ray/i)).toBeInTheDocument();
  });

  it('toggles inline edit mode and triggers update handler', () => {
    const handleUpdate = vi.fn();
    render(
      <ClinicalNotePanel
        note={SAMPLE_NOTE}
        onUpdateNote={handleUpdate}
        isLoading={false}
      />
    );

    const editBtn = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editBtn);

    // Chief complaint input should be visible
    const input = screen.getByDisplayValue(SAMPLE_NOTE.chief_complaint);
    expect(input).toBeInTheDocument();

    fireEvent.change(input, { target: { value: 'Severe bronchitis for 3 weeks' } });

    const doneBtn = screen.getByRole('button', { name: /done/i });
    fireEvent.click(doneBtn);

    expect(handleUpdate).toHaveBeenCalledWith(expect.objectContaining({
      chief_complaint: 'Severe bronchitis for 3 weeks'
    }));
  });

  it('toggles approval status between draft and reviewed', () => {
    const handleUpdate = vi.fn();
    render(
      <ClinicalNotePanel
        note={SAMPLE_NOTE}
        onUpdateNote={handleUpdate}
        isLoading={false}
      />
    );

    const approveBtn = screen.getByRole('button', { name: /approve & sign/i });
    fireEvent.click(approveBtn);

    expect(handleUpdate).toHaveBeenCalledWith({ status: 'reviewed' });
  });

  it('displays export menu options and handles FHIR roadmap notice', async () => {
    render(
      <ClinicalNotePanel
        note={SAMPLE_NOTE}
        onUpdateNote={() => {}}
        isLoading={false}
      />
    );

    const exportBtn = screen.getByRole('button', { name: /export/i });
    fireEvent.click(exportBtn);

    expect(screen.getByText(/Plain Text \(\.txt\)/i)).toBeInTheDocument();
    expect(screen.getByText(/SOAP Markdown \(\.md\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Full JSON \(\.json\)/i)).toBeInTheDocument();
    expect(screen.getByText(/FHIR R4 Bundle/i)).toBeInTheDocument();

    const fhirBtn = screen.getByText(/FHIR R4 Bundle/i);
    fireEvent.click(fhirBtn);

    await waitFor(() => {
      expect(screen.getByText(/FHIR R4 export is scheduled for Phase 4 roadmap/i)).toBeInTheDocument();
    });
  });
});
