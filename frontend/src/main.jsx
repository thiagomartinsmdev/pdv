// Ponto de entrada do React: monta a aplicação na <div id="root"> do index.html.
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'

import App from './App.jsx'
import { AuthProvider } from './contexts/AuthProvider.jsx'
import './styles/global.css'

// A ordem dos "provedores" importa: o AuthProvider usa o roteador (para redirecionar
// ao login quando a sessão expira), então ele precisa ficar dentro do BrowserRouter.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
