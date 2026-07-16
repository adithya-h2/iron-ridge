import { PageHero, Section } from "@/components/marketing";
import { createPageMetadata } from "@/lib/seo";

export const metadata = createPageMetadata({
  title: "Privacy Policy",
  description: "Iron Ridge privacy policy for website visitors and customers.",
  path: "/privacy",
});

export default function PrivacyPage() {
  return (
    <>
      <PageHero title="Privacy Policy" />
      <Section>
        <div className="prose prose-steel mx-auto max-w-3xl">
          <p className="text-steel">
            Iron Ridge respects your privacy. Information submitted through our website is used
            solely to respond to inquiries and support vehicle procurement. We do not sell personal
            information to third parties.
          </p>
          <p className="mt-4 text-steel">
            For questions about data handling, contact{" "}
            <a href="mailto:privacy@ironridgevehicles.com" className="text-accent-red hover:underline">
              privacy@ironridgevehicles.com
            </a>
            .
          </p>
        </div>
      </Section>
    </>
  );
}
