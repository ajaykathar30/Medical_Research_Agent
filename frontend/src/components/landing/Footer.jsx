import React from 'react';

export function Footer() {
  return (
    <footer className="border-t bg-background py-12">
      <div className="container mx-auto max-w-7xl px-4 flex flex-col items-center justify-between gap-6 sm:flex-row sm:px-6 lg:px-8">
        <div className="flex flex-col items-center sm:items-start gap-2">
          <span className="font-heading text-xl font-bold tracking-tight">Biomedical AI</span>
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Biomedical AI. All rights reserved.
          </p>
        </div>
        <div className="rounded-lg bg-destructive/10 px-4 py-2 border border-destructive/20 text-center">
          <p className="text-sm font-medium text-destructive">
            Disclaimer: This is a research aid, not medical advice.
          </p>
        </div>
      </div>
    </footer>
  );
}
