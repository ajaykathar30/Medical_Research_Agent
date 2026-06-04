import React from 'react';
import { BookOpen, Stethoscope, ShieldAlert, FileCheck2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';

const features = [
  {
    title: 'Literature Search',
    description: 'Finds and summarizes relevant published research directly from PubMed.',
    icon: BookOpen,
  },
  {
    title: 'Clinical-trial Landscape',
    description: 'Surfaces ongoing and completed trials from ClinicalTrials.gov.',
    icon: Stethoscope,
  },
  {
    title: 'Drug Safety & Labels',
    description: 'Access reported adverse events and FDA label information via openFDA.',
    icon: ShieldAlert,
  },
  {
    title: 'Cited, Grounded Answers',
    description: 'Every claim is backed by a linked, verifiable biomedical source.',
    icon: FileCheck2,
  },
];

export function Features() {
  return (
    <section className="py-24 bg-muted/30">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-heading text-3xl font-bold tracking-tight sm:text-4xl">Comprehensive Data Sources</h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Our agent connects to the world's most trusted medical databases to provide you with accurate, up-to-date information.
          </p>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="border-none shadow-md bg-background hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base text-muted-foreground">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
