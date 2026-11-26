import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { mdsvex } from 'mdsvex';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig, loadEnv } from 'vite';

const rootDir = fileURLToPath(new URL('.', import.meta.url));

const mdsvexConfig = {
	extensions: ['.svx'],
	layout: path.resolve(rootDir, 'src/lib/components/MarkdownPage.svelte')
};

export default defineConfig(({ mode }) => {
	// Read OPENLOBBYING_API_URL from the shell or the repo-root .env (the shell wins).
	const env = loadEnv(mode, process.cwd(), '');
	const apiTarget = env.OPENLOBBYING_API_URL || 'http://127.0.0.1:8000';

	return {
		plugins: [
			sveltekit({
				adapter: adapter(),
				// SvelteKit 3 replaced $lib with #lib; this keeps the existing $lib imports.
				alias: { $lib: 'src/lib' },
				extensions: ['.svelte', '.svx'],
				preprocess: [vitePreprocess(), mdsvex(mdsvexConfig)]
			})
		],
		server: {
			proxy: {
				'/api': {
					target: apiTarget,
					changeOrigin: true,
					rewrite: (path) => path.replace(/^\/api/, '')
				}
			}
		}
	};
});
