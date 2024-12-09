export function parseString(input: string): string[] {
	// Return empty array if input is empty or not a string
	if (!input || typeof input !== "string") {
		return [];
	}

	try {
		// Handle input wrapped in array-like format (e.g., "['Stark D.V.']")
		if (input.startsWith("['") && input.endsWith("']")) {
			// Replace single quotes with double quotes and parse as JSON
			const sanitized = input.replace(/'/g, '"');
			try {
				const parsed = JSON.parse(sanitized);
				// Validate that the parsed result is an array of strings
				if (
					Array.isArray(parsed) &&
					parsed.every((item) => typeof item === "string")
				) {
					return parsed;
				}
				return []; // Return empty array if parsed result is invalid
			} catch {
				// If JSON parsing fails, treat it as a single string
				return [input];
			}
		}

		// Handle comma-separated format (e.g., "M. A. Ganaie, Vrushank Ahire")
		const names = input
			.split(",")
			.map((name) => name.trim())
			.filter((name) => name.length > 0); // Filter out empty strings

		return names;
	} catch {
		// Catch any unexpected errors and return empty array
		return [];
	}
}
