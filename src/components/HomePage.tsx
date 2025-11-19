import OneFocusIcon from "../assets/OneFocus_nobg.png"
import { Button } from "./ui/button"
import { ClipboardList, Clock, StickyNote, Clipboard } from "lucide-react"
import Devices from "../assets/Devices.png"

const fontFamily =
  '"SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Helvetica,Arial,sans-serif'

const HomePage = () => {
  return (
    <section
      id="home"
      className="home-section flex flex-col items-center justify-center scroll-mt-32 w-full px-6"
    >
      <img
        src={OneFocusIcon}
        alt="OneFocus Logo"
        className="w-150 h-150 sm:w-120 sm:h-120 object-contain drop-shadow-xl mt-5"
      />
      <h2 className="text-5xl font-semibold fade-in-up" style={{ fontFamily }}>
        A cleaner way to get things done.
      </h2>
      <p className="text-2xl font-normal mt-5 fade-in-up" style={{ fontFamily }}>
        Simple tools for productivity, focus, and minimalism
      </p>

      <Button
        variant="default"
        className="bg-black text-white hover:bg-neutral-800 mt-8 fade-in-up fade-delay-1"
      >
        Download (coming soon)
      </Button>

      <div
        id="features"
        className="features-section max-w-4xl mx-auto px-6 text-center mt-20 fade-in-up fade-delay-1 scroll-mt-32"
      >
        <h2 className="text-4xl font-medium mb-14 mt-10">Everything you need to focus.</h2>

        <div className="features-grid grid grid-cols-1 md:grid-cols-2 gap-x-50 gap-y-10 text-left">
          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <ClipboardList className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Quick Tasks</h3>
              <p className="text-neutral-600 text-sm">Capture what matters in seconds.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <Clock className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Session Timer</h3>
              <p className="text-neutral-600 text-sm">Stay in flow with focus sessions.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <Clipboard className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Clipboard Vault</h3>
              <p className="text-neutral-600 text-sm">Find what you copied, instantly.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <StickyNote className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Quick Notes</h3>
              <p className="text-neutral-600 text-sm">Write notes with a touch of a hotkey or widget.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="devices-section text-black flex fade-in-up fade-delay-2 scroll-mt-32">
        <div className="flex-row max-w-65 mt-50 mr-20">
          <h2 className="text-3xl mb-5">Seamless across macOS and iOS</h2>
          <p className="text-sm text-neutral-600">
            Everything stays updated automatically - your focus, anywhere.
          </p>
        </div>
        <img
          src={Devices}
          className="devices-image w-150 h-150 sm:w-120 sm:h-120 mt-5 fade-in-up fade-delay-2"
          alt="Devices showcasing OneFocus"
        />
      </div>

      <section
        id="waitlist"
        className="waitlist-section fade-in-up fade-delay-3 flex flex-col items-center text-center mt-24 scroll-mt-32 lg:w-[900px] px-0 lg:px-6 -mx-6 sm:mx-0"
      >
        <div className="waitlist-card w-full lg:max-w-5xl rounded-[36px] border border-black/5 bg-white/95 p-4 sm:p-10 lg:p-11 shadow-2xl shadow-black/15 backdrop-blur-md mx-0 lg:mx-auto">
          <p className="text-sm sm:text-base uppercase tracking-[0.5em] text-neutral-500 mb-5 sm:mb-7" style={{ fontFamily }}>
            Early Access
          </p>
          <h2 className="text-4xl sm:text-5xl font-semibold mb-5 sm:mb-8 leading-tight" style={{ fontFamily }}>
            Join the OneFocus Waitlist
          </h2>
          <p className="text-lg sm:text-xl text-neutral-600 mb-7 sm:mb-12" style={{ fontFamily }}>
            Sign up to get the latest updates and be the first to try the cleanest productivity suite.
          </p>
          <div className="rounded-3xl border border-neutral-200 bg-neutral-50/90 p-4 sm:p-6 shadow-inner">
            <iframe
              src="https://tally.so/r/9qqJ7E"
              
              frameBorder="0"
              title="OneFocus Waitlist"
              className="w-full rounded-[28px] bg-white h-[300px] sm:h-[400px] lg:h-[400px]"
            />
          </div>
        </div>
      </section>
    </section>
  )
}

export default HomePage
