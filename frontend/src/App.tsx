import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import Layout from './components/Layout'
import CatalogPage from './pages/CatalogPage'
import DashboardPage from './pages/DashboardPage'
import ExportPage from './pages/ExportPage'
import RunsPage from './pages/RunsPage'
import ValidationPage from './pages/ValidationPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 5000 },
  },
})

function AnimatedRoutes() {
  const location = useLocation()
  return (
    <motion.div
      key={location.pathname}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.21, 0.47, 0.32, 0.98] }}
    >
      <Routes location={location}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/runs" element={<RunsPage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/validation" element={<ValidationPage />} />
        <Route path="/export" element={<ExportPage />} />
      </Routes>
    </motion.div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <AnimatedRoutes />
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
