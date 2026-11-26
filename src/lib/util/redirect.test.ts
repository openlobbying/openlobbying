import assert from 'node:assert/strict';
import { test } from 'node:test';
import { localRedirectTarget } from './redirect.ts';

test('keeps local paths, with their query and hash', () => {
	assert.equal(localRedirectTarget('/admin/users'), '/admin/users');
	assert.equal(localRedirectTarget('/admin/users?page=2#top'), '/admin/users?page=2#top');
});

test('falls back to /account when there is no target', () => {
	assert.equal(localRedirectTarget(null), '/account');
	assert.equal(localRedirectTarget(''), '/account');
});

test('refuses targets on another host', () => {
	for (const target of [
		'https://evil.example/',
		'//evil.example/',
		'/\\evil.example/',
		'/\t/evil.example/',
		'/\n/evil.example/',
		'javascript:alert(1)',
		'evil.example'
	]) {
		assert.equal(localRedirectTarget(target), '/account', target);
	}
});
