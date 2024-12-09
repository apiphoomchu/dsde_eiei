export interface Paper {
	id: string;
	title: string;
	abstract: string;
	authors: string;
	keywords: string;
	date?: string;
	pdf?: string;
}

export interface Message {
	role: "user" | "assistant";
	content: string;
}
