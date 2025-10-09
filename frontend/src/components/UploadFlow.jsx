import React, { useState } from 'react';
import { Upload, FileText, Loader, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadCVs, uploadJobCSV, summarizeJobs, triggerMatching } from '../services/api';
import ProcessingPipeline from './ProcessingPipeline';

const UploadFlow = ({ mode, onComplete }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const isCandidate = mode === 'candidate';
  const acceptedFormats = isCandidate ? '.pdf,.docx' : '.csv';
  const multiple = isCandidate;

  const steps = isCandidate ? [
    'Clearing existing data & uploading CVs',
    'Extracting text from PDFs',
    'Parsing candidate information',
    'Matching with job descriptions',
    'Complete!'
  ] : [
    'Clearing existing data & uploading jobs',
    'Analyzing with AI',
    'Extracting requirements',
    'Matching with candidates',
    'Complete!'
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const simulateProgress = async (callback) => {
    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i);
      await new Promise(resolve => setTimeout(resolve, 1500));
      if (i === 1 && callback) {
        await callback();
      }
      if (i === 3) {
        // Trigger matching at step 3
        try {
          await triggerMatching();
        } catch (err) {
          console.log('Matching error:', err);
        }
      }
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    try {
      setUploading(true);
      setError(null);

      if (isCandidate) {
        // Upload CVs
        await simulateProgress(async () => {
          await uploadCVs(files);
        });
      } else {
        // Upload Jobs + Summarize
        await simulateProgress(async () => {
          await uploadJobCSV(files[0]);
          await summarizeJobs();
        });
      }

      setTimeout(() => {
        onComplete(mode);
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
      setCurrentStep(0);
    } finally {
      setUploading(false);
    }
  };

  if (uploading) {
    return <ProcessingPipeline steps={steps} currentStep={currentStep} />;
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold mb-2">
          {isCandidate ? 'Upload Your Resumes' : 'Upload Job Descriptions'}
        </h2>
        <p className="text-gray-400">
          {isCandidate 
            ? 'Upload PDF or DOCX files - we\'ll extract and match them with available jobs'
            : 'Upload a CSV file with job descriptions - AI will analyze and find matching candidates'}
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-900/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="card">
        <div
          className={`border-2 border-dashed rounded-lg p-16 text-center transition-all ${
            dragActive 
              ? 'border-primary bg-primary/10 scale-105' 
              : 'border-gray-600 hover:border-gray-500'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto mb-4 text-gray-400" size={64} />
          
          {files.length === 0 ? (
            <>
              <p className="text-xl mb-2">Drag & drop files here</p>
              <p className="text-gray-400 mb-6">
                {isCandidate ? 'or click to browse (PDF, DOCX)' : 'or click to browse (CSV only)'}
              </p>
            </>
          ) : (
            <>
              <CheckCircle className="mx-auto mb-4 text-green-400" size={48} />
              <p className="text-xl mb-2">{files.length} file(s) selected</p>
            </>
          )}

          <label className="btn-primary cursor-pointer inline-block">
            <input
              type="file"
              accept={acceptedFormats}
              multiple={multiple}
              onChange={handleFileChange}
              className="hidden"
            />
            Choose Files
          </label>
        </div>

        {files.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold mb-3">Selected Files:</h4>
            <div className="space-y-2 max-h-40 overflow-y-auto bg-gray-700 rounded p-3">
              {files.map((file, index) => (
                <div key={index} className="flex items-center space-x-2 text-sm">
                  <FileText size={16} className="text-blue-400" />
                  <span>{file.name}</span>
                  <span className="text-gray-400 text-xs ml-auto">
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={files.length === 0 || uploading}
          className="btn-primary w-full mt-6 py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? (
            <span className="flex items-center justify-center space-x-2">
              <Loader className="animate-spin" size={24} />
              <span>Processing...</span>
            </span>
          ) : (
            `Process ${files.length} File${files.length !== 1 ? 's' : ''}`
          )}
        </button>
      </div>
    </div>
  );
};

export default UploadFlow;