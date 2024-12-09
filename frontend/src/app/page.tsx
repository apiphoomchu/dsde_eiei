"use client";

import React, { useEffect, useState } from "react";
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	DialogDescription,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PaperCard } from "@/components/PaperCard";
import { PaperDetails } from "@/components/PaperDetails";
import { ChatInterface } from "@/components/ChatInterface";
import { SearchBar } from "@/components/SearchBar";
import { Paper } from "@/types/types";

export default function Home() {
	const [searchTerm, setSearchTerm] = useState("");
	const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
	const [papers, setPapers] = useState<Paper[]>([]);
	const [loading, setLoading] = useState(false);

	useEffect(() => {
		const fetchSearchResults = async () => {
			if (!searchTerm.trim()) {
				setPapers([]);
				return;
			}

			setLoading(true);

			try {
				const response = await fetch(
					`http://127.0.0.1:8000/search/${encodeURIComponent(searchTerm)}`,
					{
						method: "GET",
						headers: {
							"Content-Type": "application/json",
						},
					}
				);

				if (!response.ok) {
					throw new Error("Search request failed");
				}

				const data = await response.json();
				setPapers(data.results);
			} catch (error) {
				console.error("Search failed:", error);
				setPapers([]);
			} finally {
				setLoading(false);
			}
		};

		// Debounce the search to avoid too many requests
		const timeoutId = setTimeout(fetchSearchResults, 1000);

		return () => clearTimeout(timeoutId);
	}, [searchTerm]);

	const filteredPapers = papers.filter(
		(paper) =>
			paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
			paper.abstract.toLowerCase().includes(searchTerm.toLowerCase()) ||
			paper.authors.toLowerCase().includes(searchTerm.toLowerCase())
	);

	return (
		<div className="min-h-screen bg-gray-50 p-8">
			<div className="max-w-6xl mx-auto space-y-8">
				<SearchBar
					value={searchTerm}
					onChange={setSearchTerm}
					isLoading={loading}
				/>

				<div className="grid gap-6">
					{filteredPapers.map((paper) => (
						<PaperCard
							key={paper.id}
							paper={paper}
							onSelect={setSelectedPaper}
						/>
					))}
				</div>

				<Dialog
					open={!!selectedPaper}
					onOpenChange={() => setSelectedPaper(null)}
				>
					<DialogContent className="max-w-4xl h-[80vh]">
						<DialogHeader>
							<DialogTitle>{selectedPaper?.title}</DialogTitle>
							<DialogDescription>
								{selectedPaper?.date &&
									`Published on ${selectedPaper?.date.replace(/;$/, "")}`}
							</DialogDescription>
						</DialogHeader>
						<div className="grid grid-cols-2 gap-6 mt-6 h-full overflow-hidden">
							<ScrollArea className="w-full">
								{selectedPaper && <PaperDetails paper={selectedPaper} />}
							</ScrollArea>
							<div className="border-l pl-6">
								<h3 className="text-lg font-semibold mb-4">
									Chat about this paper
								</h3>
								{selectedPaper && <ChatInterface paper={selectedPaper} />}
							</div>
						</div>
					</DialogContent>
				</Dialog>
			</div>
		</div>
	);
}
