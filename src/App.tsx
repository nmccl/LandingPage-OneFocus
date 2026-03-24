import { useEffect } from "react"
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom"
import "./App.css"
import Footer from "./components/Footer"
import HomePage from "./components/HomePage"
import Navbar from "./components/Navbar"
import PrivacyPolicy from "./components/PrivacyPolicy"
import TermsOfUse from "./components/TermsOfUse"

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])
  return null
}

function MainLayout() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible")
            obs.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.15, rootMargin: "0px 0px -5%" }
    )

    const elements = document.querySelectorAll(".fade-in-up, .fade-in-down, .fade-in")
    elements.forEach((el) => observer.observe(el))

    return () => observer.disconnect()
  }, [])

  return (
    <>
      <Navbar />
      <HomePage />
      <Footer />
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<MainLayout />} />
        <Route path="/privacy" element={<><Navbar /><PrivacyPolicy /><Footer /></>} />
        <Route path="/terms" element={<><Navbar /><TermsOfUse /><Footer /></>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
