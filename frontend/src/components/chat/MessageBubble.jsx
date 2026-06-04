import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '../../lib/utils';

export function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={cn("flex w-full mb-6", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          isUser 
            ? "max-w-[85%] rounded-2xl px-6 py-4 text-lg shadow-sm bg-primary text-primary-foreground rounded-tr-sm" 
            : "w-full rounded-xl px-6 py-8 sm:px-10 sm:py-10 text-lg shadow-sm bg-background text-foreground border"
        )}
      >
        {message.isStreaming && !message.content ? (
          <div className="flex space-x-1.5 h-6 items-center justify-center px-2">
            <div className="h-2.5 w-2.5 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="h-2.5 w-2.5 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="h-2.5 w-2.5 bg-foreground/40 rounded-full animate-bounce"></div>
          </div>
        ) : (
          <div className={cn("leading-relaxed", !isUser && "prose prose-lg md:prose-xl dark:prose-invert max-w-none prose-p:leading-loose prose-pre:p-0 prose-li:my-2 prose-headings:mt-8 prose-headings:mb-4")}>
            {isUser ? (
              <div className="whitespace-pre-wrap">{message.content}</div>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
