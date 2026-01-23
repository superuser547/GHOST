import js from '@eslint/js'
import globals from 'globals'

import tsParser from '@typescript-eslint/parser'
import tsPlugin from '@typescript-eslint/eslint-plugin'

import reactPlugin from 'eslint-plugin-react'
import reactHooksPlugin from 'eslint-plugin-react-hooks'

import prettier from 'eslint-config-prettier'

export default [
  // Глобальные исключения (замена .eslintignore для flat config)
  {
    ignores: ['node_modules/**', 'dist/**', 'coverage/**', '*.min.*'],
  },

  js.configs.recommended,

  // TS/TSX + React
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      react: reactPlugin,
      'react-hooks': reactHooksPlugin,
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      ...reactPlugin.configs.recommended.rules,
      ...reactHooksPlugin.configs.recommended.rules,
    },
  },

  // Отключить стилистические правила, которые конфликтуют с Prettier
  prettier,
]
