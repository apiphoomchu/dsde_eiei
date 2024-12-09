import OpenAI from "openai";
import { NextResponse } from "next/server";

// Initialize OpenAI client
const openai = new OpenAI({
	apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: Request) {
	try {
		if (!process.env.OPENAI_API_KEY) {
			return NextResponse.json(
				{ error: "OpenAI API key not configured" },
				{ status: 500 }
			);
		}

		const body = await req.json();
		const { message, paper } = body;

		// Create a system message that includes context about the paper
		const systemMessage = `You are an AI assistant helping to discuss the following research paper:
Title: ${paper.title}
Abstract: ${paper.abstract}
Authors: ${paper.authors}

Please provide accurate and helpful responses about this paper. You can reference specific parts of the paper and explain complex concepts in an understandable way.`;

		const completion = await openai.chat.completions.create({
			model: "gpt-4", // or "gpt-3.5-turbo" for a cheaper but still good option
			messages: [
				{ role: "system", content: systemMessage },
				{ role: "user", content: message },
			],
			temperature: 0.7,
			max_tokens: 500,
		});

		return NextResponse.json({
			response: completion.choices[0].message.content,
		});
	} catch (error) {
		console.error("OpenAI API Error:", error);

		if (error instanceof OpenAI.APIError) {
			return NextResponse.json(
				{ error: "OpenAI API error: " + error.message },
				{ status: error.status || 500 }
			);
		}

		return NextResponse.json(
			{ error: "An error occurred while processing your request" },
			{ status: 500 }
		);
	}
}
