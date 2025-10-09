import React, { useState, useRef } from 'react';
import { Upload, FileText, Users, ArrowRight, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { apiService } from '../services/api';

const UnifiedUploadFlow = ({ onComplete }) => {
  const [step, setStep] = useState(1); // 1: Upload, 2: Processing, 3: Complete
  const [jobFiles, setJobFiles] = useState([]);
  const [resumeFiles, setResumeFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({ jobs: 0, resumes: 0, matching: 0 });
  const [errors, setErrors] = useState([]);
  
  const jobFileRef = useRef(null);
  const resumeFileRef = useRef(null);

  const handleJobFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const csvFiles = files.filter(file => file.name.toLowerCase().endsWith('.csv'));
    setJobFiles(csvFiles);
    if (csvFiles.length !== files.length) {
      setErrors(prev => [...prev, 'Only CSV files are accepted for job descriptions']);
    }
  };

  const handleResumeFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(file => {
      const ext = file.name.toLowerCase();
      return ext.endsWith('.pdf') || ext.endsWith('.docx') || ext.endsWith('.doc');
    });
    setResumeFiles(validFiles);
    if (validFiles.length !== files.length) {
      setErrors(prev => [...prev, 'Only PDF, DOC, and DOCX files are accepted for resumes']);
    }
  };

  const canProceed = jobFiles.length > 0 || resumeFiles.length > 0;

  const processUploads = async () => {
    if (!canProceed) return;
    
    setIsUploading(true);
    setStep(2);
    setErrors([]);
    
    try {
      let currentProgress = 0;
      const totalSteps = (jobFiles.length > 0 ? 2 : 0) + (resumeFiles.length > 0 ? 1 : 0) + 1; // +1 for matching
      
      // Step 1: Upload Job Descriptions (if any)
      if (jobFiles.length > 0) {
        setUploadProgress(prev => ({ ...prev, jobs: 0 }));
        
        for (let i = 0; i < jobFiles.length; i++) {
          const formData = new FormData();
          formData.append('file', jobFiles[i]);
          
          await apiService.uploadJobDescriptions(formData);
          setUploadProgress(prev => ({ ...prev, jobs: Math.round(((i + 1) / jobFiles.length) * 100) }));
        }
        currentProgress += 1;
      }

      // Step 2: Upload Resumes (if any)
      if (resumeFiles.length > 0) {
        setUploadProgress(prev => ({ ...prev, resumes: 0 }));
        
        const resumeFormData = new FormData();
        resumeFiles.forEach(file => {
          resumeFormData.append('files', file);
        });
        
        await apiService.uploadResumes(resumeFormData);
        setUploadProgress(prev => ({ ...prev, resumes: 100 }));
        currentProgress += 1;
      }

      // Step 3: Summarize Job Descriptions (if jobs were uploaded)
      if (jobFiles.length > 0) {
        setUploadProgress(prev => ({ ...prev, matching: Math.round((currentProgress / totalSteps) * 100) }));
        
        await apiService.summarizeJobs();
        currentProgress += 1;
      }

      // Step 4: Trigger Matching (if both jobs and candidates exist)
      setUploadProgress(prev => ({ ...prev, matching: Math.round((currentProgress / totalSteps) * 100) }));
      
      await apiService.triggerMatching();
      setUploadProgress(prev => ({ ...prev, matching: 100 }));

      // Complete
      setStep(3);
      setTimeout(() => {
        onComplete();
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      setErrors(['Upload failed: ' + (error.response?.data?.error || error.message)]);
      setIsUploading(false);
      setStep(1);
    }
  };

  const removeJobFile = (index) => {
    setJobFiles(files => files.filter((_, i) => i !== index));
  };

  const removeResumeFile = (index) => {
    setResumeFiles(files => files.filter((_, i) => i !== index));
  };

  if (step === 2) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card">
          <div className="text-center py-12">
            <div className="mb-8">
              <Loader className="animate-spin mx-auto mb-4 text-blue-400" size={64} />
              <h2 className="text-3xl font-bold mb-4">Processing Your Data</h2>
              <p className="text-gray-400">Please wait while we upload and analyze your files...</p>
            </div>

            <div className="space-y-6">
              {/* Job Upload Progress */}
              <div className="text-left">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Uploading Job Descriptions</span>
                  <span className="text-sm text-gray-400">{uploadProgress.jobs}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress.jobs}%` }}
                  />
                </div>
              </div>

              {/* Resume Upload Progress */}
              <div className="text-left">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Processing Resumes</span>
                  <span className="text-sm text-gray-400">{uploadProgress.resumes}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress.resumes}%` }}
                  />
                </div>
              </div>

              {/* Processing Progress */}
              <div className="text-left">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">AI Processing & Matching</span>
                  <span className="text-sm text-gray-400">{uploadProgress.matching}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress.matching}%` }}
                  />
                </div>
                {uploadProgress.matching > 0 && uploadProgress.matching < 33 && (
                  <p className="text-xs text-gray-500 mt-1">Analyzing job descriptions...</p>
                )}
                {uploadProgress.matching >= 33 && uploadProgress.matching < 66 && (
                  <p className="text-xs text-gray-500 mt-1">Summarizing requirements...</p>
                )}
                {uploadProgress.matching >= 66 && uploadProgress.matching < 100 && (
                  <p className="text-xs text-gray-500 mt-1">Matching candidates...</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 3) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card">
          <div className="text-center py-12">
            <CheckCircle className="mx-auto mb-6 text-green-400" size={80} />
            <h2 className="text-3xl font-bold mb-4 text-green-400">Upload Successful!</h2>
            <p className="text-gray-400 mb-8">
              All files processed successfully. Redirecting to results dashboard...
            </p>
            <div className="animate-pulse">
              <div className="flex items-center justify-center space-x-2 text-blue-400">
                <span>Loading Results</span>
                <Loader className="animate-spin" size={20} />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold mb-4">Upload Your Files</h2>
        <p className="text-xl text-gray-400">
          Upload job descriptions and/or candidate resumes for AI-powered matching and screening
        </p>
      </div>

      {errors.length > 0 && (
        <div className="mb-8">
          {errors.map((error, index) => (
            <div key={index} className="bg-red-500/20 border border-red-500/30 rounded-lg p-4 mb-4 flex items-center">
              <AlertCircle className="text-red-400 mr-3" size={20} />
              <span className="text-red-300">{error}</span>
            </div>
          ))}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        {/* Job Descriptions Upload */}
        <div className="card">
          <div className="text-center py-8">
            <div className="bg-blue-500/20 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <FileText size={40} className="text-blue-400" />
            </div>
            
            <h3 className="text-2xl font-bold mb-4">Job Descriptions</h3>
            <p className="text-gray-400 mb-6">
              Upload CSV file(s) containing job requirements and descriptions
            </p>
            
            <input
              ref={jobFileRef}
              type="file"
              accept=".csv"
              multiple
              onChange={handleJobFileSelect}
              className="hidden"
            />
            
            <button
              onClick={() => jobFileRef.current?.click()}
              className="btn-primary w-full mb-4"
            >
              <Upload size={20} className="mr-2" />
              Choose CSV Files
            </button>

            {jobFiles.length > 0 && (
              <div className="mt-4 text-left">
                <p className="text-sm text-gray-400 mb-2">Selected Files:</p>
                {jobFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-800 rounded p-2 mb-2">
                    <span className="text-sm text-green-400">{file.name}</span>
                    <button
                      onClick={() => removeJobFile(index)}
                      className="text-red-400 hover:text-red-300 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Resumes Upload */}
        <div className="card">
          <div className="text-center py-8">
            <div className="bg-purple-500/20 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Users size={40} className="text-purple-400" />
            </div>
            
            <h3 className="text-2xl font-bold mb-4">Candidate Resumes</h3>
            <p className="text-gray-400 mb-6">
              Upload PDF or DOCX files containing candidate resumes
            </p>
            
            <input
              ref={resumeFileRef}
              type="file"
              accept=".pdf,.doc,.docx"
              multiple
              onChange={handleResumeFileSelect}
              className="hidden"
            />
            
            <button
              onClick={() => resumeFileRef.current?.click()}
              className="btn-primary w-full mb-4"
            >
              <Upload size={20} className="mr-2" />
              Choose Resume Files
            </button>

            {resumeFiles.length > 0 && (
              <div className="mt-4 text-left">
                <p className="text-sm text-gray-400 mb-2">
                  Selected Files: ({resumeFiles.length} resumes)
                </p>
                <div className="max-h-32 overflow-y-auto">
                  {resumeFiles.slice(0, 5).map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-800 rounded p-2 mb-2">
                      <span className="text-sm text-green-400 truncate">{file.name}</span>
                      <button
                        onClick={() => removeResumeFile(index)}
                        className="text-red-400 hover:text-red-300 text-sm ml-2"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  {resumeFiles.length > 5 && (
                    <div className="text-xs text-gray-500 text-center">
                      ... and {resumeFiles.length - 5} more files
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="text-center">
        {canProceed ? (
          <button
            onClick={processUploads}
            disabled={isUploading}
            className="btn-primary text-xl px-12 py-4 disabled:opacity-50"
          >
            {isUploading ? (
              <>
                <Loader className="animate-spin mr-3" size={24} />
                Processing...
              </>
            ) : (
              <>
                Start AI Screening
                <ArrowRight size={24} className="ml-3" />
              </>
            )}
          </button>
        ) : (
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <p className="text-gray-400 mb-2">Ready to start?</p>
            <p className="text-sm text-gray-500">
              Upload job descriptions (CSV) and/or candidate resumes (PDF/DOCX) to begin AI matching
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UnifiedUploadFlow;