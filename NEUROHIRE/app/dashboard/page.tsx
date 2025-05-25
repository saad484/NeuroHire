"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Logo } from "@/components/logo"
import { API_ENDPOINTS } from "@/app/actions"
import JobPostingForm from "@/components/job-posting-form"
import ResumeUploader from "@/components/resume-uploader"
import CandidateMatchList from "@/components/candidate-match-list"
import Swal from "sweetalert2"

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [jobs, setJobs] = useState([])
  const [candidates, setCandidates] = useState([])
  const [matches, setMatches] = useState([])
  const [authenticated, setAuthenticated] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("neurohire_token")
    if (!token) {
      router.push("/auth/login")
      return
    }
    
    setAuthenticated(true)
    
    // Fetch initial data
    fetchJobs()
    fetchCandidates()
    fetchMatches()
  }, [router])

  const fetchJobs = async () => {
    try {
      const token = localStorage.getItem("neurohire_token")
      const response = await fetch(API_ENDPOINTS.JOBS, {
        headers: {
          Authorization: `Token ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setJobs(data)
      }
    } catch (error) {
      console.error("Error fetching jobs:", error)
    }
  }

  const fetchCandidates = async () => {
    try {
      const token = localStorage.getItem("neurohire_token")
      const response = await fetch(API_ENDPOINTS.PARSED_RESUMES, {
        headers: {
          Authorization: `Token ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setCandidates(data)
      }
    } catch (error) {
      console.error("Error fetching candidates:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchMatches = async () => {
    try {
      const token = localStorage.getItem("neurohire_token")
      const response = await fetch(API_ENDPOINTS.MATCHES, {
        headers: {
          Authorization: `Token ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMatches(data)
      }
    } catch (error) {
      console.error("Error fetching matches:", error)
    }
  }

  const handleJobCreated = () => {
    fetchJobs()
  }

  const handleResumeUploaded = () => {
    fetchCandidates()
  }

  const handleLogout = () => {
    localStorage.removeItem("neurohire_token")
    router.push("/auth/login")
  }
  
  const deleteCandidate = async (candidateId: number) => {
    // Use SweetAlert2 for confirmation
    const result = await Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this deletion!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#6d28d9',  // Purple color
      cancelButtonColor: '#475569',   // Slate color
      confirmButtonText: 'Yes, delete it!',
      background: '#1e293b',          // Slate background
      color: '#f8fafc'               // Light text
    })
    
    if (!result.isConfirmed) {
      return
    }
    
    try {
      const token = localStorage.getItem("neurohire_token")
      // Use the PARSED_RESUMES endpoint which matches what we're displaying
      const response = await fetch(`${API_ENDPOINTS.PARSED_RESUMES}${candidateId}/`, {
        method: 'DELETE',
        headers: {
          Authorization: `Token ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        // Remove candidate from state
        setCandidates(candidates.filter((c: any) => c.id !== candidateId))
        
        // Show success message with SweetAlert2
        await Swal.fire({
          title: 'Deleted!',
          text: 'Candidate has been removed from the database.',
          icon: 'success',
          background: '#1e293b',
          color: '#f8fafc'
        })
      } else {
        let errorMessage = 'Unknown error occurred';
        
        try {
          const errorData = await response.json()
          console.error("Error deleting candidate:", errorData)
          errorMessage = errorData.error || errorData.message || errorMessage
        } catch (jsonError) {
          console.error("Error parsing error response:", jsonError)
        }
        
        // Show error message with SweetAlert2
        await Swal.fire({
          title: 'Error!',
          text: `Failed to delete candidate: ${errorMessage}`,
          icon: 'error',
          background: '#1e293b',
          color: '#f8fafc'
        })
      }
    } catch (error) {
      console.error("Error during delete request:", error)
      
      // Show network error message with SweetAlert2
      await Swal.fire({
        title: 'Connection Error!',
        text: 'Could not connect to the server.',
        icon: 'error',
        background: '#1e293b',
        color: '#f8fafc'
      })
    }
  }

  if (!authenticated) {
    return null // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Background effects */}
      <div className="space-bg"></div>
      <div className="stars-small absolute inset-0"></div>
      <div className="stars-medium absolute inset-0"></div>
      <div className="nebula opacity-30"></div>

      {/* Header */}
      <header className="border-b border-purple-500/20 backdrop-blur-md bg-slate-900/50 sticky top-0 z-50">
        <div className="container mx-auto py-4 px-6 flex justify-between items-center">
          <Logo />
          <Button 
            variant="outline" 
            onClick={handleLogout}
            className="border-purple-500/30 text-white bg-purple-900/30"
          >
            Logout
          </Button>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto py-8 px-6 relative z-10">
        <h1 className="text-4xl font-bold mb-8">Recruiter Dashboard</h1>

        <Tabs defaultValue="jobs" className="w-full">
          <TabsList className="mb-8 bg-slate-800/60 border border-purple-500/20">
            <TabsTrigger value="jobs">Job Postings</TabsTrigger>
            <TabsTrigger value="candidates">Candidates</TabsTrigger>
            <TabsTrigger value="matches">Matches</TabsTrigger>
          </TabsList>
          
          <TabsContent value="jobs" className="space-y-8">
            <div className="grid md:grid-cols-2 gap-8">
              <Card className="bg-slate-900/50 backdrop-blur-md border border-purple-500/20">
                <CardHeader>
                  <CardTitle className="text-white">Create Job Posting</CardTitle>
                  <CardDescription className="text-gray-400">
                    Define the requirements for your open position
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <JobPostingForm onJobCreated={handleJobCreated} />
                </CardContent>
              </Card>
              
              <Card className="bg-slate-900/50 backdrop-blur-md border border-purple-500/20">
                <CardHeader>
                  <CardTitle className="text-white">Active Job Postings</CardTitle>
                  <CardDescription className="text-gray-400">
                    {jobs.length} active positions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <p className="text-gray-400">Loading job postings...</p>
                  ) : jobs.length > 0 ? (
                    <div className="space-y-4">
                      {jobs.map((job: any) => (
                        <div 
                          key={job.id} 
                          className="p-4 rounded-lg bg-slate-800/80 border border-purple-500/20"
                        >
                          <h3 className="font-medium text-lg text-white">{job.title}</h3>
                          <p className="text-gray-300">{job.company}</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {job.required_skills.map((skill: string, i: number) => (
                              <span 
                                key={i} 
                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-900/50 text-purple-200"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No job postings yet. Create your first posting!</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="candidates" className="space-y-8">
            <Card className="bg-slate-900/50 backdrop-blur-md border border-purple-500/20">
              <CardHeader>
                <CardTitle className="text-white">Upload Candidate Resumes</CardTitle>
                <CardDescription className="text-gray-400">
                  Our AI will analyze and extract key information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResumeUploader onResumeUploaded={handleResumeUploaded} />
              </CardContent>
            </Card>
            
            <Card className="bg-slate-900/50 backdrop-blur-md border border-purple-500/20">
              <CardHeader>
                <CardTitle className="text-white">Candidate Database</CardTitle>
                <CardDescription className="text-gray-400">
                  {candidates.length} candidates in the database
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p className="text-gray-400">Loading candidates...</p>
                ) : candidates.length > 0 ? (
                  <div className="space-y-4">
                    {candidates.map((candidate: any) => (
                      <div 
                        key={candidate.id} 
                        className="relative p-4 rounded-lg bg-slate-800/80 border border-purple-500/20 group"
                      >
                        <div className="absolute top-2 right-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => deleteCandidate(candidate.id)}
                            className="bg-transparent border-red-500/50 text-red-300 hover:bg-red-900/30 rounded-sm px-3 py-1"
                            aria-label="Delete candidate"
                          >
                            Remove
                          </Button>
                        </div>
                        <h3 className="font-medium text-lg text-white">{candidate.name}</h3>
                        <p className="text-gray-300">{candidate.email}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {candidate.skills && candidate.skills.map((skill: string, i: number) => (
                            <span 
                              key={i} 
                              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900/50 text-blue-200"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400">No candidates yet. Upload resumes to get started!</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="matches">
            <Card className="bg-slate-900/50 backdrop-blur-md border border-purple-500/20">
              <CardHeader>
                <CardTitle className="text-white">Candidate-Job Matches</CardTitle>
                <CardDescription className="text-gray-400">
                  AI-powered matches between candidates and open positions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <CandidateMatchList 
                  matches={matches} 
                  jobs={jobs} 
                  candidates={candidates} 
                  onRunMatching={fetchMatches} 
                  loading={loading}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
