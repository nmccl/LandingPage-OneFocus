const fontFamily =
  '"SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Helvetica,Arial,sans-serif'

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div className="mb-10">
    <h2 className="text-xl font-semibold mb-3 text-neutral-900" style={{ fontFamily }}>{title}</h2>
    <div className="text-neutral-600 text-sm leading-relaxed space-y-3">{children}</div>
  </div>
)

const TermsOfUse = () => {
  return (
    <main className="min-h-screen pt-32 pb-24 px-6 max-w-3xl mx-auto" style={{ fontFamily }}>
      <h1 className="text-4xl font-semibold mb-2 text-neutral-900">Terms of Use</h1>
      <p className="text-sm text-neutral-400 mb-12">Last updated: March 24, 2026</p>

      <Section title="Agreement to Terms">
        <p>
          By downloading, installing, or using OneFocus ("the App"), you agree to be bound by
          these Terms of Use ("Terms"). If you do not agree to these Terms, do not use the App.
          These Terms apply to all users of OneFocus, including free and Pro subscribers.
        </p>
      </Section>

      <Section title="License">
        <p>
          Subject to these Terms, Noah McClung ("we", "us") grants you a limited, non-exclusive,
          non-transferable, revocable license to download and use OneFocus on Apple devices that
          you own or control, solely for your personal, non-commercial purposes.
        </p>
        <p>
          You may not copy, modify, distribute, sell, or lease any part of the App, nor may you
          reverse engineer or attempt to extract the source code of the App.
        </p>
      </Section>

      <Section title="OneFocus Pro Subscription">
        <p>
          OneFocus Pro is an auto-renewable subscription available for $12.99 per year. A 7-day
          free trial is offered to new subscribers. Your subscription will automatically renew
          unless cancelled at least 24 hours before the end of the current period.
        </p>
        <p>
          Payment is charged to your Apple ID account at confirmation of purchase. You can manage
          and cancel your subscription at any time from System Settings → Apple ID → Subscriptions
          (macOS) or Settings → Apple ID → Subscriptions (iOS).
        </p>
        <p>
          Refunds are handled by Apple in accordance with their standard refund policy. We do not
          process refunds directly.
        </p>
      </Section>

      <Section title="Acceptable Use">
        <p>You agree not to use OneFocus to:</p>
        <ul className="list-disc list-inside space-y-1 pl-2">
          <li>Violate any applicable law or regulation.</li>
          <li>Infringe the intellectual property rights of any third party.</li>
          <li>Transmit any malicious code, viruses, or harmful data.</li>
          <li>Attempt to gain unauthorized access to our systems or other users' accounts.</li>
        </ul>
      </Section>

      <Section title="User Content">
        <p>
          All content you create within OneFocus (tasks, notes, clipboard history, focus data)
          remains yours. We do not claim any ownership over your content. You are solely
          responsible for the content you store in the App.
        </p>
      </Section>

      <Section title="Intellectual Property">
        <p>
          The OneFocus name, logo, design, and all related materials are the intellectual property
          of Noah McClung. Nothing in these Terms grants you any right to use our trademarks,
          trade names, or logos without our prior written consent.
        </p>
      </Section>

      <Section title="Disclaimer of Warranties">
        <p>
          OneFocus is provided "as is" and "as available" without warranties of any kind, either
          express or implied, including but not limited to implied warranties of merchantability,
          fitness for a particular purpose, and non-infringement. We do not warrant that the App
          will be uninterrupted, error-free, or free of viruses or other harmful components.
        </p>
      </Section>

      <Section title="Limitation of Liability">
        <p>
          To the maximum extent permitted by applicable law, Noah McClung shall not be liable for
          any indirect, incidental, special, consequential, or punitive damages, including loss of
          data, arising out of or in connection with your use of OneFocus, even if we have been
          advised of the possibility of such damages.
        </p>
        <p>
          Our total liability to you for any claims arising under these Terms shall not exceed the
          amount you paid for OneFocus Pro in the 12 months preceding the claim.
        </p>
      </Section>

      <Section title="Termination">
        <p>
          We reserve the right to suspend or terminate your access to OneFocus at any time, with
          or without notice, if you violate these Terms. Upon termination, your license to use the
          App will immediately cease.
        </p>
      </Section>

      <Section title="Changes to These Terms">
        <p>
          We may update these Terms from time to time. We will notify you of material changes by
          updating the "Last updated" date at the top of this page. Continued use of OneFocus
          after changes constitutes acceptance of the revised Terms.
        </p>
      </Section>

      <Section title="Governing Law">
        <p>
          These Terms are governed by the laws of the State of Nevada, United States, without
          regard to its conflict of law provisions.
        </p>
      </Section>

      <Section title="Contact">
        <p>
          If you have questions about these Terms, please contact us at{" "}
          <a
            href="mailto:support@noahmcclung.com"
            className="text-neutral-900 underline underline-offset-2 hover:text-neutral-600"
          >
            support@noahmcclung.com
          </a>
          .
        </p>
      </Section>
    </main>
  )
}

export default TermsOfUse
