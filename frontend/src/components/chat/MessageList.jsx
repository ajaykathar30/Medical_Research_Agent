import React, { useEffect, useRef, useState } from 'react';
import { MessageBubble } from './MessageBubble';
import { useChats } from '../../context/ChatContext';

export function MessageList() {
  const { messages, isLoadingMessages } = useChats();
  const bottomRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const [isAtBottom, setIsAtBottom] = useState(true);

  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    
    // Check if user is scrolled up (give a generous 100px threshold for bottom)
    const atBottom = scrollHeight - scrollTop - clientHeight < 100;
    setIsAtBottom(atBottom);
  };

  // Auto-scroll to bottom whenever messages change, BUT ONLY if we are at the bottom
  useEffect(() => {
    if (isAtBottom && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'auto' });
    }
  }, [messages, isAtBottom]);

  if (isLoadingMessages) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4 text-muted-foreground">
          <div className="h-8 w-8 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
          <p>Loading messages...</p>
        </div>
      </div>
    );
  }

  if (!messages || messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center p-8 text-center text-muted-foreground">
        <p>No messages yet. Send a message to start the conversation.</p>
      </div>
    );
  }

  return (
    <div 
      className="flex-1 overflow-y-auto p-4 sm:p-6" 
      ref={scrollContainerRef} 
      onScroll={handleScroll}
    >
      <div className="mx-auto max-w-5xl flex flex-col pb-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  );
}
