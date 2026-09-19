import { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export default function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setMessage(null);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage(response.data.message);
      if (onUploadSuccess) onUploadSuccess(file.name);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload document.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg">
      <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2 mb-4">
        <UploadCloud className="text-indigo-400" /> Upload Document
      </h2>

      <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-indigo-500 transition-colors cursor-pointer bg-slate-900/50">
        <input 
          type="file" 
          accept=".pdf" 
          onChange={handleFileChange} 
          className="hidden" 
          id="fileInput" 
        />
        <label htmlFor="fileInput" className="cursor-pointer flex flex-col items-center">
          <FileText className="w-10 h-10 text-slate-400 mb-2" />
          <span className="text-sm font-medium text-slate-300">
            {file ? file.name : 'Click to upload or drag and drop PDF'}
          </span>
          <span className="text-xs text-slate-500 mt-1">PDF documents only</span>
        </label>
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="w-full mt-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer disabled:cursor-not-allowed"
      >
        {loading ? <Loader2 className="animate-spin w-5 h-5" /> : 'Process PDF'}
      </button>

      {message && (
        <div className="mt-4 p-3 bg-emerald-950/60 border border-emerald-500/50 rounded-lg flex items-center gap-2 text-emerald-300 text-sm">
          <CheckCircle className="w-5 h-5 shrink-0" /> {message}
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-rose-950/60 border border-rose-500/50 rounded-lg flex items-center gap-2 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" /> {error}
        </div>
      )}
    </div>
  );
}