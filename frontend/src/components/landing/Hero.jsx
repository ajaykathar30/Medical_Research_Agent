import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/button';
import { ArrowRight, Activity } from 'lucide-react';

export function Hero() {
  const { user } = useAuth();

  return (
    <section className="relative overflow-hidden py-24 lg:py-32">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-8 items-center">
          <div className="flex flex-col justify-center text-center lg:text-left space-y-8">
            <div className="space-y-4">
              <h1 className="font-heading text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
                Evidence-based answers to your <span className="text-primary">biomedical research</span> questions
              </h1>
              <p className="max-w-[42rem] mx-auto lg:mx-0 text-lg sm:text-xl text-muted-foreground">
                An advanced AI assistant that searches the latest published research, clinical trials, and drug-safety data to return concise, fully-cited answers.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
              {user ? (
                <Button size="lg" className="h-14 px-8 text-lg" asChild>
                  <Link to="/chat">
                    Go to App <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              ) : (
                <>
                  <Button size="lg" className="h-14 px-8 text-lg w-full sm:w-auto" asChild>
                    <Link to="/register">
                      Get started <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                  </Button>
                  <Button size="lg" variant="outline" className="h-14 px-8 text-lg w-full sm:w-auto" asChild>
                    <Link to="/login">Log in</Link>
                  </Button>
                </>
              )}
            </div>
          </div>
          
          <div className="mx-auto w-full max-w-lg lg:max-w-none flex justify-center">
            <div className="relative w-full aspect-square md:aspect-[4/3] lg:aspect-square bg-muted/30 rounded-full flex items-center justify-center border-8 border-background shadow-2xl">
              <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-primary/20 to-transparent" />
              <Activity className="w-32 h-32 md:w-48 md:h-48 text-primary opacity-80" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
