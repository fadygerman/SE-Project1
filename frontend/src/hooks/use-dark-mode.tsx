import { useState, useEffect } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface UseThemeOptions {
  defaultTheme?: Theme;
  storageKey?: string;
}

/**
 * A custom hook to manage 'light', 'dark', or 'system' themes without Context.
 */
export function useTheme({
  defaultTheme = 'system',
  storageKey = 'my-app-theme',
}: UseThemeOptions = {}) {
  // 1. Initialize from localStorage or fallback to defaultTheme
  const [theme, setThemeState] = useState<Theme>(() => {
    const stored = localStorage.getItem(storageKey);
    // If stored is one of 'light'/'dark'/'system', use it
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      return stored;
    }
    return defaultTheme;
  });

  // 2. Sync to <html> class and localStorage whenever theme changes
  useEffect(() => {
    const root = window.document.documentElement;
    // Remove any existing theme classes so they don't stack
    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      // Apply the OS-level preference
      root.classList.add(isDark ? 'dark' : 'light');
    } else {
      // Apply whichever theme is explicitly set
      root.classList.add(theme);
    }

    // Store theme in localStorage
    localStorage.setItem(storageKey, theme);
  }, [theme, storageKey]);

  // A setter function you can call to change the theme
  function setTheme(newTheme: Theme) {
    setThemeState(newTheme);
  }

  // Optionally add a quick toggle if only 'light' or 'dark' is important to you:
  function toggleTheme() {
    setThemeState((prev) => (prev === 'light' ? 'dark' : 'light'));
  }

  return { theme, setTheme, toggleTheme };
}
