import SEOHead from "../components/SEOHead";

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-white py-20">
      <SEOHead
        title="Terms of Service | Codeteki"
        description="Read Codeteki's Terms of Service covering our AI workforce solutions, web development, and automation services under Australian law."
        page="terms-of-service"
      />
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-black mb-4">Terms of Service</h1>
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
            <h2 className="text-2xl font-bold text-black mb-4">1. Acceptance of Terms</h2>
            <p>
              By accessing and using Codeteki's website and services, you accept and agree to be bound by these Terms of Service. These terms constitute a legally binding agreement between you and Codeteki, governed by Australian law. If you do not agree to these terms, please do not use our services.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">2. Services Description</h2>
            <p>Codeteki provides the following services:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>AI Workforce Solutions:</strong> Custom AI chatbots, voice agents, and automation tools</li>
              <li><strong>Web Development:</strong> Professional website design, development, and maintenance</li>
              <li><strong>Custom Automation:</strong> Business process automation and system integration</li>
              <li><strong>Consultation Services:</strong> Strategic planning and technical advisory services</li>
            </ul>
            <p className="mt-4">
              All services are provided on a custom basis with pricing determined through individual consultation and project requirements.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">3. Service Agreements and Pricing</h2>
            <h3 className="text-xl font-semibold text-black mb-3">Project Proposals</h3>
            <p>
              All services begin with a free consultation to understand your requirements. We provide detailed project proposals outlining scope, timeline, and pricing before work commences.
            </p>
            
            <h3 className="text-xl font-semibold text-black mb-3 mt-6">Pricing and Payment</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>All prices are quoted in Australian Dollars (AUD) and include GST where applicable</li>
              <li>Payment terms are Net 30 days unless otherwise specified in the service agreement</li>
              <li>A 50% deposit may be required before project commencement</li>
              <li>Late payment fees of 1.5% per month may apply to overdue amounts</li>
              <li>We reserve the right to suspend services for non-payment</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">4. Client Responsibilities</h2>
            <p>As our client, you agree to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Provide accurate and complete information necessary for service delivery</li>
              <li>Respond to requests for information or feedback within reasonable timeframes</li>
              <li>Ensure you have necessary rights and permissions for any content provided</li>
              <li>Comply with all applicable laws and regulations in your use of our services</li>
              <li>Maintain confidentiality of any login credentials or access information</li>
              <li>Use our services only for lawful business purposes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">5. Intellectual Property Rights</h2>
            <h3 className="text-xl font-semibold text-black mb-3">Client Ownership</h3>
            <p>
              Upon full payment, you own all custom code, designs, and deliverables created specifically for your project. This includes websites, AI models trained on your data, and custom automation scripts.
            </p>
            
            <h3 className="text-xl font-semibold text-black mb-3 mt-6">Codeteki Ownership</h3>
            <p>
              We retain ownership of our proprietary methodologies, frameworks, general knowledge, and pre-existing intellectual property used in service delivery.
            </p>
            
            <h3 className="text-xl font-semibold text-black mb-3 mt-6">Third-Party Components</h3>
            <p>
              Some services may include third-party software or platforms subject to separate licensing terms. We will clearly identify these components and their respective licenses.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">6. Warranties and Disclaimers</h2>
            <h3 className="text-xl font-semibold text-black mb-3">Service Warranties</h3>
            <p>We warrant that our services will:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Be performed with reasonable skill and care</li>
              <li>Comply with agreed specifications and requirements</li>
              <li>Be free from defects for 90 days post-delivery (warranty period)</li>
            </ul>
            
            <h3 className="text-xl font-semibold text-black mb-3 mt-6">Disclaimers</h3>
            <p>
              To the extent permitted by Australian Consumer Law, we disclaim all other warranties, including implied warranties of merchantability and fitness for a particular purpose. We do not guarantee that our services will meet all your business requirements or be error-free.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">7. Limitation of Liability</h2>
            <p>
              To the maximum extent permitted by Australian law, our liability for any claim related to our services is limited to the amount paid for the specific service giving rise to the claim. We are not liable for:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Indirect, consequential, or special damages</li>
              <li>Loss of profits, revenue, or business opportunities</li>
              <li>Data loss (beyond our reasonable control)</li>
              <li>Third-party actions or content</li>
              <li>Force majeure events beyond our reasonable control</li>
            </ul>
            <p className="mt-4">
              This limitation does not apply to liability that cannot be excluded under the Australian Consumer Law, including liability for death, personal injury, or misleading and deceptive conduct.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">8. Confidentiality</h2>
            <p>
              We respect the confidential nature of your business information. We agree to:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Keep all client information confidential and secure</li>
              <li>Use client information only for service delivery purposes</li>
              <li>Not disclose client information without written consent</li>
              <li>Return or destroy confidential information upon request</li>
            </ul>
            <p className="mt-4">
              This confidentiality obligation survives termination of our service relationship.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">9. Termination</h2>
            <h3 className="text-xl font-semibold text-black mb-3">Termination by Client</h3>
            <p>
              You may terminate services at any time with 30 days written notice. You remain liable for all work completed and expenses incurred up to the termination date.
            </p>
            
            <h3 className="text-xl font-semibold text-black mb-3 mt-6">Termination by Codeteki</h3>
            <p>
              We may terminate services immediately if you breach these terms, fail to pay invoices, or engage in illegal activities. We may also terminate with 30 days notice for any other reason.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">10. Dispute Resolution</h2>
            <p>
              We are committed to resolving disputes amicably. If a dispute arises:
            </p>
            <ol className="list-decimal pl-6 space-y-2">
              <li>Contact us directly to discuss the issue</li>
              <li>If unresolved, we agree to mediation through a mutually agreed mediator</li>
              <li>Any legal proceedings will be conducted in Victoria, Australia, under Australian law</li>
            </ol>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">11. Force Majeure</h2>
            <p>
              Neither party is liable for delays or failures due to circumstances beyond reasonable control, including natural disasters, government actions, pandemics, internet outages, or third-party service failures.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">12. Updates to Terms</h2>
            <p>
              We may update these terms periodically to reflect changes in our services or legal requirements. Significant changes will be communicated via email or website notice 30 days before taking effect.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">13. Severability</h2>
            <p>
              If any provision of these terms is found to be unenforceable, the remaining provisions continue in full force and effect.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">14. Entire Agreement</h2>
            <p>
              These terms, together with any signed service agreements, constitute the entire agreement between you and Codeteki regarding our services.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-black mb-4">15. Contact Information</h2>
            <p>For questions about these Terms of Service, please contact us:</p>
            <div className="bg-gray-50 p-6 rounded-lg mt-4">
              <p><strong>Codeteki Digital Services (Aptaa Pty Ltd)</strong></p>
              <p>Email: <a href="mailto:info@codeteki.au" className="text-[#f9cb07] hover:underline">info@codeteki.au</a></p>
              <p>Phone: <a href="tel:+61469754386" className="text-[#f9cb07] hover:underline">+61 469 754 386</a></p>
              <p>Phone: <a href="tel:+61424538777" className="text-[#f9cb07] hover:underline">+61 424 538 777</a></p>
              <p>Address: Melbourne, Victoria, Australia</p>
              <p>ABN: 20 608 158 407</p>
            </div>
          </section>

          <section className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-black mb-2">Australian Consumer Law Notice</h3>
            <p className="text-sm">
              Our services come with guarantees that cannot be excluded under the Australian Consumer Law. You are entitled to a replacement or refund for a major failure and compensation for any other reasonably foreseeable loss or damage. You are also entitled to have services rectified in a reasonable time if they fail to be of acceptable quality and the failure does not amount to a major failure.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
