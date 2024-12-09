export function parseString(input: string): string[] {
	// Handle input wrapped in array-like format (e.g., "['Stark D.V.']")
	if (input.startsWith("['") && input.endsWith("']")) {
		// Replace single quotes with double quotes, parse as JSON, and return the result
		const sanitized = input.replace(/'/g, '"');
		return JSON.parse(sanitized);
	}

	// Handle comma-separated format (e.g., "M. A. Ganaie, Vrushank Ahire")
	return input
		.split(",") // Split by commas
		.map((name) => name.trim()); // Trim whitespace from each name
}
