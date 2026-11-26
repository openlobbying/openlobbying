import { redirect } from '@sveltejs/kit';
import { localRedirectTarget } from '#lib/util/redirect.js';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
	const redirectTo = localRedirectTarget(url.searchParams.get('redirectTo'));

	if (locals.user) {
		redirect(303, redirectTo);
	}

	return { redirectTo };
};
