import React, { useState, useEffect } from 'react';

interface AICompletionProps {
    onApply: (code: string) => void;
    initialCode?: string;
    onClose: () => void;
}

const AICompletion: React.FC<AICompletionProps> = ({ onApply, initialCode, onClose }) => {
    const [context, setContext] = useState('');
    const [currentCode, setCurrentCode] = useState(initialCode || '');
    const [result, setResult] = useState('');
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState<'EDITOR' | 'JOURNALIST' | 'CRITIC' | 'VISUAL_DIRECTOR'>('EDITOR');

    useEffect(() => {
        if (initialCode) setCurrentCode(initialCode);
    }, [initialCode]);

    const handleGenerate = async () => {
        if (!currentCode) return;
        setLoading(true);
        try {
            const res = await fetch('/api/ai/edit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: currentCode,
                    instruction: context,
                    mode: mode
                })
            });
            const data = await res.json();

            if (data.success) {
                setResult(data.data.content);
            } else {
                setResult(`// ERROR: ${data.error}`);
            }
        } catch (e) {
            console.error(e);
            setResult('// TRANSFORMATION_ERROR: Connection failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-12">
            <div className="w-full max-w-6xl h-[80vh] bg-black border border-zinc-800 flex flex-col p-8 shadow-2xl">

                <div className="flex justify-between items-start mb-8 border-l-4 border-orange-500 pl-6">
                    <div>
                        <h2 className="text-4xl font-black text-white mb-2 italic tracking-tighter uppercase">
                            AI Forge: <span className="text-orange-500">Neural Orchestrator</span>
                        </h2>
                        <p className="text-zinc-600 font-bold text-[10px] uppercase tracking-widest max-w-2xl">
                            Select your operative mode.
                        </p>
                    </div>
                    <button onClick={onClose} className="text-zinc-500 hover:text-white uppercase text-xs tracking-widest font-bold">Close</button>
                </div>

                <div className="flex-1 grid grid-cols-2 gap-10 min-h-0">
                    <div className="flex flex-col space-y-6 overflow-hidden">

                        {/* Mode Selector */}
                        <div className="grid grid-cols-2 gap-2">
                            {[
                                { id: 'EDITOR', label: 'Copy Editor', desc: 'Fixes & Flow (No Em Dashes)' },
                                { id: 'JOURNALIST', label: 'Journalist', desc: 'Expand & Research' },
                                { id: 'CRITIC', label: 'Yin Yang', desc: 'Critique & Holes' },
                                { id: 'VISUAL_DIRECTOR', label: 'Visuals', desc: 'Image Prompts' }
                            ].map(m => (
                                <button
                                    key={m.id}
                                    onClick={() => setMode(m.id as any)}
                                    className={`p-3 border text-left transition-all ${mode === m.id ? 'border-orange-500 bg-orange-500/10 text-white' : 'border-zinc-800 bg-zinc-900 text-zinc-500 hover:border-zinc-700'}`}
                                >
                                    <div className="text-[10px] font-black uppercase tracking-widest">{m.label}</div>
                                    <div className="text-[9px] opacity-60">{m.desc}</div>
                                </button>
                            ))}
                        </div>

                        <div className="flex-shrink-0">
                            <label className="block text-[8px] font-black text-zinc-500 mb-2 uppercase tracking-[0.3em]">Instruction / Intent (Optional)</label>
                            <input
                                type="text"
                                value={context}
                                onChange={(e) => setContext(e.target.value)}
                                placeholder={mode === 'CRITIC' ? "Focus on..." : "Specific requirements..."}
                                className="w-full bg-[#050505] border border-[#111] px-5 py-4 text-orange-500 focus:outline-none focus:border-orange-500/40 font-mono text-xs uppercase font-black"
                            />
                        </div>

                        <div className="flex-1 flex flex-col min-h-0">
                            <label className="block text-[8px] font-black text-zinc-500 mb-2 uppercase tracking-[0.3em]">Source Content</label>
                            <textarea
                                value={currentCode}
                                onChange={(e) => setCurrentCode(e.target.value)}
                                className="flex-1 w-full bg-[#050505] border border-[#111] p-6 font-mono text-xs text-zinc-400 resize-none focus:outline-none focus:border-orange-500/40 custom-scrollbar"
                                placeholder="// Paste content here..."
                            />
                        </div>
                        <button
                            onClick={handleGenerate}
                            disabled={loading || !currentCode}
                            className="w-full bg-orange-500 hover:bg-orange-400 text-black font-black py-5 shadow-2xl transition-all flex items-center justify-center space-x-4 text-xs uppercase tracking-[0.4em]"
                        >
                            {loading ? (
                                <div className="flex items-center space-x-3">
                                    <span>PROCESSING...</span>
                                </div>
                            ) : (
                                <>
                                    <span>INITIATE_TRANSFORM</span>
                                </>
                            )}
                        </button>
                    </div>

                    <div className="flex flex-col min-h-0">
                        <label className="block text-[8px] font-black text-zinc-500 mb-2 uppercase tracking-[0.3em]">Result</label>
                        <div className="flex-1 bg-[#020202] border border-[#111] p-8 overflow-y-auto relative custom-scrollbar">
                            {result ? (
                                <pre className="text-xs font-mono text-emerald-500/80 whitespace-pre-wrap leading-relaxed">
                                    {result}
                                </pre>
                            ) : (
                                <div className="flex flex-col items-center justify-center h-full text-zinc-900 text-[10px] uppercase tracking-widest font-black italic opacity-40">
                                    Waiting_For_Convergence
                                </div>
                            )}

                            {result && (
                                <div className="absolute top-6 right-6 flex space-x-2">
                                    <button
                                        onClick={() => navigator.clipboard.writeText(result)}
                                        className="bg-black hover:bg-[#111] text-[8px] font-black px-4 py-2 border border-[#111] text-zinc-500 uppercase tracking-widest transition-all hover:text-orange-500"
                                    >
                                        COPY
                                    </button>
                                    <button
                                        onClick={() => onApply(result)}
                                        className="bg-orange-500 hover:bg-white text-black hover:text-black text-[8px] font-black px-4 py-2 border border-orange-500 uppercase tracking-widest transition-all"
                                    >
                                        APPLY
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AICompletion;
