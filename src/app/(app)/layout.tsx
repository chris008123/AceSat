import BottomNav from "@/components/ui/BottomNav";

export default function AppShellLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto flex h-dvh max-w-md flex-col bg-paper">
      <div className="flex-1 overflow-y-auto">{children}</div>
      <BottomNav />
    </div>
  );
}
