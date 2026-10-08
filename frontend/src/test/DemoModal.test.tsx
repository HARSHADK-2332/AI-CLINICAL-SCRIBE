import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DemoModal } from '../components/DemoModal';
import { api } from '../services/api';
import '../i18n';

describe('DemoModal Component', () => {
  it('renders modal fields when open', () => {
    render(<DemoModal isOpen={true} onClose={() => {}} />);

    expect(screen.getByRole('heading', { name: /request a scribecare demo/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/dr\. sarah jenkins/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/s\.jenkins@healthsystem\.org/i)).toBeInTheDocument();
  });

  it('validates email format before submitting', async () => {
    render(<DemoModal isOpen={true} onClose={() => {}} />);

    fireEvent.change(screen.getByPlaceholderText(/dr\. sarah jenkins/i), {
      target: { value: 'Dr. Test' },
    });
    fireEvent.change(screen.getByPlaceholderText(/s\.jenkins@healthsystem\.org/i), {
      target: { value: 'invalid-email' },
    });
    fireEvent.change(screen.getByPlaceholderText(/valley regional/i), {
      target: { value: 'Test Hospital' },
    });
    fireEvent.change(screen.getByPlaceholderText(/lead physician/i), {
      target: { value: 'Physician' },
    });

    const submitBtn = screen.getByRole('button', { name: /submit request/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/please provide a valid corporate or clinical email address/i)).toBeInTheDocument();
    });
  });

  it('submits valid form data and shows confirmation message', async () => {
    vi.spyOn(api, 'submitDemoRequest').mockResolvedValueOnce({
      id: 1,
      status: 'received',
      message: 'Demo request submitted successfully.',
    });

    render(<DemoModal isOpen={true} onClose={() => {}} />);

    fireEvent.change(screen.getByPlaceholderText(/dr\. sarah jenkins/i), {
      target: { value: 'Dr. Sarah Jenkins' },
    });
    fireEvent.change(screen.getByPlaceholderText(/s\.jenkins@healthsystem\.org/i), {
      target: { value: 's.jenkins@healthsystem.org' },
    });
    fireEvent.change(screen.getByPlaceholderText(/valley regional/i), {
      target: { value: 'Valley Regional Medical Center' },
    });
    fireEvent.change(screen.getByPlaceholderText(/lead physician/i), {
      target: { value: 'CMIO' },
    });

    const submitBtn = screen.getByRole('button', { name: /submit request/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/demo requested!/i)).toBeInTheDocument();
    });
  });
});
