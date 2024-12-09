import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Loader2, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Paper, Message } from "@/types/types";

export interface Props {
	paper: Paper;
}

export const ChatInterface = ({ paper }: Props) => {
	const [messages, setMessages] = useState<Message[]>([]);
	const [newMessage, setNewMessage] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const handleSendMessage = async () => {
		if (!newMessage.trim()) return;

		const userMessage: Message = {
			role: "user",
			content: newMessage,
		};

		setMessages((prev) => [...prev, userMessage]);
		setNewMessage("");
		setIsLoading(true);
		setError(null);

		try {
			const response = await fetch("/api/chat", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					message: newMessage,
					paper,
				}),
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error || "Failed to get response");
			}

			const data = await response.json();

			setMessages((prev) => [
				...prev,
				{
					role: "assistant",
					content: data.response,
				},
			]);
		} catch (error) {
			console.error("Error:", error);
			setError(
				error instanceof Error
					? error.message
					: "An error occurred while sending your message"
			);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="flex flex-col h-[400px]">
			<ScrollArea className="flex-1 p-4 border rounded-lg mb-4">
				{messages.map((message, idx) => (
					<div
						key={idx}
						className={`mb-4 ${
							message.role === "user" ? "text-right" : "text-left"
						}`}
					>
						<div
							className={`inline-block p-3 rounded-lg ${
								message.role === "user"
									? "bg-blue-600 text-white"
									: "bg-gray-200 text-gray-800"
							}`}
						>
							{message.content}
						</div>
					</div>
				))}
				{isLoading && (
					<div className="flex items-center justify-center">
						<Loader2 className="w-6 h-6 animate-spin" />
					</div>
				)}
			</ScrollArea>

			{error && (
				<Alert variant="destructive" className="mb-4">
					<AlertCircle className="h-4 w-4" />
					<AlertDescription>{error}</AlertDescription>
				</Alert>
			)}

			<div className="flex gap-2">
				<Textarea
					placeholder="Ask questions about this paper..."
					value={newMessage}
					onChange={(e) => setNewMessage(e.target.value)}
					className="flex-1"
					onKeyDown={(e) => {
						if (e.key === "Enter" && !e.shiftKey) {
							e.preventDefault();
							handleSendMessage();
						}
					}}
				/>
				<Button onClick={handleSendMessage} disabled={isLoading}>
					<Send className="w-4 h-4" />
				</Button>
			</div>
		</div>
	);
};
