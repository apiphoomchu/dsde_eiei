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
import Latex from "react-latex";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [searchTerm, setSearchTerm] = useState("machine learning");
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  useEffect(() => {
    const fetchSearchResults = async () => {
      if (!searchTerm.trim()) {
        setPapers([]);
        return;
      }

      setLoading(true);

      try {
        const response = await fetch(
          `/api/proxy?searchTerm=${encodeURIComponent(searchTerm)}`,
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
        setCurrentPage(1);
      } catch (error) {
        console.error("Search failed:", error);
        setPapers([]);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchSearchResults, 1000);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentPapers = papers.slice(startIndex, endIndex);

  const totalPages = Math.ceil(papers.length / itemsPerPage);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage((prev) => prev + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage((prev) => prev - 1);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 flex flex-col items-end pt-4">
      <Link href={process.env.NEXT_PUBLIC_VISUALIZATION_URL || ""}>
        <Button className="font-bold gap-1">
          Visualization
          <ArrowRight />
        </Button>
      </Link>

      <div className="max-w-6xl mx-auto space-y-8 mt-4">
        <SearchBar
          value={searchTerm}
          onChange={setSearchTerm}
          isLoading={loading}
        />

        <div className="grid gap-6">
          {currentPapers.map((paper) => (
            <PaperCard
              key={paper.id}
              paper={paper}
              onSelect={setSelectedPaper}
            />
          ))}
        </div>

        {/* Pagination Controls */}
        <div className="flex justify-between items-center mt-4">
          <Button
            onClick={handlePreviousPage}
            disabled={currentPage === 1}
            className="disabled:opacity-50"
          >
            Previous
          </Button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <Button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="disabled:opacity-50"
          >
            Next
          </Button>
        </div>

        <Dialog
          open={!!selectedPaper}
          onOpenChange={() => setSelectedPaper(null)}
        >
          <DialogContent className="max-w-4xl h-[80vh]">
            <DialogHeader>
              <DialogTitle>
                <Latex>{selectedPaper?.title}</Latex>
              </DialogTitle>
              <DialogDescription>
                {selectedPaper?.date &&
                  `Published on ${selectedPaper?.date.replace(/;$/, "")}`}
              </DialogDescription>
            </DialogHeader>
            <div className="grid grid-cols-2 gap-6 h-full overflow-hidden">
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
