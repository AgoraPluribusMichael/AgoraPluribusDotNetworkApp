import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Index from './components/MainArticle.jsx'
import Topbar from './components/Topbar.jsx'
import Footer from './components/Footer.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Topbar />
    <Index />
    <Footer />
  </StrictMode>
)
