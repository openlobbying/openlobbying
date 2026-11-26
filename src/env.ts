import { defineEnvVars } from '@sveltejs/kit/env';

// Server-only variables, read when the app starts and available from $app/env/private.
// Each is optional here; src/lib/server/auth.ts decides what happens when one is unset.
const optional = (value: string | undefined) => value || undefined;

export const variables = defineEnvVars({
	BETTER_AUTH_SECRET: { schema: optional },
	BETTER_AUTH_URL: { schema: optional },
	MUCKRAKE_DATABASE_URL: { schema: optional },
	OPENLOBBYING_ADMIN_API_SECRET: { schema: optional }
});
