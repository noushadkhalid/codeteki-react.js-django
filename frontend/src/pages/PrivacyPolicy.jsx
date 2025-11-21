export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-white py-20">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-black mb-4">Privacy Policy</h1>
          <p className="text-gray-600 text-lg">
            Last updated: {new Date().toLocaleDateString('en-AU', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>

        <div className="prose prose-lg max-w-none text-gray-800 space-y-8">
          <section>
            <h2 className="text-2xl font-bold text-black mb-4">1. Introduction</h2>
            <p>
              Codeteki ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website or use our services. This policy complies with the Australian Privacy Principles (APPs) under the Privacy Act 1988 (Cth).
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">2. Information We Collect</h2>
            <h3 className="text-xl font-semibold text-black mb-3">Personal Information</h3>
            <p>We may collect the following personal information:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Name and contact details (email address, phone number)</li>
              <li>Business information (company name, industry, role)</li>
              <li>Communication preferences and inquiry details</li>
              <li>Payment information for services rendered</li>
              <li>Website usage data and analytics information</li>
            </ul>

            <h3 className="text-xl font-semibold text-black mb-3 mt-6">Technical Information</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>IP address and browser information</li>
              <li>Device and operating system details</li>
              <li>Website navigation patterns and preferences</li>
              <li>Cookies and similar tracking technologies</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">3. How We Use Your Information</h2>
            <p>We use your personal information for the following purposes:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Providing AI workforce solutions, web development, and automation services</li>
              <li>Responding to inquiries and providing customer support</li>
              <li>Processing payments and managing service agreements</li>
              <li>Improving our services and website functionality</li>
              <li>Sending relevant updates about our services (with your consent)</li>
              <li>Complying with legal obligations and resolving disputes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">4. Information Sharing and Disclosure</h2>
            <p>We do not sell, trade, or rent your personal information. We may share your information only in the following circumstances:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Service Providers:</strong> Trusted third-party vendors who assist in delivering our services (cloud hosting, payment processing, analytics)</li>
              <li><strong>Legal Requirements:</strong> When required by Australian law, court orders, or government requests</li>
              <li><strong>Business Transfers:</strong> In the event of a merger, acquisition, or sale of business assets</li>
              <li><strong>Consent:</strong> When you have provided explicit consent for specific sharing purposes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">5. Data Security</h2>
            <p>
              We implement appropriate technical and organizational security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. This includes:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Encrypted data transmission (SSL/TLS)</li>
              <li>Secure cloud storage with access controls</li>
              <li>Regular security assessments and updates</li>
              <li>Staff training on privacy and data protection</li>
              <li>Incident response procedures for data breaches</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">6. Your Rights Under Australian Privacy Law</h2>
            <p>Under the Privacy Act 1988 (Cth), you have the following rights:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Access:</strong> Request access to your personal information we hold</li>
              <li><strong>Correction:</strong> Request correction of inaccurate or outdated information</li>
              <li><strong>Complaint:</strong> Lodge a complaint about our handling of your personal information</li>
              <li><strong>Opt-out:</strong> Unsubscribe from marketing communications at any time</li>
            </ul>
            <p className="mt-4">
              To exercise these rights, contact us at <a href="mailto:info@codeteki.au" className="text-[#f9cb07] hover:underline">info@codeteki.au</a>. We will respond within 30 days of receiving your request.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">7. Data Retention</h2>
            <p>
              We retain your personal information only for as long as necessary to fulfill the purposes outlined in this policy, comply with legal obligations, resolve disputes, and enforce agreements. Typically, this means:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Customer data: Duration of service relationship plus 7 years for tax and business records</li>
              <li>Marketing data: Until you opt-out or request deletion</li>
              <li>Website analytics: Up to 26 months</li>
              <li>Support communications: 3 years from last interaction</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">8. Cookies and Tracking Technologies</h2>
            <p>
              Our website uses cookies to enhance your browsing experience. You can control cookie settings through your browser preferences. Disabling cookies may affect website functionality.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">9. Third-Party Links</h2>
            <p>
              Our website may contain links to third-party sites. We are not responsible for the privacy practices of these external sites. We encourage you to review their privacy policies before providing personal information.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">10. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy periodically to reflect changes in our practices or legal requirements. We will notify you of significant changes by posting the updated policy on our website with a new effective date.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">11. Contact Information</h2>
            <p>If you have questions about this Privacy Policy or our data practices, please contact us:</p>
            <div className="bg-gray-50 p-6 rounded-lg mt-4">
              <p><strong>Codeteki Digital Services (Aptaa Pty Ltd)</strong></p>
              <p>Email: <a href="mailto:info@codeteki.au" className="text-[#f9cb07] hover:underline">info@codeteki.au</a></p>
              <p>Phone: <a href="tel:+61469754386" className="text-[#f9cb07] hover:underline">+61 469 754 386</a></p>
              <p>Phone: <a href="tel:+61424538777" className="text-[#f9cb07] hover:underline">+61 424 538 777</a></p>
              <p>Address: Melbourne, Victoria, Australia</p>
              <p>ABN: 20 608 158 407</p>
            </div>
            <p className="mt-4">
              If you are not satisfied with our response to a privacy complaint, you may lodge a complaint with the Office of the Australian Information Commissioner (OAIC) at <a href="https://www.oaic.gov.au" className="text-[#f9cb07] hover:underline" target="_blank" rel="noopener noreferrer">www.oaic.gov.au</a>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
