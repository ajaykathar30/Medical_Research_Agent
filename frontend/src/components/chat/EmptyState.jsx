import React from 'react';
import { MessageSquare } from 'lucide-react';

export function EmptyState() {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center text-muted-foreground p-8 text-center">
      <div className="flex h-24 w-24 items-center justify-center rounded-full bg-muted mb-8">
        <MessageSquare className="h-12 w-12 opacity-50" />
      </div>
      <h2 className="text-3xl font-semibold mb-3 text-foreground">Biomedical Research Assistant</h2>
      <p className="max-w-md text-lg">
        Select an existing chat from the sidebar or start a new one to begin your research.
      </p>
    </div>
  );
}
