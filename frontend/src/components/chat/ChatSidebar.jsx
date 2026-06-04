import React, { useState } from 'react';
import { PlusCircle, LogOut } from 'lucide-react';
import { useChats } from '../../context/ChatContext';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/button';
import { Separator } from '../ui/separator';
import { ChatListItem } from './ChatListItem';

export function ChatSidebar() {
  const { chats, selectedChatId, selectChat, createChat, deleteChat, isLoadingChats } = useChats();
  const { user, logout } = useAuth();
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateChat = async () => {
    try {
      setIsCreating(true);
      await createChat();
    } catch (error) {
      console.error(error);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="flex h-full w-[350px] flex-col border-r bg-muted/20">
      <div className="flex h-20 items-center px-6 font-semibold text-2xl border-b">
        Biomedical AI
      </div>
      
      <div className="p-6">
        <Button 
          onClick={handleCreateChat} 
          disabled={isCreating} 
          className="w-full justify-start gap-3 h-14 text-lg" 
          variant="outline"
        >
          <PlusCircle className="h-6 w-6" />
          {isCreating ? 'Creating...' : 'New Chat'}
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden px-4">
        <div className="flex flex-col gap-2 p-2">
          {isLoadingChats ? (
            <p className="text-lg text-muted-foreground p-3 text-center">Loading chats...</p>
          ) : chats.length === 0 ? (
            <p className="text-lg text-muted-foreground p-3 text-center">No chats yet</p>
          ) : (
            chats.map((chat) => (
              <ChatListItem
                key={chat.id}
                chat={chat}
                isSelected={selectedChatId === chat.id}
                onSelect={selectChat}
                onDelete={deleteChat}
              />
            ))
          )}
        </div>
      </div>

      <Separator />
      
      <div className="flex items-center justify-between p-6 mt-auto">
        <div className="truncate text-lg text-muted-foreground font-medium pr-4">
          {user?.email}
        </div>
        <Button variant="ghost" size="icon" className="h-12 w-12" onClick={logout} title="Logout">
          <LogOut className="h-6 w-6" />
        </Button>
      </div>
    </div>
  );
}
