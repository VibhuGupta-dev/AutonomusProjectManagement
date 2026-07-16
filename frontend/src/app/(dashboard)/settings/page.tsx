"use client";

import { useState, useEffect } from "react";
import { Save, Link as LinkIcon, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";

export default function SettingsPage() {
  const [domain, setDomain] = useState("");
  const [email, setEmail] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [boardId, setBoardId] = useState("");
  const [projectKey, setProjectKey] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [boards, setBoards] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);

  useEffect(() => {
    const credsStr = localStorage.getItem("jira_credentials");
    if (credsStr) {
      try {
        const creds = JSON.parse(credsStr);
        setDomain(creds.base_url || "");
        setEmail(creds.email || "");
        setApiToken(creds.api_token || "");
        setBoardId(creds.board_id || "");
        setProjectKey(creds.project_key || "");
      } catch (e) {}
    }
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    const creds = {
      base_url: domain,
      email: email,
      api_token: apiToken,
      board_id: boardId,
      project_key: projectKey
    };
    localStorage.setItem("jira_credentials", JSON.stringify(creds));
    // Mock save delay
    setTimeout(() => {
      setIsSaving(false);
      toast.success("Jira settings saved securely to your browser!");
    }, 600);
  };

  const fetchJiraDetails = async () => {
    if (!domain || !email || !apiToken) {
      toast.error("Please enter Domain, Email, and API Token first.");
      return;
    }
    setIsFetching(true);
    const creds = { base_url: domain, email: email, api_token: apiToken };
    
    try {
      const [projectsRes, boardsRes] = await Promise.all([
        fetch("http://localhost:8001/api/v1/jira/projects", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(creds)
        }),
        fetch("http://localhost:8001/api/v1/jira/boards", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(creds)
        })
      ]);

      if (!projectsRes.ok || !boardsRes.ok) throw new Error("Failed to fetch from Jira. Check your credentials.");
      
      const pData = await projectsRes.json();
      const bData = await boardsRes.json();
      
      setProjects(pData.projects || []);
      setBoards(bData.boards || []);
      toast.success("Jira Projects and Boards fetched successfully!");
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
        <p className="text-neutral-400">Manage your workspace integrations and preferences.</p>
      </div>

      <div className="bg-[#111] border border-white/10 rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-white/10 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
            <LinkIcon className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Jira Integration</h2>
            <p className="text-sm text-neutral-400">Connect your account to export sprints directly to Jira.</p>
          </div>
        </div>
        
        <form onSubmit={handleSave} className="p-6 space-y-6">
          <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-4 flex gap-3 text-sm text-blue-200">
            <AlertCircle className="w-5 h-5 text-blue-400 shrink-0" />
            <p>You can generate a Jira API token from your Atlassian account security settings. These credentials are stored securely and only used for your exports.</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">Jira Domain</label>
              <input 
                type="url" 
                placeholder="https://your-company.atlassian.net"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full bg-[#1a1a1a] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">Atlassian Email</label>
              <input 
                type="email" 
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#1a1a1a] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">API Token</label>
              <input 
                type="password" 
                placeholder="Paste your Jira API token here"
                value={apiToken}
                onChange={(e) => setApiToken(e.target.value)}
                className="w-full bg-[#1a1a1a] border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
              />
            </div>

            <div className="pt-2">
              <button 
                type="button" 
                onClick={fetchJiraDetails}
                disabled={isFetching}
                className="bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 px-4 py-2 rounded-lg font-medium transition-colors text-sm flex items-center gap-2"
              >
                {isFetching ? "Fetching..." : "Connect & Fetch Projects/Boards"}
              </button>
            </div>

            {projects.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1.5">Select Jira Project</label>
                <select 
                  value={projectKey}
                  onChange={(e) => setProjectKey(e.target.value)}
                  className="w-full bg-[#1a1a1a] border border-white/10 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500"
                >
                  <option value="">-- Select Project --</option>
                  {projects.map(p => (
                    <option key={p.key} value={p.key}>{p.name} ({p.key})</option>
                  ))}
                </select>
              </div>
            )}

            {boards.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1.5">Select Jira Board (Scrum)</label>
                <select 
                  value={boardId}
                  onChange={(e) => setBoardId(e.target.value)}
                  className="w-full bg-[#1a1a1a] border border-white/10 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500"
                >
                  <option value="">-- Select Board --</option>
                  {boards.map(b => (
                    <option key={b.id} value={b.id}>{b.name} ({b.type})</option>
                  ))}
                </select>
                <p className="text-xs text-neutral-500 mt-1.5">Only Scrum boards are supported for creating sprints.</p>
              </div>
            )}
          </div>

          <div className="pt-4 flex justify-end">
            <button 
              type="submit"
              disabled={isSaving}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white px-6 py-2.5 rounded-lg font-medium transition-all flex items-center gap-2 shadow-lg shadow-purple-500/20"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
