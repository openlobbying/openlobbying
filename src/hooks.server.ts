import { building } from '$app/env';
import { auth, ensureAuthSchema } from '#lib/server/auth.js';
import { svelteKitHandler } from 'better-auth/svelte-kit';
import type { Handle } from '@sveltejs/kit/hooks';

export const handle: Handle = async ({ event, resolve }) => {
	await ensureAuthSchema();

	const session = await auth.api.getSession({
		headers: event.request.headers
	});

	event.locals.session = session?.session ?? null;
	event.locals.user = session?.user ?? null;

	return svelteKitHandler({
		auth,
		event,
		resolve,
		building
	});
};
