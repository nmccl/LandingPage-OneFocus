import { useEffect } from "react"
import "./App.css"
import Footer from "./components/Footer"
import HomePage from "./components/HomePage"
import Navbar from "./components/Navbar"

function App() {
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

export default App
