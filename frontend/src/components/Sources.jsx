import { BookOpen, MapPin } from 'lucide-react';

export default function Sources({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg text-slate-500 text-center">
        <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Sources & Citations will appear here after querying.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-lg space-y-4">
      <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
        <BookOpen className="text-indigo-400" /> Relevant Sources ({sources.length})
      </h2>

      <div className="space-y-3">
        {sources.map((src, index) => (
          <div key={index} className="bg-slate-900 border border-slate-700 p-4 rounded-lg space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-indigo-400">
              <span className="truncate max-w-[200px]">📄 {src.source}</span>
              <span className="flex items-center gap-1 bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">
                <MapPin className="w-3 h-3" /> Page {src.page}
              </span>
            </div>
            <p className="text-xs text-slate-300 italic bg-slate-950/50 p-2.5 rounded border border-slate-800/80 leading-relaxed">
              "{src.snippet}"
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}