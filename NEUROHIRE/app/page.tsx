"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Logo } from "@/components/logo"

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem("neurohire_token")
    if (token) {
      router.push("/dashboard")
    }
  }, [router])

  return (
    <main className="min-h-screen relative bg-black text-white overflow-hidden">
      {/* Enhanced space background */}
      <div className="space-bg"></div>

      {/* Stars layers */}
      <div className="stars-small absolute inset-0"></div>
      <div className="stars-medium absolute inset-0"></div>
      <div className="stars-large absolute inset-0"></div>
      <div className="stars-twinkle"></div>

      {/* Nebula effect */}
      <div className="nebula"></div>

      {/* Galaxy */}
      <div className="galaxy"></div>

      {/* Shooting stars */}
      <div className="shooting-star"></div>
      <div className="shooting-star"></div>
      <div className="shooting-star"></div>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto p-6 md:p-24 space-y-8">
        {/* Logo */}
        <Logo />

        <section className="space-y-4 text-center">
          <h1 className="text-5xl font-bold tracking-tight text-white">NeuroHire</h1>
          <p className="text-gray-300 text-xl max-w-3xl mx-auto">
            AI-Powered Recruitment Platform for Finding the Perfect Match
          </p>
        </section>

        <div className="flex flex-col items-center justify-center space-y-6 mt-8">
          <div className="text-center max-w-2xl">
            <p className="text-gray-300 text-lg mb-8">
              Our advanced AI analyzes resumes, job descriptions, and social profiles to find the best candidates for your open positions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                asChild
                className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-lg py-6 px-8"
              >
                <Link href="/auth/login">Sign In</Link>
              </Button>
              <Button 
                asChild
                variant="outline"
                className="border-purple-500/30 text-purple-300 hover:bg-purple-900/30 text-lg py-6 px-8"
              >
                <Link href="/dashboard">Browse as Guest</Link>
              </Button>
            </div>
          </div>
        </div>

        <section className="mt-16 p-8 bg-slate-900/70 backdrop-blur-md rounded-lg border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
          <h2 className="text-3xl font-semibold mb-8 text-white text-center">How NeuroHire Works</h2>
          <div className="grid gap-8 md:grid-cols-3">
            <div className="p-6 rounded-lg bg-slate-800/80 border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
              <div className="mb-3 text-2xl font-medium text-purple-300">1. Post Jobs</div>
              <p className="text-gray-300">Create detailed job postings with required skills, experience, and education.</p>
            </div>
            <div className="p-6 rounded-lg bg-slate-800/80 border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
              <div className="mb-3 text-2xl font-medium text-purple-300">2. Upload Resumes</div>
              <p className="text-gray-300">Let our AI extract and analyze information from candidate resumes automatically.</p>
            </div>
            <div className="p-6 rounded-lg bg-slate-800/80 border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
              <div className="mb-3 text-2xl font-medium text-purple-300">3. Match Candidates</div>
              <p className="text-gray-300">Get AI-powered match scores and rankings to find your perfect candidates.</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
