import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Read OPENLOBBYING_API_URL from the shell or the repo-root .env (the shell wins).
	const env = loadEnv(mode, process.cwd(), '');
	const apiTarget = env.OPENLOBBYING_API_URL || 'http://127.0.0.1:8000';

	return {
		plugins: [sveltekit()],
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
