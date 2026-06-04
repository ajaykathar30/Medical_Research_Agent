import React from 'react';
import { ChatSidebar } from '../components/chat/ChatSidebar';
import { MainChatArea } from '../components/chat/MainChatArea';

export default function ChatPage() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <ChatSidebar />
      <MainChatArea />
    </div>
  );
}
