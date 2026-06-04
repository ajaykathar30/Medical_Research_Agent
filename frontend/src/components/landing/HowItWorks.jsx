import React from 'react';
import { Search, BrainCircuit, CheckCircle } from 'lucide-react';

const steps = [
  {
    title: 'Ask a Question',
    description: 'Type your complex biomedical research question in plain English.',
    icon: Search,
  },
  {
    title: 'AI Synthesis',
    description: 'The agent searches and synthesizes data across multiple trusted biomedical sources concurrently.',
    icon: BrainCircuit,
  },
  {
    title: 'Get Your Answer',
    description: 'Receive a concise, grounded answer with clear citations for further reading.',
    icon: CheckCircle,
  },
];

export function HowItWorks() {
  return (
    <section className="py-24">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-heading text-3xl font-bold tracking-tight sm:text-4xl">How it works</h2>
        </div>
        <div className="grid gap-12 lg:grid-cols-3">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="flex flex-col items-center text-center space-y-6">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Icon className="h-10 w-10" />
                </div>
                <div className="space-y-3">
                  <h3 className="text-2xl font-bold">
                    <span className="text-muted-foreground/50 mr-2">{index + 1}.</span>
                    {step.title}
                  </h3>
                  <p className="text-lg text-muted-foreground max-w-xs mx-auto">
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
