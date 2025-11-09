import { FaInstagram, FaGithub } from "react-icons/fa"
import { FiLink } from "react-icons/fi"

const Footer = () => {
  return (
    <footer
      id="contact"
      className="fade-in-up fade-delay-3 mt-16 w-full scroll-mt-32 border-t border-neutral-200 bg-[#fbfafb] px-4 py-10 text-center sm:px-6"
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
          href="https://www.noahmcclung.com"
          aria-label="Noah McClung personal website"
          target="_blank"
          rel="noreferrer"
          className="transition hover:text-primary/70"
        >
          <FiLink />
        </a>
      </div>
    </footer>
  )
}

export default Footer
