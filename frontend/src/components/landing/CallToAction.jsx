import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/button';

export function CallToAction() {
  const { user } = useAuth();

  return (
    <section className="bg-primary py-20 text-primary-foreground">
      <div className="container mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="font-heading text-3xl font-bold tracking-tight sm:text-4xl mb-6">
          Ready to accelerate your biomedical research?
        </h2>
        <p className="mb-10 text-lg text-primary-foreground/90 max-w-2xl mx-auto">
          Join researchers and healthcare professionals using AI to navigate complex medical literature and trials.
        </p>
        {user ? (
          <Button size="lg" variant="secondary" className="h-14 px-8 text-lg font-semibold" asChild>
            <Link to="/chat">Go to App</Link>
          </Button>
        ) : (
          <Button size="lg" variant="secondary" className="h-14 px-8 text-lg font-semibold" asChild>
            <Link to="/register">Get started for free</Link>
          </Button>
        )}
      </div>
    </section>
  );
}
