import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('eu-ai-theme') || 'dark'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('eu-ai-theme', theme)
  }, [theme])

  const themes = [
    { id: 'dark', label: 'Regulatory Dark', icon: '◈' },
    { id: 'light', label: 'Executive Light', icon: '◎' },
    { id: 'contrast', label: 'High Contrast', icon: '◆' },
  ]

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themes }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
