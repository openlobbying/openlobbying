const FALLBACK = '/account';
const BASE = 'http://local.invalid';

/**
 * The `redirectTo` target if it's a path on this site, else `/account`. Parsing against a
 * placeholder origin catches what browsers treat as another host: `//host`, `/\host`, and
 * the same with tabs or newlines inside.
 */
export function localRedirectTarget(value: string | null): string {
	if (!value?.startsWith('/')) {
		return FALLBACK;
	}

	const url = new URL(value, BASE);
	return url.origin === BASE ? url.pathname + url.search + url.hash : FALLBACK;
}
