import { useState } from 'react';
import axios from 'axios';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function ChatBox({ onQueryResult, activeDocument }) {
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQuery = question;
    setQuestion('');
    setChatHistory((prev) => [...prev, { role: 'user', content: userQuery }]);
    setLoading(true);

    try {
      const response = await axios.post('/query', {
        question: userQuery,
      });

      const { answer, sources } = response.data;

      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', content: answer, sources },
      ]);

      if (onQueryResult) {
        onQueryResult(sources);
      }
    } catch {
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error processing question. Please upload a PDF first or check server status.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg flex flex-col h-[600px]">
      <div className="p-4 border-b border-slate-700 flex items-center gap-2">
        <Bot className="text-indigo-400" />
        <h2 className="text-xl font-bold text-slate-100">DocuMind Assistant</h2>
        {activeDocument && (
          <span className="ml-auto text-xs bg-indigo-950 text-indigo-300 border border-indigo-700/50 px-2.5 py-1 rounded-full">
            📄 {activeDocument}
          </span>
        )}
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {chatHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-center">
            <Bot className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm">Upload a document and ask any question to get started!</p>
          </div>
        ) : (
          chatHistory.map((msg, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                msg.role === 'user' ? 'flex-row-reverse' : ''
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === 'user' ? 'bg-indigo-600' : 'bg-slate-700'
                }`}
              >
                {msg.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-indigo-400" />
                )}
              </div>

              <div
                className={`max-w-[85%] p-3.5 rounded-xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-slate-900 border border-slate-700 text-slate-200 rounded-tl-none'
                }`}
              >
                {msg.role === 'user' ? (
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                ) : (
                  <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed">
                    <ReactMarkdown
                      components={{
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                        ul: ({ node, ...props }) => (
                          <ul className="list-disc pl-5 mb-2 space-y-1 text-slate-300" {...props} />
                        ),
                        ol: ({ node, ...props }) => (
                          <ol className="list-decimal pl-5 mb-2 space-y-1 text-slate-300" {...props} />
                        ),
                        li: ({ node, ...props }) => <li className="text-slate-200" {...props} />,
                        strong: ({ node, ...props }) => (
                          <strong className="font-semibold text-indigo-300" {...props} />
                        ),
                        code: ({ node, ...props }) => (
                          <code
                            className="bg-slate-800 text-indigo-300 px-1.5 py-0.5 rounded font-mono text-xs"
                            {...props}
                          />
                        ),
                        pre: ({ node, ...props }) => (
                          <pre
                            className="bg-slate-950 p-3 rounded-lg overflow-x-auto text-xs font-mono border border-slate-800 my-2"
                            {...props}
                          />
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400 text-sm">
            <Bot className="w-8 h-8 p-1.5 bg-slate-700 rounded-full text-indigo-400" />
            <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 px-4 py-2 rounded-xl">
              <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="p-4 border-t border-slate-700 flex gap-2">
        <input
          type="text"
          placeholder="Ask something about your document..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 text-white p-2.5 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}