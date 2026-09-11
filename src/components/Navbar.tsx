import React, { useState } from "react"
import { Menu, X } from "lucide-react"
import { Link, useLocation } from "react-router-dom"

interface NavItem {
  name: string
  href: string
  external?: boolean
}

//const APP_STORE_URL = "https://apps.apple.com/app/onefocus/id000000000"

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const { pathname } = useLocation()
  const isHome = pathname === "/"

  const navItems: NavItem[] = isHome
    ? [
        { name: "Features", href: "#features" },
        { name: "Pricing", href: "#pricing" },
        { name: "FAQ", href: "#faq" },
      ]
    : [
        { name: "Home", href: "/" },
      ]

  return (
    <nav className="fade-in-down fixed top-0 left-0 w-full bg-white/70 backdrop-blur-md border-b border-neutral-200 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <Link to="/" className="text-lg font-semibold tracking-tight text-black">
            OneFocus
          </Link>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          {navItems.map((item) =>
            item.href.startsWith("#") ? (
              <a
                key={item.name}
                href={item.href}
                className="text-lg text-neutral-800 hover:text-black transition-colors"
              >
                {item.name}
              </a>
            ) : (
              <Link
                key={item.name}
                to={item.href}
                className="text-lg text-neutral-800 hover:text-black transition-colors"
              >
                {item.name}
              </Link>
            )
          )}
          <a
           
            className="bg-black text-white text-sm font-medium px-4 py-2 rounded-full hover:bg-neutral-800 transition-colors"
          >
           Coming Soon
          </a>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden text-neutral-800"
          aria-label="Toggle Menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-neutral-200 px-6 py-4 space-y-4">
          {navItems.map((item) =>
            item.href.startsWith("#") ? (
              <a
                key={item.name}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className="block text-sm text-neutral-800 hover:text-black transition-colors"
              >
                {item.name}
              </a>
            ) : (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setIsOpen(false)}
                className="block text-sm text-neutral-800 hover:text-black transition-colors"
              >
                {item.name}
              </Link>
            )
          )}
          <a
          
            className="block text-sm font-medium text-black hover:text-neutral-700 transition-colors"
          >
            Coming soon to the App Store
          </a>
        </div>
      )}
    </nav>
  )
}

export default Navbar
