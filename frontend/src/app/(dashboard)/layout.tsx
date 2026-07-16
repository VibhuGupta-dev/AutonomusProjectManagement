import { UserButton } from "@clerk/nextjs";
import { LayoutDashboard, Settings, Layers } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-[#0A0A0A] text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 bg-[#0A0A0A] flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-white/10">
          <Layers className="w-6 h-6 text-purple-500 mr-2" />
          <span className="font-semibold tracking-tight">AutonomousPM</span>
        </div>
        
        
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/projects" className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5 text-white">
            <LayoutDashboard className="w-4 h-4" />
            <span className="text-sm font-medium">Projects</span>
          </Link>
          <Link href="/settings" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 text-neutral-400 hover:text-white transition-colors">
            <Settings className="w-4 h-4" />
            <span className="text-sm font-medium">Settings</span>
          </Link>
        </nav>
        
        <div className="p-4 border-t border-white/10 flex items-center gap-3">
          <UserButton afterSignOutUrl="/" appearance={{ elements: { userButtonAvatarBox: "w-8 h-8" } }} />
          <div className="text-sm font-medium text-neutral-300">My Account</div>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-[#0A0A0A]">
        {children}
      </main>
    </div>
  );
}
