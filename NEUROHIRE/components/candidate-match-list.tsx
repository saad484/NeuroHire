"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { AlertCircle, Award, Zap, CheckCircle, XCircle, Info } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { API_ENDPOINTS } from "@/app/actions"
import { Tooltip } from "@/components/ui/tooltip"
import { Badge } from "@/components/ui/badge"

interface CandidateMatchListProps {
  matches: any[]
  jobs: any[]
  candidates: any[]
  onRunMatching: () => void
  loading: boolean
}

export default function CandidateMatchList({
  matches,
  jobs,
  candidates,
  onRunMatching,
  loading
}: CandidateMatchListProps) {
  const [selectedJob, setSelectedJob] = useState<number | null>(null)
  const [matchRunning, setMatchRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedMatchId, setSelectedMatchId] = useState<number | null>(null)
  const [detailedAnalysis, setDetailedAnalysis] = useState<any | null>(null)
  const [loadingDetails, setLoadingDetails] = useState(false)

  // Filter matches for the selected job
  const filteredMatches = selectedJob
    ? matches.filter(match => match.job === selectedJob || match.job_id === selectedJob).sort((a, b) => b.match_score - a.match_score)
    : matches.sort((a, b) => b.match_score - a.match_score)

  const handleRunMatching = async () => {
    if (jobs.length === 0 || candidates.length === 0) {
      setError("You need at least one job posting and one candidate to run matching")
      return
    }

    setMatchRunning(true)
    setError(null)
    setDetailedAnalysis(null)

    try {
      const token = localStorage.getItem("neurohire_token")
      const jobId = selectedJob || jobs[0].id
      
      // Call the backend to run matching algorithm for the selected job
      const response = await fetch(`${API_ENDPOINTS.JOBS}${jobId}/run-matching/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Token ${token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to run matching")
      }

      const results = await response.json()
      console.log('AI Matching Results:', results)
      
      // Refresh the matches list
      onRunMatching()
    } catch (err: any) {
      setError(err.message || "Failed to run matching")
      console.error("Matching error:", err)
    } finally {
      setMatchRunning(false)
    }
  }

  // Get job name by ID
  const getJobTitle = (jobId: number) => {
    const job = jobs.find(j => j.id === jobId)
    return job ? job.title : "Unknown Job"
  }

  // Get candidate name by ID
  const getCandidateName = (candidateId: number) => {
    const candidate = candidates.find(c => c.id === candidateId)
    return candidate ? candidate.name : "Unknown Candidate"
  }

  // Format match score as percentage
  const formatScore = (score: number) => {
    return `${Math.round(score)}%`
  }

  // Determine color class based on match score
  const getScoreColorClass = (score: number) => {
    if (score >= 80) return "from-green-500 to-emerald-500"
    if (score >= 60) return "from-blue-500 to-cyan-500"
    if (score >= 40) return "from-yellow-500 to-amber-500"
    return "from-orange-500 to-red-500"
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert className="bg-red-900/20 text-red-300 border-red-500/30">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="space-y-2">
          <label htmlFor="job-filter" className="text-sm text-gray-300">Filter by Job</label>
          <select
            id="job-filter"
            value={selectedJob || ""}
            onChange={(e) => {
              setSelectedJob(e.target.value ? parseInt(e.target.value) : null);
              setDetailedAnalysis(null); // Reset detailed analysis when job filter changes
            }}
            className="w-full md:w-64 rounded-md bg-slate-800/80 border border-purple-500/30 text-white px-3 py-2"
          >
            <option value="">All Job Postings</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title} at {job.company}
              </option>
            ))}
          </select>
        </div>
        
        <Button
          onClick={handleRunMatching}
          disabled={matchRunning || jobs.length === 0 || candidates.length === 0}
          className="bg-purple-600 hover:bg-purple-700 text-white rounded-md flex items-center gap-2"
        >
          <Zap className="h-4 w-4" />
          {matchRunning ? "Running AI..." : "Run Real-time AI Matching"}
        </Button>
      </div>
      
      {loading || matchRunning ? (
        <div className="text-center py-12">
          <div className="animate-pulse flex flex-col items-center space-y-4">
            <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
              <Zap className="h-6 w-6 text-purple-400" />
            </div>
            <div className="text-xl font-medium text-purple-300">
              {matchRunning ? "AI is analyzing candidates and job requirements..." : "Loading matches..."}
            </div>
            <Progress value={matchRunning ? 75 : 45} className="w-64 h-2 bg-slate-700">
              <div className="h-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-full" />
            </Progress>
          </div>
        </div>
      ) : filteredMatches.length > 0 ? (
        <div className="space-y-6">
          {filteredMatches.map((match) => {
            // Detect if match contains AI analysis data or error
            const hasError = match.error !== undefined;
            
            // Extract match data safely with fallbacks
            const strengths = match.strengths || (match.ai_analysis?.key_strengths) || [];
            const improvements = match.improvement_areas || (match.ai_analysis?.areas_for_improvement) || [];
            
            // Get match tier for styling
            const tier = match.tier || 
              (match.ai_analysis?.tier) ||
              (match.explanation && typeof match.explanation === 'object' ? match.explanation.tier : null) || 
              (match.match_score >= 80 ? 'excellent' : 
               match.match_score >= 60 ? 'good' : 
               match.match_score >= 40 ? 'potential' : 'weak');
            
            // Generate tier badge
            let TierBadge = null;
            if (tier === 'excellent') {
              TierBadge = (
                <Badge className="bg-green-600/80 hover:bg-green-600 text-white flex gap-1 items-center">
                  <Award className="h-3 w-3" /> Excellent Match
                </Badge>
              );
            } else if (tier === 'good') {
              TierBadge = (
                <Badge className="bg-blue-600/80 hover:bg-blue-600 text-white flex gap-1 items-center">
                  <CheckCircle className="h-3 w-3" /> Good Match
                </Badge>
              );
            } else if (tier === 'potential') {
              TierBadge = (
                <Badge className="bg-yellow-600/80 hover:bg-yellow-600 text-white flex gap-1 items-center">
                  <Info className="h-3 w-3" /> Potential Match
                </Badge>
              );
            } else {
              TierBadge = (
                <Badge className="bg-red-600/80 hover:bg-red-600 text-white flex gap-1 items-center">
                  <XCircle className="h-3 w-3" /> Weak Match
                </Badge>
              );
            }
            
            // Helper function to get candidate data
            const candidateId = match.parsed_resume || match.candidate_id;
            const candidateName = match.name || getCandidateName(candidateId);
            const jobId = match.job || match.job_id;
            const jobTitle = getJobTitle(jobId);
            
            // Handle explanation text from various sources
            let explanation = "";
            if (typeof match.explanation === 'string') {
              explanation = match.explanation;
            } else if (match.explanation?.summary) {
              explanation = match.explanation.summary;
            } else if (match.explanation?.detailed) {
              explanation = match.explanation.detailed;
            } else if (match.ai_analysis?.explanation) {
              explanation = match.ai_analysis.explanation;
            }
            
            if (hasError) {
              return (
                <div key={match.id || candidateId} className="p-4 rounded-lg bg-slate-800/90 border border-red-500/40">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="h-5 w-5 text-red-400" />
                    <h3 className="text-lg font-medium text-white">{candidateName}</h3>
                  </div>
                  <p className="text-red-300">{match.error}</p>
                  <Button 
                    className="mt-3 bg-slate-700 hover:bg-slate-600 text-white text-xs" 
                    size="sm"
                    onClick={handleRunMatching}
                  >
                    Try Again
                  </Button>
                </div>
              );
            }
            
            return (
              <div 
                key={match.id} 
                className={`p-4 rounded-lg bg-slate-800/90 border ${tier === 'excellent' ? 'border-green-500/40' : 
                               tier === 'good' ? 'border-blue-500/40' : 
                               tier === 'potential' ? 'border-yellow-500/40' : 
                               'border-red-500/40'} hover:border-purple-500/40 transition-all`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-medium text-white">
                        {candidateName}
                      </h3>
                      {TierBadge}
                    </div>
                    <p className="text-gray-400">
                      Match for {jobTitle}
                    </p>
                  </div>
                  
                  <div className="mt-2 md:mt-0 flex items-center gap-2">
                    <div className="flex items-center gap-2">
                      <Progress value={match.match_score} className="w-24 md:w-32 h-3 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r ${getScoreColorClass(match.match_score)}`} 
                          style={{ width: `${match.match_score}%` }}>
                        </div>
                      </Progress>
                      <span className="text-sm font-medium text-white">
                        {formatScore(match.match_score)}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* AI-generated Match explanation */}
                {explanation && (
                  <div className="mb-4 p-3 bg-slate-900/70 rounded border border-slate-700 text-gray-300 text-sm">
                    <div className="flex items-start gap-2">
                      <span className="text-purple-400 text-xs font-medium mt-0.5">AI ANALYSIS:</span>
                      <p>{explanation}</p>
                    </div>
                  </div>
                )}
                
                {/* Strengths and improvement areas if available */}
                {(strengths.length > 0 || improvements.length > 0) && (
                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    {strengths.length > 0 && (
                      <div className="p-3 bg-green-900/20 rounded border border-green-500/30">
                        <h4 className="text-sm font-medium text-green-300 mb-2 flex items-center gap-1">
                          <CheckCircle className="h-3.5 w-3.5" /> Key Strengths
                        </h4>
                        <ul className="text-xs text-green-100 space-y-1 pl-5 list-disc">
                          {typeof strengths === 'string' ? (
                            <li>{strengths}</li>
                          ) : (
                            strengths.map((strength: string, idx: number) => (
                              <li key={idx}>{strength}</li>
                            ))
                          )}
                        </ul>
                      </div>
                    )}
                    
                    {improvements.length > 0 && (
                      <div className="p-3 bg-yellow-900/20 rounded border border-yellow-500/30">
                        <h4 className="text-sm font-medium text-yellow-300 mb-2 flex items-center gap-1">
                          <Info className="h-3.5 w-3.5" /> Areas for Improvement
                        </h4>
                        <ul className="text-xs text-yellow-100 space-y-1 pl-5 list-disc">
                          {typeof improvements === 'string' ? (
                            <li>{improvements}</li>
                          ) : (
                            improvements.map((area: string, idx: number) => (
                              <li key={idx}>{area}</li>
                            ))
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-300 flex justify-between">
                        <span>Skills Match</span>
                        <span>{Math.round(match.skills_match?.percentage || match.skills_match?.score || 0)}%</span>
                      </h4>
                      <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r ${getScoreColorClass(match.skills_match?.percentage || match.skills_match?.score || 0)}`} 
                          style={{ width: `${match.skills_match?.percentage || match.skills_match?.score || 0}%` }}
                        ></div>
                      </div>
                    
                      <div className="mt-2">
                        <div className="text-xs text-gray-400 mb-1 font-medium">Matched Skills:</div>
                        <div className="flex flex-wrap gap-1.5">
                          {match.skills_match?.matched && match.skills_match.matched.length > 0 ? 
                            match.skills_match.matched.map((skill: string, idx: number) => (
                              <span key={idx} className="px-2 py-1 bg-green-900/30 text-green-200 text-xs rounded">
                                {skill}
                              </span>
                            )) : 
                            <span className="text-xs text-gray-500">None</span>
                          }
                        </div>
                      </div>
                      
                      <div className="mt-2">
                        <div className="text-xs text-gray-400 mb-1 font-medium">Missing Skills:</div>
                        <div className="flex flex-wrap gap-1.5">
                          {match.skills_match?.missing && match.skills_match.missing.length > 0 ? 
                            match.skills_match.missing.map((skill: string, idx: number) => (
                              <span key={idx} className="px-2 py-1 bg-red-900/30 text-red-200 text-xs rounded">
                                {skill}
                              </span>
                            )) : 
                            <span className="text-xs text-gray-500">None</span>
                          }
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-300 flex justify-between">
                        <span>Experience Match</span>
                        <span>{Math.round(match.experience_match)}%</span>
                      </h4>
                      <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r ${getScoreColorClass(match.experience_match)}`}
                          style={{ width: `${match.experience_match}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-300 flex justify-between">
                        <span>Education Match</span>
                        <span>{Math.round(match.education_match)}%</span>
                      </h4>
                      <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r ${getScoreColorClass(match.education_match)}`}
                          style={{ width: `${match.education_match}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* AI analyzed social profiles */}
                {(match.github_score > 0 || match.linkedin_score > 0) && (
                  <div className="mt-4 pt-4 border-t border-slate-700">
                    <h4 className="text-sm font-medium text-gray-300 mb-3">AI Social Profile Analysis</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      {match.github_score > 0 && (
                        <div className="space-y-2 p-3 bg-slate-900/50 rounded border border-slate-700">
                          <h5 className="text-xs font-medium text-blue-300">GitHub Profile Relevance</h5>
                          <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500"
                              style={{ width: `${match.github_score}%` }}
                            ></div>
                          </div>
                          <div className="text-xs text-blue-200 flex justify-between">
                            <span>Relevance to job</span>
                            <span>{Math.round(match.github_score)}%</span>
                          </div>
                        </div>
                      )}
                      
                      {match.linkedin_score > 0 && (
                        <div className="space-y-2 p-3 bg-slate-900/50 rounded border border-slate-700">
                          <h5 className="text-xs font-medium text-blue-300">LinkedIn Profile Relevance</h5>
                          <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-blue-600 to-blue-400"
                              style={{ width: `${match.linkedin_score}%` }}
                            ></div>
                          </div>
                          <div className="text-xs text-blue-200 flex justify-between">
                            <span>Relevance to job</span>
                            <span>{Math.round(match.linkedin_score)}%</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 bg-slate-900/50 rounded-lg border border-purple-500/20">
          <div className="flex flex-col items-center space-y-4">
            <Zap className="h-10 w-10 text-gray-500" />
            <h3 className="text-xl font-medium text-gray-300">No Matches Yet</h3>
            <p className="text-gray-400 max-w-md">
              Upload resumes and create job postings, then run the AI matching algorithm to find the best candidates.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
