export interface TranscriptSegment {
  speaker: 'Doctor' | 'Patient' | 'Unknown';
  start: number;
  end: number;
  text: string;
}

export interface NoteCapabilities {
  allergies: boolean;
  medications: boolean;
  negation: boolean;
  diarization: boolean;
}

export interface ClinicalNote {
  id?: number;
  patient_id?: number;
  chief_complaint: string;
  history_of_present_illness: string;
  assessment: string;
  plan: string[];
  allergies: string[];
  medications: string[];
  negated_findings: string[];
  status: 'draft' | 'reviewed';
  language: string;
  capabilities: NoteCapabilities;
  created_at?: string;
  updated_at?: string;
}

export interface Patient {
  id: number;
  name: string;
  age: number;
  gender: string;
  medical_record_number: string;
}

export interface DemoRequestData {
  name: string;
  email: string;
  organization: string;
  role: string;
  message?: string;
}

export const SAMPLE_TRANSCRIPT: TranscriptSegment[] = [
  {
    speaker: 'Doctor',
    start: 0.0,
    end: 2.8,
    text: 'How long have you been experiencing these symptoms?'
  },
  {
    speaker: 'Patient',
    start: 3.1,
    end: 8.4,
    text: 'About 2 weeks now. It started with a mild cough and then I began to feel short of breath when I move around.'
  },
  {
    speaker: 'Doctor',
    start: 8.9,
    end: 11.5,
    text: 'Do you have any fever, chest pain or other symptoms?'
  },
  {
    speaker: 'Patient',
    start: 12.0,
    end: 16.8,
    text: "No fever. Just the cough and shortness of breath. It's worse in the morning."
  }
];

export const SAMPLE_NOTE: ClinicalNote = {
  id: 101,
  patient_id: 1,
  chief_complaint: 'Cough and shortness of breath for 2 weeks.',
  history_of_present_illness: 'Patient reports a 2-week history of cough, initially mild, with progressive shortness of breath on exertion. No fever, no chest pain. Symptoms are worse in the morning.',
  assessment: 'Likely acute bronchitis vs. mild lower respiratory tract infection. Rule out early pneumonia.',
  plan: [
    'Chest X-ray (PA and lateral views)',
    'Symptomatic treatment (hydration, rest, antitussive as indicated)',
    'Follow up in 3 days or earlier if symptoms worsen'
  ],
  allergies: [],
  medications: [],
  negated_findings: ['fever', 'chest pain'],
  status: 'draft',
  language: 'en',
  capabilities: {
    allergies: false,
    medications: false,
    negation: true,
    diarization: false,
  },
  created_at: new Date().toISOString(),
};

const IS_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || import.meta.env.VITE_USE_MOCK === true;

export const api = {
  isMockMode: () => IS_MOCK,

  async getHealth() {
    if (IS_MOCK) {
      return { status: 'ok', whisper_loaded: true, ffmpeg_available: true, mock_mode: true };
    }
    const res = await fetch('/api/health');
    return res.json();
  },

  async getPatients(): Promise<Patient[]> {
    if (IS_MOCK) {
      return [
        { id: 1, name: 'Sarah Jenkins', age: 42, gender: 'Female', medical_record_number: 'MRN-10492' },
        { id: 2, name: 'David Miller', age: 58, gender: 'Male', medical_record_number: 'MRN-20984' },
        { id: 3, name: 'Priya Sharma', age: 29, gender: 'Female', medical_record_number: 'MRN-39481' },
      ];
    }
    try {
      const res = await fetch('/api/patients');
      if (!res.ok) throw new Error('Failed to load patients');
      return await res.json();
    } catch {
      // Fallback
      return [
        { id: 1, name: 'Sarah Jenkins', age: 42, gender: 'Female', medical_record_number: 'MRN-10492' },
        { id: 2, name: 'David Miller', age: 58, gender: 'Male', medical_record_number: 'MRN-20984' },
        { id: 3, name: 'Priya Sharma', age: 29, gender: 'Female', medical_record_number: 'MRN-39481' },
      ];
    }
  },

  async transcribeAudio(file: File, language?: string): Promise<{ segments: TranscriptSegment[]; language: string }> {
    if (IS_MOCK) {
      // Simulate real-time streaming delay
      await new Promise(r => setTimeout(r, 1200));
      return { segments: SAMPLE_TRANSCRIPT, language: language || 'en' };
    }

    const formData = new FormData();
    formData.append('audio', file);
    if (language) {
      formData.append('language', language);
    }

    const res = await fetch('/api/transcribe', {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Transcription failed with code ${res.status}`);
    }

    return res.json();
  },

  async transcribeSampleAudio(filename: string, language?: string): Promise<{ segments: TranscriptSegment[]; language: string }> {
    if (IS_MOCK) {
      await new Promise(r => setTimeout(r, 1000));
      return { segments: SAMPLE_TRANSCRIPT, language: language || 'en' };
    }

    const url = `/api/sample-audio/${encodeURIComponent(filename)}/transcribe` + (language ? `?language=${encodeURIComponent(language)}` : '');
    const res = await fetch(url, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Sample audio transcription failed.');
    }
    return res.json();
  },

  async generateNote(segments: TranscriptSegment[], language?: string, patientId?: number): Promise<ClinicalNote> {
    if (IS_MOCK) {
      await new Promise(r => setTimeout(r, 1000));
      return { ...SAMPLE_NOTE, id: Math.floor(Math.random() * 900) + 100, patient_id: patientId || 1 };
    }

    const res = await fetch('/api/notes/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript: segments,
        language: language || 'en',
        patient_id: patientId,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Note generation failed.');
    }

    return res.json();
  },

  async updateNote(noteId: number, data: Partial<ClinicalNote>): Promise<ClinicalNote> {
    if (IS_MOCK) {
      return { ...SAMPLE_NOTE, ...data, id: noteId };
    }

    const res = await fetch(`/api/notes/${noteId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      throw new Error('Failed to update clinical note.');
    }

    return res.json();
  },

  async exportNote(noteId: number, format: 'txt' | 'json' | 'soap' | 'fhir'): Promise<{ blob: Blob; filename: string }> {
    if (format === 'fhir') {
      throw new Error('FHIR R4 export is scheduled for Phase 4 roadmap and not yet implemented.');
    }

    if (IS_MOCK) {
      const text = format === 'json'
        ? JSON.stringify(SAMPLE_NOTE, null, 2)
        : `SCRIBECARE CLINICAL NOTE\nChief Complaint: ${SAMPLE_NOTE.chief_complaint}\nHPI: ${SAMPLE_NOTE.history_of_present_illness}`;
      const blob = new Blob([text], { type: format === 'json' ? 'application/json' : 'text/plain' });
      return { blob, filename: `scribecare_note_${noteId}.${format === 'soap' ? 'md' : format}` };
    }

    const res = await fetch(`/api/notes/${noteId}/export?format=${format}`, {
      method: 'POST',
    });

    if (res.status === 501) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'FHIR R4 export is scheduled for Phase 4 roadmap and not yet implemented.');
    }

    if (!res.ok) {
      throw new Error(`Export failed with status ${res.status}`);
    }

    const disposition = res.headers.get('Content-Disposition') || '';
    const match = disposition.match(/filename="?([^"]+)"?/);
    const filename = match ? match[1] : `note_${noteId}.${format === 'soap' ? 'md' : format}`;
    const blob = await res.blob();
    return { blob, filename };
  },

  async submitDemoRequest(data: DemoRequestData) {
    if (IS_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return { id: 99, status: 'received', message: 'Demo request submitted successfully.' };
    }

    const res = await fetch('/api/demo-requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to submit demo request.');
    }

    return res.json();
  }
};
