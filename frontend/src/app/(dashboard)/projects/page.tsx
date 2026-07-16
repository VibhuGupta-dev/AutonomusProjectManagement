"use client";

import { useEffect, useState } from "react";
import { useApi } from "@/lib/api";
import { Plus, Folder, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function ProjectsPage() {
  const { request } = useApi();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await request("/projects/");
        setProjects(data);
      } catch (err) {
        console.error("Failed to load projects", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [request]);

  const createProject = async () => {
    const name = prompt("Project Name:");
    if (!name) return;
    try {
      const data = await request("/projects/", {
        method: "POST",
        body: JSON.stringify({ name, description: "New AI managed project" })
      });
      setProjects([data, ...projects]);
    } catch (err) {
      alert("Error creating project");
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Your Projects</h1>
          <p className="text-neutral-400">Manage your AI-generated product lifecycles.</p>
        </div>
        <button 
          onClick={createProject}
          className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-neutral-200 transition-colors flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Project
        </button>
      </div>

      {loading ? (
        <div className="text-neutral-500 animate-pulse">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="p-12 text-center border border-white/10 rounded-2xl bg-white/5 border-dashed">
          <Folder className="w-12 h-12 text-neutral-500 mx-auto mb-4" />
          <h3 className="text-xl font-medium mb-2">No projects yet</h3>
          <p className="text-neutral-400 mb-6">Create a project to start analyzing requirements.</p>
          <button onClick={createProject} className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg font-medium transition-colors">
            Create your first project
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(p => (
            <Link href={`/projects/${p.id}`} key={p.id}>
              <div className="p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors group cursor-pointer relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/0 via-purple-500/0 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                <h3 className="text-lg font-semibold mb-2">{p.name}</h3>
                <p className="text-sm text-neutral-400 line-clamp-2 mb-6">{p.description || "No description"}</p>
                <div className="flex items-center text-sm font-medium text-purple-400">
                  Open Project <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
