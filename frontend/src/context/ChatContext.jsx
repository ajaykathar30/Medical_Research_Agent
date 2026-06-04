import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import api from '../lib/api';
import { useAuth } from './AuthContext';

const ChatContext = createContext(undefined);

export function ChatProvider({ children }) {
  const { user } = useAuth();
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  
  const [isLoadingChats, setIsLoadingChats] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [error, setError] = useState(null);

  const [isStreaming, setIsStreaming] = useState(false);

  // Load all chats
  const loadChats = useCallback(async (background = false) => {
    if (!user) return;
    if (!background) setIsLoadingChats(true);
    setError(null);
    try {
      const response = await api.get('/chats');
      setChats(response.data);
    } catch (err) {
      if (!background) setError(err.message || 'Failed to load chats');
    } finally {
      if (!background) setIsLoadingChats(false);
    }
  }, [user]);

  // Load chats on mount (or when user changes)
  useEffect(() => {
    loadChats();
  }, [loadChats]);

  // Create a new chat
  const createChat = async (title = 'New Chat') => {
    setError(null);
    try {
      const response = await api.post('/chats', { title });
      const newChat = response.data;
      setChats(prev => [newChat, ...prev]);
      await selectChat(newChat.id);
      return newChat;
    } catch (err) {
      setError(err.message || 'Failed to create chat');
      throw err;
    }
  };

  // Select a chat and fetch its messages
  const selectChat = async (id) => {
    if (selectedChatId === id) return;
    
    setSelectedChatId(id);
    setMessages([]);
    setIsLoadingMessages(true);
    setError(null);

    try {
      const response = await api.get(`/chats/${id}`);
      setMessages(response.data.messages || []);
    } catch (err) {
      setError(err.message || 'Failed to load messages');
      setSelectedChatId(null);
    } finally {
      setIsLoadingMessages(false);
    }
  };

  // Delete a chat
  const deleteChat = async (id) => {
    setError(null);
    try {
      await api.delete(`/chats/${id}`);
      setChats(prev => prev.filter(c => c.id !== id));
      if (selectedChatId === id) {
        setSelectedChatId(null);
        setMessages([]);
      }
    } catch (err) {
      setError(err.message || 'Failed to delete chat');
      throw err;
    }
  };

  const sendMessage = async (content) => {
    if (!selectedChatId || isStreaming || !content.trim()) return;

    // Optimistic UI updates
    const tempUserMsgId = `temp-user-${Date.now()}`;
    const tempAstMsgId = `temp-ast-${Date.now()}`;

    setMessages((prev) => [
      ...prev,
      { id: tempUserMsgId, role: 'user', content: content, created_at: new Date().toISOString() },
      { id: tempAstMsgId, role: 'assistant', content: '', created_at: new Date().toISOString(), isStreaming: true },
    ]);

    setIsStreaming(true);
    setError(null);

    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/chats/${selectedChatId}/messages/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // essential for cookie auth
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        let errorMsg = 'Failed to send message';
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errorMsg;
        } catch (e) {}
        throw new Error(errorMsg);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        
        // Keep the last chunk in the buffer if it doesn't end with \n\n
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);
              
              if (data.token) {
                setMessages((prev) => 
                  prev.map((msg) => 
                    msg.id === tempAstMsgId 
                      ? { ...msg, content: msg.content + data.token }
                      : msg
                  )
                );
              } else if (data.done) {
                // Done streamed
              } else if (data.error) {
                throw new Error(data.error);
              }
            } catch (err) {
              console.error('Error parsing SSE json', err);
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'Stream connection failed');
      
      // Update the assistant message to show error
      setMessages((prev) => 
        prev.map((msg) => 
          msg.id === tempAstMsgId 
            ? { ...msg, content: msg.content + '\n\n[Error: ' + (err.message || 'Connection lost') + ']', isStreaming: false }
            : msg
        )
      );
    } finally {
      setIsStreaming(false);
      
      // Mark as not streaming
      setMessages((prev) => 
        prev.map((msg) => 
          msg.id === tempAstMsgId 
            ? { ...msg, isStreaming: false }
            : msg
        )
      );

      // Refresh to get real IDs and ensure title is synced in sidebar
      try {
        const chatRes = await api.get(`/chats/${selectedChatId}`);
        setMessages(chatRes.data.messages || []);
        loadChats(true);
      } catch (err) {
        console.error('Failed to sync after streaming', err);
      }
    }
  };

  const value = {
    chats,
    selectedChatId,
    messages,
    isLoadingChats,
    isLoadingMessages,
    isStreaming,
    error,
    loadChats,
    createChat,
    selectChat,
    deleteChat,
    sendMessage
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChats() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChats must be used within a ChatProvider');
  }
  return context;
}
