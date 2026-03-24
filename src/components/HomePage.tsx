import OneFocusIcon from "../assets/icon.png"
import { Button } from "./ui/button"
import { ClipboardList, Clock, StickyNote, Clipboard, Cloud, Palette, ChevronDown, ChevronUp, Check } from "lucide-react"
import { useState } from "react"

const fontFamily =
  '"SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Helvetica,Arial,sans-serif'

// App Store placeholder — replace with your real link once the app is live
const APP_STORE_URL = "https://apps.apple.com/app/onefocus/id000000000"

const faqs = [
  {
    q: "Is OneFocus free to use?",
    a: "Yes. OneFocus is free to download with a generous free tier that includes up to 20 tasks, 15 notes, 20 clipboard items, and 5 focus sessions per day. OneFocus Pro unlocks everything with a 7-day free trial.",
  },
  {
    q: "What is included in OneFocus Pro?",
    a: "Pro gives you unlimited focus sessions, tasks, notes, and clipboard history, plus custom themes, iCloud sync across all your devices, the menu bar widget, keyboard shortcuts, advanced statistics, and more.",
  },
  {
    q: "How much does OneFocus Pro cost?",
    a: "OneFocus Pro is $12.99 per year, billed annually. Your first 7 days are completely free — no charge until the trial ends, and you can cancel any time before then.",
  },
  {
    q: "Can I use OneFocus on both my Mac and iPhone?",
    a: "Yes. OneFocus is a universal purchase — one subscription covers both macOS and iOS. iCloud sync keeps everything in perfect sync across your devices automatically.",
  },
  {
    q: "How do I cancel my subscription?",
    a: "You can cancel at any time from System Settings → Apple ID → Subscriptions on macOS, or Settings → Apple ID → Subscriptions on iOS. Your Pro access continues until the end of the current billing period.",
  },
  {
    q: "Does OneFocus work offline?",
    a: "Yes. All your data is stored locally first. iCloud sync runs in the background when you have a connection, so OneFocus is fully functional even without internet access.",
  },
  {
    q: "Is my data private?",
    a: "Absolutely. Your notes, tasks, and clipboard history are stored on your device and synced only through your private iCloud account. We never have access to your data. See our Privacy Policy for full details.",
  },
  {
    q: "What macOS and iOS versions are required?",
    a: "OneFocus requires macOS 26.2 or later, and iOS 26.2 or later. This app utilises Apple's latest frameworks and UI changes.",
  },
]

const FaqItem = ({ q, a }: { q: string; a: string }) => {
  const [open, setOpen] = useState(false)
  return (
    <div
      className="border-b border-neutral-200 last:border-0 py-5 cursor-pointer text-left"
      onClick={() => setOpen(!open)}
    >
      <div className="flex items-center justify-between gap-4">
        <span className="text-base font-medium text-neutral-900" style={{ fontFamily }}>{q}</span>
        {open ? (
          <ChevronUp className="w-5 h-5 text-neutral-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-neutral-400 flex-shrink-0" />
        )}
      </div>
      {open && (
        <p className="mt-3 text-sm text-neutral-600 leading-relaxed" style={{ fontFamily }}>{a}</p>
      )}
    </div>
  )
}

const HomePage = () => {
  return (
    <section
      id="home"
      className="home-section flex flex-col items-center justify-center scroll-mt-32 w-full px-6 pt-28 sm:pt-32"
    >
      <img
        src={OneFocusIcon}
        alt="OneFocus Logo"
        className="w-150 h-150 sm:w-70 sm:h-70 object-contain drop-shadow-xl mt-0 mb-10 sm:mb-5"
      />
      <h2 className="text-5xl font-semibold fade-in-up" style={{ fontFamily }}>
        A cleaner way to get things done.
      </h2>
      <p className="text-2xl font-normal mt-5 fade-in-up" style={{ fontFamily }}>
        Simple tools for productivity, focus, and minimalism
      </p>

      <a href={APP_STORE_URL} target="_blank" rel="noreferrer">
        <Button
          variant="default"
          className="bg-black text-white hover:bg-neutral-800 mt-8 fade-in-up fade-delay-1"
        >
          Download on the App Store
        </Button>
      </a>

      {/* ── Features ── */}
      <div
        id="features"
        className="features-section max-w-4xl mx-auto px-6 text-center mt-20 fade-in-up fade-delay-1 scroll-mt-32"
      >
        <h2 className="text-4xl font-medium mb-14 mt-10">Everything you need to focus.</h2>

        <div className="features-grid grid grid-cols-1 md:grid-cols-2 gap-x-50 gap-y-10 text-left">
          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <ClipboardList className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Smart Tasks</h3>
              <p className="text-neutral-600 text-sm">Capture, prioritise, and track what matters — with reminders, drag-and-drop ordering, and recurring tasks.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <Clock className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Focus Sessions</h3>
              <p className="text-neutral-600 text-sm">Stay in flow with a customisable focus timer. Track streaks, view session history, and see your productivity trends over time.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <Clipboard className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Clipboard History</h3>
              <p className="text-neutral-600 text-sm">Never lose a copied snippet again. OneFocus keeps your full clipboard history searchable and instantly accessible.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <StickyNote className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Quick Notes</h3>
              <p className="text-neutral-600 text-sm">Rich-text notes with a global hotkey or menu bar widget. Write fast, find faster.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <Cloud className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">iCloud Sync</h3>
              <p className="text-neutral-600 text-sm">Your tasks, notes, and focus history stay perfectly in sync across your Mac and iPhone — automatically.</p>
            </div>
          </div>

          <div className="flex items-start space-x-4 fade-in-up fade-delay-1">
            <Palette className="w-7 h-7 text-black flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-medium mb-1">Custom Themes</h3>
              <p className="text-neutral-600 text-sm">Choose from a curated set of themes — light, dark, Liquid Glass, and more — to make OneFocus feel like yours.</p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Pricing ── */}
      <div
        id="pricing"
        className="fade-in-up fade-delay-2 mt-24 scroll-mt-32 w-full max-w-4xl mx-auto px-6 text-center"
      >
        <h2 className="text-4xl font-medium mb-3" style={{ fontFamily }}>Simple, honest pricing.</h2>
        <p className="text-neutral-600 text-lg mb-12" style={{ fontFamily }}>
          Start for free. Upgrade when you're ready.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          {/* Free tier */}
          <div className="rounded-[28px] border border-neutral-200 bg-white p-8 shadow-sm">
            <p className="text-sm uppercase tracking-widest text-neutral-400 mb-3" style={{ fontFamily }}>Free</p>
            <p className="text-4xl font-semibold mb-1" style={{ fontFamily }}>$0</p>
            <p className="text-neutral-500 text-sm mb-8">Forever free, no credit card required.</p>
            <ul className="space-y-3 text-sm text-neutral-700">
              {[
                "Up to 20 active tasks",
                "Up to 15 notes",
                "20 clipboard items",
                "5 focus sessions per day",
                "Basic statistics",
                "Light & dark themes",
              ].map((f) => (
                <li key={f} className="flex items-center gap-3">
                  <Check className="w-4 h-4 text-neutral-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <a href={APP_STORE_URL} target="_blank" rel="noreferrer">
              <Button variant="outline" className="mt-8 w-full border-neutral-300 text-neutral-800 hover:bg-neutral-50">
                Download Free
              </Button>
            </a>
          </div>

          {/* Pro tier */}
          <div className="rounded-[28px] border border-black bg-black text-white p-8 shadow-xl relative overflow-hidden">
            <div className="absolute top-5 right-5 bg-white text-black text-xs font-semibold px-3 py-1 rounded-full" style={{ fontFamily }}>
              7-day free trial
            </div>
            <p className="text-sm uppercase tracking-widest text-neutral-400 mb-3" style={{ fontFamily }}>Pro</p>
            <p className="text-4xl font-semibold mb-1" style={{ fontFamily }}>$12.99</p>
            <p className="text-neutral-400 text-sm mb-8">per year · cancel any time</p>
            <ul className="space-y-3 text-sm text-neutral-300">
              {[
                "Everything in Free",
                "Unlimited tasks, notes & clipboard",
                "Unlimited focus sessions",
                "iCloud sync across Mac & iPhone",
                "Menu bar widget",
                "Custom themes & Liquid Glass",
                "Advanced statistics & streaks",
                "Keyboard shortcuts",
                "Data export",
                "Priority support",
              ].map((f) => (
                <li key={f} className="flex items-center gap-3">
                  <Check className="w-4 h-4 text-white flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <a href={APP_STORE_URL} target="_blank" rel="noreferrer">
              <Button className="mt-8 w-full bg-white text-black hover:bg-neutral-100">
                Try Free for 7 Days
              </Button>
            </a>
          </div>
        </div>
      </div>

      {/* ── FAQ ── */}
      <div
        id="faq"
        className="fade-in-up fade-delay-3 mt-24 scroll-mt-32 w-full max-w-2xl mx-auto px-6 text-center mb-10"
      >
        <h2 className="text-4xl font-medium mb-12" style={{ fontFamily }}>Frequently asked questions.</h2>
        <div className="rounded-[28px] border border-neutral-200 bg-white px-8 py-2 shadow-sm text-left">
          {faqs.map((item) => (
            <FaqItem key={item.q} q={item.q} a={item.a} />
          ))}
        </div>
      </div>
    </section>
  )
}

export default HomePage
