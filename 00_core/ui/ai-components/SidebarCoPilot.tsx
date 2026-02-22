import React, { useState, useRef, useEffect } from 'react';

interface SidebarCoPilotProps {
    currentContent: string;
    onUpdateContent: (newContent: string) => void;
    onClose: () => void;
}

interface Message {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    timestamp: number;
}

const SidebarCoPilot: React.FC<SidebarCoPilotProps> = ({ currentContent, onUpdateContent, onClose }) => {
    const [messages, setMessages] = useState<Message[]>([
        { id: '1', role: 'assistant', text: 'Co-Pilot Online. Mode: EDITOR. How can I help?', timestamp: Date.now() }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState<'EDITOR' | 'CODING_ASSISTANT'>('EDITOR');
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { id: Date.now().toString(), role: 'user', text: input, timestamp: Date.now() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('/api/ai/edit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: currentContent,
                    instruction: input,
                    mode: mode
                })
            });
            const data = await res.json();

            if (data.success) {
                const aiMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', text: data.data.content, timestamp: Date.now() };
                setMessages(prev => [...prev, aiMsg]);
            } else {
                const errorMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', text: `Error: ${data.error}`, timestamp: Date.now() };
                setMessages(prev => [...prev, errorMsg]);
            }
        } catch (e) {
            const errorMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', text: 'Connection failed.', timestamp: Date.now() };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-80 bg-zinc-900 border-l border-zinc-800 flex flex-col h-full animate-in slide-in-from-right duration-300 rounded-lg overflow-hidden">
            <div className="p-4 border-b border-zinc-800 bg-zinc-950">
                <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse"></span>
                        Co-Pilot
                    </h3>
                    <button onClick={onClose} className="text-zinc-500 hover:text-white">&times;</button>
                </div>

                {/* Mode Toggle */}
                <div className="flex bg-black rounded p-1 gap-1 border border-zinc-800">
                    <button
                        onClick={() => setMode('EDITOR')}
                        className={`flex-1 text-[9px] uppercase font-bold py-1.5 rounded transition-all ${mode === 'EDITOR' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-600 hover:text-zinc-400'}`}
                    >
                        Editor
                    </button>
                    <button
                        onClick={() => setMode('CODING_ASSISTANT')}
                        className={`flex-1 text-[9px] uppercase font-bold py-1.5 rounded transition-all ${mode === 'CODING_ASSISTANT' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-600 hover:text-zinc-400'}`}
                    >
                        Coder
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-zinc-900/50" ref={scrollRef}>
                {messages.map(msg => (
                    <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`max-w-[90%] p-3 rounded-lg text-xs font-mono leading-relaxed ${msg.role === 'user'
                                ? 'bg-zinc-800 text-white border border-zinc-700'
                                : 'bg-orange-500/10 text-orange-200 border border-orange-500/20'
                            }`}>
                            {msg.text}
                        </div>
                        {msg.role === 'assistant' && (
                            <button
                                onClick={() => onUpdateContent(msg.text)}
                                className="mt-1 text-[9px] uppercase tracking-widest text-zinc-500 hover:text-orange-500 flex items-center gap-1 ml-1"
                            >
                                <span>REPLACE CONTENT</span>
                            </button>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="flex items-center gap-2 text-xs text-zinc-600 font-mono p-2">
                        <span className="uppercase tracking-widest text-[9px]">Processing</span>
                        <div className="flex gap-1">
                            <div className="w-1 h-1 bg-zinc-600 rounded-full animate-bounce"></div>
                            <div className="w-1 h-1 bg-zinc-600 rounded-full animate-bounce delay-75"></div>
                            <div className="w-1 h-1 bg-zinc-600 rounded-full animate-bounce delay-150"></div>
                        </div>
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-zinc-800 bg-zinc-950">
                <div className="relative">
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSend()}
                        placeholder={`Ask ${mode === 'EDITOR' ? 'Editor' : 'Coder'}...`}
                        className="w-full bg-zinc-900 border border-zinc-700 rounded p-2 pr-10 text-xs text-white focus:border-orange-500 focus:outline-none placeholder:text-zinc-600 font-mono"
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading}
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white"
                    >
                        &rarr;
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SidebarCoPilot;
