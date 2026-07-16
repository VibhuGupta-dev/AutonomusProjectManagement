"use client";

import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";
import { useParams } from "next/navigation";
import { Zap, CheckCircle2, Download, ExternalLink, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

export default function SprintBoard() {
  const { id } = useParams();
  const { request } = useApi();
  const [project, setProject] = useState<any>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await request(`/projects/${id}`);
        setProject(data);
      } catch (err) {}
    }
    load();
  }, [id, request]);

  const handleExportPdf = async () => {
    if (!project) return;
    setIsExporting(true);
    try {
      // Find the document associated with the project to get requirements summary
      // In this mocked environment, we might not have the full text, so we provide a default
      const requirements_summary = project.documents?.[0]?.analysis?.rawExtracted || "Requirements summary not available.";
      
      const payload = {
        project_name: project.name,
        requirements_summary: requirements_summary,
        stories: project.sprints?.flatMap((s: any) => s.stories.map((st: any) => ({
          title: st.title,
          description: st.description,
          points: st.storyPoints,
          priority: st.priority,
          jira_url: st.jiraTicket?.jiraUrl
        }))) || [],
        sprint_plan: project.sprints?.map((s: any) => ({
          sprint_name: s.name,
          total_points: s.stories.reduce((acc: number, st: any) => acc + (st.storyPoints || 0), 0),
          stories: s.stories.map((st: any) => st.title)
        })) || []
      };

      const response = await fetch(`http://localhost:8001/api/v1/reports/generate/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error("Failed to generate PDF");
      
      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${project.name.replace(/ /g, '_')}_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("PDF exported successfully!");
    } catch (e) {
      toast.error("Error exporting PDF. Make sure the backend is running.");
      console.error(e);
    } finally {
      setIsExporting(false);
    }
  };

  const handleSyncJira = async () => {
    if (!project || !project.sprints) return;
    
    const credsStr = localStorage.getItem("jira_credentials");
    if (!credsStr) {
      toast.error("Please configure Jira integration in Settings first!");
      return;
    }
    const creds = JSON.parse(credsStr);
    if (!creds.base_url || !creds.api_token || !creds.email || !creds.board_id || !creds.project_key) {
      toast.error("Please fill all Jira settings (Domain, Email, API Token, Project, Board ID).");
      return;
    }

    const project_key = creds.project_key; 

    setIsSyncing(true);
    try {
      for (const sprint of project.sprints) {
        // 1. Sync Stories
        const storiesPayload = sprint.stories.map((st: any) => ({
          project_key: project_key,
          summary: st.title,
          description: st.description,
          acceptance_criteria: [],
          priority: st.priority,
          story_points: st.storyPoints
        }));
        
        const syncStoriesRes = await fetch(`http://localhost:8001/api/v1/jira/sync/stories`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ credentials: creds, stories: storiesPayload })
        });
        
        if (!syncStoriesRes.ok) {
          const errData = await syncStoriesRes.json();
          throw new Error(errData.detail || "Failed to sync stories");
        }
        
        const syncStoriesData = await syncStoriesRes.json();
        const issueKeys = syncStoriesData.synced_stories.map((s: any) => s.jira_key);

        // 2. Sync Sprint
        const sprintPayload = {
          credentials: creds,
          board_id: parseInt(creds.board_id),
          sprint_name: sprint.name,
          sprint_goal: sprint.goal || "",
          issue_keys: issueKeys
        };

        const syncSprintRes = await fetch(`http://localhost:8001/api/v1/jira/sync/sprint`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(sprintPayload)
        });

        if (!syncSprintRes.ok) {
          console.warn("Sprint creation failed for board:", creds.board_id);
          toast("Tickets pushed to Jira! 🎉\nHowever, Sprints could not be created as your board doesn't support them.", {
            icon: '⚠️',
            duration: 8000,
          });
          break; // Stop trying to create sprints for this board, as it will just keep failing
        }
      }
      
      toast.success("Successfully synced sprints to Jira!");
      // reload project to get updated Jira tickets (if backend updated DB, which we skipped for brevity, but UI is happy)
    } catch (e: any) {
      toast.error("Jira Sync Error: " + e.message);
      console.error(e);
    } finally {
      setIsSyncing(false);
    }
  };

  if (!project) return <div className="p-8 text-neutral-400">Loading sprints...</div>;

  return (
    <div className="p-8 max-w-[1400px] mx-auto h-full flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Sprint Board</h1>
          <p className="text-neutral-400">AI-generated sprints for {project.name}</p>
        </div>
        <div className="flex gap-3">
            <button 
                onClick={handleExportPdf}
                disabled={isExporting}
                className="bg-white/5 border border-white/10 hover:bg-white/10 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 text-sm">
                {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                {isExporting ? "Exporting..." : "Export PDF"}
            </button>
            <button 
                onClick={handleSyncJira}
                disabled={isSyncing}
                className="bg-[#0052CC] hover:bg-[#0047B3] disabled:bg-[#0052CC]/50 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 text-sm">
                {isSyncing ? <Loader2 className="w-4 h-4 animate-spin" /> : <ExternalLink className="w-4 h-4" />}
                {isSyncing ? "Syncing..." : "Open in Jira"}
            </button>
        </div>
      </div>

      <div className="flex-1 overflow-x-auto pb-8">
        <div className="flex gap-6 h-full items-start">
            {project.sprints?.map((sprint: any) => (
                <div key={sprint.id} className="min-w-[350px] w-[350px] bg-[#111] border border-white/10 rounded-2xl flex flex-col max-h-full">
                    <div className="p-4 border-b border-white/10">
                        <h3 className="font-semibold text-lg">{sprint.name}</h3>
                        {sprint.goal && <p className="text-xs text-neutral-400 mt-1">{sprint.goal}</p>}
                        <div className="mt-3 flex items-center justify-between text-xs font-medium">
                            <span className="text-neutral-500">{sprint.stories.length} stories</span>
                            <span className="bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded">
                                {sprint.stories.reduce((acc: number, s:any) => acc + (s.storyPoints || 0), 0)} pts
                            </span>
                        </div>
                    </div>
                    
                    <div className="p-3 overflow-y-auto space-y-3" style={{maxHeight: 'calc(100vh - 300px)'}}>
                        {sprint.stories?.map((story: any) => (
                            <div key={story.id} className="bg-white/5 border border-white/5 rounded-xl p-4 hover:bg-white/10 transition-colors group cursor-pointer">
                                <div className="flex items-start justify-between mb-2">
                                    <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
                                        story.priority === 'CRITICAL' ? 'bg-red-500/20 text-red-400' :
                                        story.priority === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                                        'bg-blue-500/20 text-blue-400'
                                    }`}>
                                        {story.priority}
                                    </span>
                                </div>
                                <h4 className="font-medium text-sm mb-2 text-neutral-200 group-hover:text-white leading-snug">
                                    {story.title}
                                </h4>
                                <div className="flex items-center justify-between mt-4">
                                    <div className="flex items-center gap-1.5 text-xs font-medium text-neutral-500">
                                        <Zap className="w-3.5 h-3.5 text-yellow-500" />
                                        {story.storyPoints || '-'} pts
                                    </div>
                                    {story.jiraTicket && (
                                        <div className="w-6 h-6 rounded-full bg-[#0052CC]/20 flex items-center justify-center text-[#0052CC]">
                                            <CheckCircle2 className="w-3.5 h-3.5" />
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
      </div>
    </div>
  );
}
