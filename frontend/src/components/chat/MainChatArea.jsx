import React from 'react';
import { useChats } from '../../context/ChatContext';
import { EmptyState } from './EmptyState';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

export function MainChatArea() {
  const { chats, selectedChatId } = useChats();
  const selectedChat = chats.find(c => c.id === selectedChatId);

  if (!selectedChatId) {
    return <EmptyState />;
  }

  return (
    <div className="flex h-full w-full flex-col bg-background">
      <header className="flex h-14 items-center justify-between border-b px-6 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-10">
        <h2 className="text-lg font-semibold truncate pr-4">
          {selectedChat?.title || 'Untitled Chat'}
        </h2>
      </header>
      
      <MessageList />
      <ChatInput />
    </div>
  );
}
