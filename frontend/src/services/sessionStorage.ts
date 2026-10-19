/**
 * Centralized session storage management for HealthSense AI.
 * Ensures clean workflow switching and prevents cross-flow state leakage.
 */

export const clearQuestionnaireSessionState = (): void => {
  try {
    sessionStorage.removeItem('healthsense_active_screening_type');
    sessionStorage.removeItem('healthsense_active_view');
    const types = ['alzheimers', 'parkinsons', 'both'];
    types.forEach(t => {
      sessionStorage.removeItem(`healthsense_answers_${t}`);
      sessionStorage.removeItem(`healthsense_index_${t}`);
    });
    // Remove any remaining healthsense_ session keys
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const key = sessionStorage.key(i);
      if (key && key.startsWith('healthsense_')) {
        sessionStorage.removeItem(key);
      }
    }
  } catch (e) {
    // Fail-safe if storage is blocked
  }
};

export const clearReportSessionState = (): void => {
  try {
    // Remove any report-related session keys if set in future
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const key = sessionStorage.key(i);
      if (key && (key.startsWith('healthsense_report') || key.startsWith('healthsense_pdf'))) {
        sessionStorage.removeItem(key);
      }
    }
  } catch (e) {
    // Fail-safe if storage is blocked
  }
};

export const clearAllHealthSenseSession = (): void => {
  clearQuestionnaireSessionState();
  clearReportSessionState();
};
