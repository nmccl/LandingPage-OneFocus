import { FaInstagram, FaGithub } from "react-icons/fa"
import { FiLink } from "react-icons/fi"
import { Link } from "react-router-dom"

const fontFamily =
  '"SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Helvetica,Arial,sans-serif'

const Footer = () => {
  return (
    <footer
      id="contact"
      className="fade-in-up fade-delay-3 mt-16 w-full scroll-mt-32 border-t border-neutral-200 bg-[#fbfafb] px-4 py-10 text-center sm:px-6"
      style={{ fontFamily }}
    >
      <h2 className="text-xl font-medium sm:text-2xl">Made by Noah McClung.</h2>

      <div className="mt-4 flex flex-wrap items-center justify-center gap-4 text-2xl text-primary sm:gap-6 sm:text-3xl">
        <a
          href="https://www.instagram.com/imnoahmcclung/"
          aria-label="Noah McClung on Instagram"
          target="_blank"
          rel="noreferrer"
          className="transition hover:text-primary/70"
        >
          <FaInstagram />
        </a>
        <a
          href="https://www.github.com/nmccl"
          aria-label="Noah McClung on GitHub"
          target="_blank"
          rel="noreferrer"
          className="transition hover:text-primary/70"
        >
          <FaGithub />
        </a>
        <a
          href="https://noahmcclung.com"
          aria-label="Noah McClung personal website"
          target="_blank"
          rel="noreferrer"
          className="transition hover:text-primary/70"
        >
          <FiLink />
        </a>
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-center gap-5 text-sm text-neutral-500">
        <Link to="/privacy" className="hover:text-neutral-800 transition-colors">
          Privacy Policy
        </Link>
        <span className="text-neutral-300">·</span>
        <Link to="/terms" className="hover:text-neutral-800 transition-colors">
          Terms of Use
        </Link>
        <span className="text-neutral-300">·</span>
        <a
          href="mailto:support@noahmcclung.com"
          className="hover:text-neutral-800 transition-colors"
        >
          Support
        </a>
      </div>

      <p className="mt-5 text-xs text-neutral-400">
        © {new Date().getFullYear()} Noah McClung. All rights reserved.
      </p>
    </footer>
  )
}

export default Footer
