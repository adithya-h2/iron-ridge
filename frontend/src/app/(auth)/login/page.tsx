import { ComingSoonPage } from "@/components/common/coming-soon-page";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        <ComingSoonPage
          title="Login"
          description="Authentication UI will be implemented in Module 1. Auth service and context are wired."
        />
      </div>
    </main>
  );
}
