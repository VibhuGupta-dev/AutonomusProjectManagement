"use client";

import { motion } from "framer-motion";
import { ArrowRight, Bot, Code, Cpu, LayoutDashboard, Layers, Zap, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white selection:bg-purple-500/30 font-sans">
      {/* Navigation */}
      <nav className="fixed top-0 w-full border-b border-white/10 bg-[#0A0A0A]/80 backdrop-blur-md z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-purple-500" />
            <span className="font-semibold text-lg tracking-tight">AutonomousPM</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-neutral-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/projects" className="text-sm font-medium text-neutral-300 hover:text-white transition-colors">Log in</Link>
            <Link href="/projects" className="text-sm font-medium bg-white text-black px-4 py-2 rounded-full hover:bg-neutral-200 transition-colors">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <main className="pt-32 pb-16 px-6">
        {/* HERO SECTION */}
        <section className="relative max-w-5xl mx-auto text-center py-20">
          {/* Background Glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-purple-600/20 blur-[120px] rounded-full pointer-events-none" />
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 backdrop-blur-md mb-8 text-sm text-neutral-300">
              <SparklesIcon className="w-4 h-4 text-purple-400" />
              <span>Introducing AI-driven Sprint Planning</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent">
              Product management,<br />completely automated.
            </h1>
            
            <p className="text-lg md:text-xl text-neutral-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Upload your raw requirements. Our AI agents extract goals, generate INVEST-ready user stories, estimate points, and plan your sprints in seconds.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/projects" className="h-12 px-8 rounded-full bg-white text-black font-medium hover:scale-105 transition-transform flex items-center justify-center gap-2">
                Start Building Free <ArrowRight className="w-4 h-4" />
              </Link>
              <Link href="#pricing" className="h-12 px-8 rounded-full border border-white/10 bg-white/5 backdrop-blur-md font-medium hover:bg-white/10 transition-colors flex items-center justify-center gap-2">
                Book a Demo
              </Link>
            </div>
          </motion.div>
        </section>

        {/* FEATURES SECTION */}
        <section id="features" className="max-w-7xl mx-auto py-32">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4">Everything you need to ship faster.</h2>
            <p className="text-neutral-400">A complete suite of AI agents working together.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            <FeatureCard 
              icon={<Layers className="text-blue-400" />}
              title="Story Generation"
              description="Transforms raw PRDs into perfectly formatted Agile user stories using the INVEST framework."
            />
            <FeatureCard 
              icon={<Zap className="text-yellow-400" />}
              title="Fibonacci Estimation"
              description="Automatically assigns story points based on complexity, risk, and technical effort."
            />
            <FeatureCard 
              icon={<LayoutDashboard className="text-green-400" />}
              title="Sprint Planning"
              description="Intelligently groups stories into 2-week sprints, respecting dependencies and a 40-point capacity."
            />
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section id="how-it-works" className="max-w-5xl mx-auto py-32">
          <div className="flex flex-col md:flex-row items-center gap-16">
            <div className="flex-1">
              <h2 className="text-3xl font-bold tracking-tight mb-6">A seamless pipeline from document to Jira.</h2>
              <div className="space-y-8">
                <Step number="01" title="Upload Requirements" desc="Drag and drop your PDF or DOCX file." />
                <Step number="02" title="AI Agents Run" desc="A LangGraph pipeline analyzes and estimates everything." />
                <Step number="03" title="Sync to Jira" desc="One click exports all epics and stories to your active board." />
              </div>
            </div>
            <div className="flex-1 w-full relative">
              {/* Glassmorphism Mockup */}
              <div className="aspect-square rounded-2xl border border-white/10 bg-gradient-to-tr from-white/5 to-white/0 backdrop-blur-xl p-8 relative overflow-hidden shadow-2xl">
                 <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 blur-[80px] rounded-full" />
                 <div className="space-y-4 relative z-10">
                    <div className="h-8 w-32 bg-white/10 rounded-md animate-pulse" />
                    <div className="h-24 w-full bg-white/5 rounded-lg border border-white/10 p-4">
                       <div className="h-4 w-1/2 bg-white/20 rounded mb-2" />
                       <div className="h-3 w-3/4 bg-white/10 rounded" />
                    </div>
                    <div className="h-24 w-full bg-white/5 rounded-lg border border-white/10 p-4">
                       <div className="h-4 w-1/3 bg-white/20 rounded mb-2" />
                       <div className="h-3 w-2/3 bg-white/10 rounded" />
                    </div>
                 </div>
              </div>
            </div>
          </div>
        </section>

        {/* PRICING */}
        <section id="pricing" className="max-w-5xl mx-auto py-32">
           <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4">Simple, transparent pricing.</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
             <PricingCard 
                title="Starter" 
                price="Free" 
                features={["Up to 3 projects", "Basic story generation", "PDF exports"]} 
             />
             <PricingCard 
                title="Pro" 
                price="$49/mo" 
                features={["Unlimited projects", "Jira Cloud Sync", "Advanced Sprint Planning", "Priority Support"]} 
                highlight 
             />
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="max-w-3xl mx-auto py-32">
           <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight mb-4">Frequently Asked Questions</h2>
          </div>
          <div className="space-y-4">
             <FaqItem question="How accurate are the story points?" answer="Our Estimation Agent uses a fine-tuned LangGraph workflow that strictly maps to the Fibonacci sequence, analyzing complexity, risk, and dependencies to provide highly accurate estimates." />
             <FaqItem question="Can it sync with my existing Jira board?" answer="Yes. The platform seamlessly authenticates with Jira Cloud via OAuth and automatically creates Epics, Stories, and Sprint assignments on your active boards." />
             <FaqItem question="What document formats are supported?" answer="We currently support uploading PDF, DOCX, and TXT files for requirements analysis." />
          </div>
        </section>

        {/* CTA */}
        <section className="max-w-4xl mx-auto py-32 text-center">
          <div className="p-12 rounded-3xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent relative overflow-hidden">
             <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-purple-500/10 blur-[100px] pointer-events-none" />
             <h2 className="text-4xl font-bold tracking-tight mb-6 relative z-10">Ready to automate your workflow?</h2>
             <Link href="/projects" className="inline-flex items-center justify-center h-12 px-8 rounded-full bg-white text-black font-medium hover:scale-105 transition-transform relative z-10">
                Get Started for Free
              </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 py-12 text-center text-neutral-500 text-sm">
        <p>© 2026 AutonomousPM. All rights reserved.</p>
      </footer>
    </div>
  );
}

// Subcomponents
function SparklesIcon(props: any) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
    </svg>
  );
}

function FeatureCard({ icon, title, description }: any) {
  return (
    <div className="p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors">
      <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-6 border border-white/10">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-neutral-400 leading-relaxed">{description}</p>
    </div>
  );
}

function Step({ number, title, desc }: any) {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-8 h-8 rounded-full border border-white/20 flex items-center justify-center text-sm font-mono text-neutral-400">
        {number}
      </div>
      <div>
        <h4 className="text-lg font-semibold mb-1">{title}</h4>
        <p className="text-neutral-400">{desc}</p>
      </div>
    </div>
  );
}

function PricingCard({ title, price, features, highlight }: any) {
  return (
    <div className={`p-8 rounded-3xl border ${highlight ? 'border-purple-500/50 bg-purple-500/5' : 'border-white/10 bg-white/5'} relative`}>
      {highlight && <div className="absolute top-0 right-8 -translate-y-1/2 px-3 py-1 bg-purple-500 text-white text-xs font-semibold rounded-full">Most Popular</div>}
      <h3 className="text-xl font-medium mb-2">{title}</h3>
      <div className="text-4xl font-bold mb-8">{price}</div>
      <ul className="space-y-4 mb-8">
        {features.map((f: string, i: number) => (
          <li key={i} className="flex items-center gap-3 text-neutral-300">
            <CheckCircle2 className="w-5 h-5 text-purple-500" />
            {f}
          </li>
        ))}
      </ul>
      <button className={`w-full h-12 rounded-xl font-medium transition-colors ${highlight ? 'bg-white text-black hover:bg-neutral-200' : 'bg-white/10 text-white hover:bg-white/20'}`}>
        Select {title}
      </button>
    </div>
  );
}

function FaqItem({ question, answer }: any) {
  return (
    <div className="p-6 rounded-2xl border border-white/10 bg-white/5">
      <h4 className="text-lg font-medium mb-2">{question}</h4>
      <p className="text-neutral-400 leading-relaxed">{answer}</p>
    </div>
  );
}
