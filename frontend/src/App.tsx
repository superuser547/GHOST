import React from 'react'

const containerStyle: React.CSSProperties = {
  padding: '2rem',
  fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  lineHeight: 1.6,
}

function App() {
  return (
    <div style={containerStyle}>
      <h1>GHOST — конструктор отчётов по ГОСТ/МИСИС</h1>
      <p>
        Это фронтенд-проект (React + TypeScript), который в будущем будет содержать
        визуальный конструктор отчётов: блоки, структуру, проверки и экспорт.
      </p>
      <p>
        Подробные функциональные и технические требования см. в файле{' '}
        <a href="../REQUIREMENTS.md" target="_blank" rel="noreferrer">
          REQUIREMENTS.md
        </a>
        .
      </p>
      <p>
        Сейчас это только минимальная заглушка. Реальный интерфейс будет добавляться
        поэтапно.
      </p>
    </div>
  )
}

export default App
