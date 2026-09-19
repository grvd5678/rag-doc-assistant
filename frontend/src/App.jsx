import { useState } from 'react';
import FileUpload from './components/FileUpload';
import ChatBox from './components/ChatBox';
import Sources from './components/Sources';
import { Cpu } from 'lucide-react';

export default function App() {
  const [sources, setSources] = useState([]);
  const [activeDoc, setActiveDoc] = useState(null);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10">
      <header className="max-w-7xl mx-auto mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-500/20">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">DocuMind AI</h1>
            <p className="text-xs text-slate-400">RAG Document Assistant Platform</p>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 space-y-6">
          <FileUpload onUploadSuccess={(docName) => setActiveDoc(docName)} />
          <Sources sources={sources} />
        </div>

        <div className="lg:col-span-8">
          <ChatBox onQueryResult={(srcs) => setSources(srcs)} activeDocument={activeDoc} />
        </div>
      </main>
    </div>
  );
}

