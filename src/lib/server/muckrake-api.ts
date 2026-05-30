export function getOpenLobbyingApiBaseUrl(): string {
	return process.env.OPENLOBBYING_API_URL || 'http://127.0.0.1:8000';
}
