import React, { useState } from "react";
import { Menu, X } from "lucide-react";



interface NavItem {
  name: string;
  href: string;
}

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const navItems: NavItem[] = [
    { name: "Home", href: "#home" },
    { name: "Features", href: "#features" },
    { name: "Download", href: "#download" },
    { name: "Contact", href: "#contact" },
  ];

  return (
    <nav className="fade-in-down fixed top-0 left-0 w-full bg-white/70 backdrop-blur-md border-b border-neutral-200 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <span className="text-lg font-semibold tracking-tight text-black">
            OneFocus
          </span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          {navItems.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="text-lg text-neutral-800 hover:text-black transition-colors"
            >
              {item.name}
            </a>
          ))}
          
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
          {navItems.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="block text-sm text-neutral-800 hover:text-black transition-colors"
            >
              {item.name}
            </a>
          ))}
         
        </div>
      )}
    </nav>
  );
};

export default Navbar;
