import React, { useState, useRef } from 'react';
import { Upload, FileText, ArrowLeft, AlertCircle, ShieldCheck } from 'lucide-react';

import { extractReport } from '../services/api';
import type { StructuredClinicalProfile } from '../types/api';

interface ReportUploadProps {
  onBack: () => void;
  onExtracted: (data: StructuredClinicalProfile) => void;
}

export const ReportUpload: React.FC<ReportUploadProps> = ({ onBack, onExtracted }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile: File) => {
    setError(null);
    if (!selectedFile.name.toLowerCase().endsWith(".pdf") && selectedFile.type !== "application/pdf") {
      setError("Please upload a valid PDF document. Images (JPG/PNG) are not supported.");
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size exceeds 10 MB limit. Please select a smaller PDF.");
      return;
    }
    setFile(selectedFile);
  };

  const handleSubmit = async () => {
    if (!file || loading) return;
    
    setLoading(true);
    setError(null);
    try {
      const extractedData = await extractReport(file);
      onExtracted(extractedData);
    } catch (err: any) {
      setError(err.message || "An error occurred while extracting the clinical report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <button 
        onClick={onBack}
        disabled={loading}
        className="mb-8 inline-flex items-center text-slate-600 hover:text-slate-900 transition-colors text-sm font-medium bg-white border border-slate-200 px-4 py-2 rounded-xl shadow-xs disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Options
      </button>

      <div className="text-center mb-10 space-y-3">
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Upload Clinical PDF Report
        </h2>
        <p className="text-slate-600 max-w-lg mx-auto text-sm sm:text-base leading-relaxed">
          Upload a medical, cognitive, or neurological evaluation report in PDF format for automated clinical profile extraction.
        </p>
      </div>

      <div 
        className={`border-2 border-dashed rounded-3xl p-10 text-center transition-all duration-300 ${
          isDragging ? 'border-blue-500 bg-blue-50/60 shadow-md' : 'border-slate-300 bg-white hover:bg-slate-50/80 hover:border-slate-400 shadow-xs'
        } ${file ? 'border-blue-500 bg-blue-50/20' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileInput}
          accept="application/pdf"
          className="hidden" 
        />
        
        {loading ? (
          <div className="flex flex-col items-center py-6">
            <div className="relative w-16 h-16 mb-6 flex items-center justify-center">
              <div className="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-xl font-bold text-slate-900 mb-2">Extracting Clinical Profile...</p>
            <p className="text-xs text-slate-600 max-w-sm">Synthesizing cognitive test scores, demographics, biomarkers, and symptom flags</p>
          </div>
        ) : file ? (
          <div className="flex flex-col items-center py-4">
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-2xl mb-4">
              <FileText className="w-10 h-10 text-blue-600" />
            </div>
            <p className="text-lg font-bold text-slate-900 mb-1">{file.name}</p>
            <p className="text-xs font-semibold text-slate-600 mb-6 bg-slate-100 border border-slate-200 px-3 py-1 rounded-full">
              {(file.size / 1024 / 1024).toFixed(2)} MB • PDF Document
            </p>
            <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
              <button 
                onClick={() => { setFile(null); setError(null); }}
                disabled={loading}
                className="px-5 py-3 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 font-semibold text-sm transition-colors disabled:opacity-50 cursor-pointer shadow-xs"
              >
                Choose Another File
              </button>
              <button 
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-bold text-sm transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
              >
                Extract Clinical Information →
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center cursor-pointer py-6 group" onClick={() => fileInputRef.current?.click()}>
            <div className="bg-slate-100 border border-slate-200 p-4 rounded-2xl mb-4 group-hover:bg-blue-50 group-hover:border-blue-200 transition-colors">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-lg font-bold text-slate-900 mb-1">Click to upload or drag and drop</p>
            <p className="text-xs text-slate-500">Text-based PDF medical documents (Max 10 MB)</p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-6 bg-rose-50 border border-rose-200 text-rose-800 px-5 py-4 rounded-2xl flex items-start">
          <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5 text-rose-600" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      <div className="mt-8 text-center text-xs text-slate-600 bg-white rounded-2xl p-5 border border-slate-200 shadow-xs flex items-start space-x-3 text-left">
        <ShieldCheck className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-bold text-slate-900 mb-1">In-Memory Privacy Guarantee</p>
          <p className="text-slate-600 leading-relaxed">
            Uploaded reports are extracted in-memory using PDF parsing pipelines and are never saved to disk or permanent databases.
          </p>
        </div>
      </div>
    </div>
  );
};

