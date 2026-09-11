const fontFamily =
  '"SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Helvetica Neue",Helvetica,Arial,sans-serif'

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div className="mb-10">
    <h2 className="text-xl font-semibold mb-3 text-neutral-900" style={{ fontFamily }}>{title}</h2>
    <div className="text-neutral-600 text-sm leading-relaxed space-y-3">{children}</div>
  </div>
)

const PrivacyPolicy = () => {
  return (
    <main className="min-h-screen pt-32 pb-24 px-6 max-w-3xl mx-auto" style={{ fontFamily }}>
      <h1 className="text-4xl font-semibold mb-2 text-neutral-900">Privacy Policy</h1>
      <p className="text-sm text-neutral-400 mb-12">Last updated: March 24, 2026</p>

      <Section title="Overview">
        <p>
          OneFocus ("we", "our", or "us") is built with privacy as a first principle. This policy
          explains what data OneFocus collects, how it is used, and the choices you have. The short
          version: your personal content (tasks, notes, clipboard history, focus sessions) never
          leaves your device and iCloud account. We do not sell your data. We do not run ads.
        </p>
      </Section>

      <Section title="Information We Collect">
        <p>
          <strong className="text-neutral-800">Account information.</strong> When you create an
          OneFocus account, we collect your email address and display name via Supabase Auth. This
          is used solely for authentication and to associate your subscription status with your
          account.
        </p>
        <p>
          <strong className="text-neutral-800">Subscription status.</strong> When you purchase
          OneFocus Pro, Apple processes the payment. We receive a cryptographically verified
          transaction receipt from Apple's StoreKit framework and store a boolean flag
          (subscribed / not subscribed) in our Supabase database. We never receive or store your
          payment card details.
        </p>
        <p>
          <strong className="text-neutral-800">App content.</strong> Your tasks, notes, clipboard
          history, and focus session data are stored locally on your device and, if you enable
          iCloud Sync, in your private iCloud account. This data is never transmitted to our
          servers.
        </p>
        <p>
          <strong className="text-neutral-800">Crash and diagnostic data.</strong> If you opt in
          to sharing analytics with Apple, Apple may share anonymized crash reports with us through
          App Store Connect. This data contains no personally identifiable information.
        </p>
      </Section>

      <Section title="How We Use Your Information">
        <p>We use the information we collect only to:</p>
        <ul className="list-disc list-inside space-y-1 pl-2">
          <li>Authenticate you and maintain your session.</li>
          <li>Verify and enforce your Pro subscription entitlement.</li>
          <li>Send transactional emails (e.g. password reset) via Supabase Auth.</li>
          <li>Respond to support requests you initiate.</li>
        </ul>
        <p>We do not use your data for advertising, profiling, or any third-party analytics.</p>
      </Section>

      <Section title="iCloud Sync">
        <p>
          When iCloud Sync is enabled, your app content is stored in your personal iCloud private
          database using Apple's CloudKit framework. This data is governed by Apple's iCloud Terms
          and Conditions and Privacy Policy. We do not have access to your iCloud data.
        </p>
      </Section>

      <Section title="Data Sharing">
        <p>
          We do not sell, rent, or share your personal information with third parties except in the
          following limited circumstances:
        </p>
        <ul className="list-disc list-inside space-y-1 pl-2">
          <li>
            <strong className="text-neutral-800">Supabase</strong> — our backend provider stores
            your account email and subscription flag. Supabase is SOC 2 Type II certified and
            processes data in accordance with GDPR.
          </li>
          <li>
            <strong className="text-neutral-800">Apple</strong> — processes in-app purchases and
            may share anonymized diagnostic data as described above.
          </li>
          <li>
            <strong className="text-neutral-800">Legal requirements</strong> — we may disclose
            information if required by law or to protect the rights and safety of our users.
          </li>
        </ul>
      </Section>

      <Section title="Data Retention">
        <p>
          Your account data is retained for as long as your account is active. You may delete your
          account at any time from the Account Settings screen inside OneFocus. Deleting your
          account permanently removes your email address and subscription record from our servers
          within 30 days.
        </p>
      </Section>

      <Section title="Children's Privacy">
        <p>
          OneFocus is not directed at children under the age of 13. We do not knowingly collect
          personal information from children under 13. If you believe a child has provided us with
          personal information, please contact us and we will delete it promptly.
        </p>
      </Section>

      <Section title="Your Rights">
        <p>
          Depending on your location, you may have the right to access, correct, or delete the
          personal data we hold about you. To exercise any of these rights, please contact us at
          the email address below.
        </p>
      </Section>

      <Section title="Changes to This Policy">
        <p>
          We may update this Privacy Policy from time to time. We will notify you of material
          changes by updating the "Last updated" date at the top of this page. Continued use of
          OneFocus after changes constitutes acceptance of the revised policy.
        </p>
      </Section>

      <Section title="Contact">
        <p>
          If you have questions about this Privacy Policy or your data, please contact us at{" "}
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

export default PrivacyPolicy
