import {
  CatchBoundary,
  Outlet,
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from '@tanstack/react-router';
// biome-ignore lint/style/useImportType: <explanation>
import { ICreateRouter } from '@akashaorg/typings/lib/ui';
import PollPage from '../poll-page';
import PollFormPage from '../poll-form-page';
import { useEffect, useState } from 'react';
const POLL_EDITOR = 'Poll editor';
const POLLS = 'Polls';

const routes = {
  [POLL_EDITOR]: '/poll-editor',
  [POLLS]: '/polls',
} as const;

const rootRoute = createRootRoute({
  component: Outlet,
  notFoundComponent: () => <div>Not found</div>,
});

const defaultRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    throw redirect({ to: routes[POLLS], replace: true });
  },
});

const pollsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: routes[POLLS],
  component: () => {
    return (
      <CatchBoundary getResetKey={() => 'polls_reset'} errorComponent={() => <div>Not found</div>}>
        <PollPage />
      </CatchBoundary>
    );
  },
});

const pollEditorRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: routes[POLL_EDITOR],
  component: () => {
    return (
      <CatchBoundary
        getResetKey={() => 'polls_form_reset'}
        errorComponent={() => <div>Not found</div>}
      >
        <PollFormPage />
      </CatchBoundary>
    );
  },
});

const akaVibeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/vibe',
  component: () => {
    const [post, setPost] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      const fetchPost = async () => {
        try {
          const response = await fetch('http://localhost:7007/generate-post',);
          const data = await response.json();
          
          if (response.ok) {
            setPost(data.post);
          } else {
            setError(data.error || 'Failed to fetch post');
          }
        } catch (err) {
          setError('An error occurred while fetching the post');
        } finally {
          setLoading(false);
        }
      };
      fetchPost();
    }, []);

    if (loading) {
      return (
        <CatchBoundary
          getResetKey={() => 'polls_form_reset'}
          errorComponent={() => <div>Not found</div>}
        >
          <div className="flex items-center justify-center min-h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
          </div>
        </CatchBoundary>
      );
    }

    if (error) {
      return (
        <CatchBoundary
          getResetKey={() => 'polls_form_reset'}
          errorComponent={() => <div>Not found</div>}
        >
          <div className="p-4">
            <div className="text-red-500">{error}</div>
            {/* biome-ignore lint/a11y/useButtonType: <explanation> */}
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Try Again
            </button>
          </div>
        </CatchBoundary>
      );
    }

    return (
      <CatchBoundary
        getResetKey={() => 'polls_form_reset'}
        errorComponent={() => <div>Not found</div>}
      >
        <div className="p-8">
          <div className="prose max-w-none">
            {post.split('\n').map((line, index) => {
              if (line.startsWith('# ')) {
                // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                return <h1 key={index} className="text-xl font-bold text-center pt-8 pb-4">{line.substring(2)}</h1>;
              }
              if (line.startsWith('## ')) {
                // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                return <h2 key={index} className="text-2xl font-bold text-center pt-8 pb-4">{line.substring(3)}</h2>;
              }
              if (line.startsWith('### ')) {
                // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                return <h1 key={index} className="text-3xl font-bold text-center pt-8 pb-4">{line.substring(4)}</h1>;
              }
              if (line.startsWith('#### ')) {
                // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                return <h3 key={index} className="text-xl font-bold text-center pt-6 pb-3">{line.substring(5)}</h3>;
              }
              if (line.startsWith('* ')) {
                // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                return <li key={index} className="ml-6 list-disc mb-2">{line.substring(2)}</li>;
              }
              if (line.includes('**')) {
                const parts = line.split('**');
                return (
                  // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                  <p key={index} className="mb-2">
                    {parts.map((part, i) => 
                      i % 2 === 1 ? (
                        // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                        <strong key={i} className="font-bold">{part}</strong>
                      ) : (
                        // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                        <span key={i}>{part}</span>
                      )
                    )}
                  </p>
                );
              }
              // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
              return <p key={index} className="mb-2">{line}</p>;
            })}
          </div>
        </div>
      </CatchBoundary>
    );
  },
});

const routeTree = rootRoute.addChildren([defaultRoute, pollsRoute, pollEditorRoute, akaVibeRoute]);

const router = ({ baseRouteName }: ICreateRouter) =>
  createRouter({
    routeTree,
    basepath: baseRouteName,
    defaultErrorComponent: ({ error }) => <div>Error: {error.message}</div>,
  });

export { routes, router, POLL_EDITOR, POLLS };
