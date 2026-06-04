import React, { useState } from 'react';
import { SendHorizontal } from 'lucide-react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { useChats } from '../../context/ChatContext';

export function ChatInput() {
  const [content, setContent] = useState('');
  const { sendMessage, isStreaming, selectedChatId } = useChats();

  const handleSend = () => {
    if (!content.trim() || isStreaming || !selectedChatId) return;
    sendMessage(content);
    setContent('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full px-4 pb-2 pt-2 sm:px-8 sm:pb-4">
      <div className="mx-auto max-w-5xl relative flex items-center">
        <Textarea
          placeholder="Type your message..."
          className="min-h-[80px] max-h-[300px] w-full resize-y rounded-3xl pr-16 pl-6 py-5 text-xl md:text-xl bg-background shadow-xl border border-muted-foreground/30 focus-visible:ring-1 focus-visible:ring-primary disabled:opacity-75 disabled:cursor-not-allowed"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isStreaming || !selectedChatId}
          rows={1}
        />
        <Button 
          size="icon" 
          onClick={handleSend}
          disabled={!content.trim() || isStreaming || !selectedChatId} 
          className="absolute right-4 bottom-4 h-12 w-12 rounded-full disabled:opacity-50 shadow-md transition-transform hover:scale-105 active:scale-95"
        >
          <SendHorizontal className="h-5 w-5" />
        </Button>
      </div>
      <div className="text-center mt-3 text-sm text-muted-foreground">
        AI can make mistakes. Consider verifying important biomedical information.
      </div>
    </div>
  );
}
