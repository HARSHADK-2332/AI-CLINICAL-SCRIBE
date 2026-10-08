import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Navbar } from '../components/Navbar';
import '../i18n';
import i18n from '../i18n';

describe('Language Switcher in Navbar', () => {
  it('renders language switch options for English, Hindi, and Telugu', () => {
    render(
      <Navbar
        onOpenDemo={() => {}}
        currentPath="/"
        onNavigate={() => {}}
      />
    );

    expect(screen.getByRole('button', { name: /switch language to english/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /switch language to हिंदी/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /switch language to తెలుగు/i })).toBeInTheDocument();
  });

  it('switches application language when pill is clicked', async () => {
    render(
      <Navbar
        onOpenDemo={() => {}}
        currentPath="/"
        onNavigate={() => {}}
      />
    );

    const hindiBtn = screen.getByRole('button', { name: /switch language to हिंदी/i });
    fireEvent.click(hindiBtn);

    expect(i18n.language).toBe('hi');
    expect(document.documentElement.lang).toBe('hi');

    // Switch back to English
    const enBtn = screen.getByRole('button', { name: /switch language to english/i });
    fireEvent.click(enBtn);
    expect(i18n.language).toBe('en');
  });
});
