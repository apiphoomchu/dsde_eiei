import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Maximize2 } from "lucide-react";
import { PDFDialog } from "../PDFDialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Paper } from "@/types/types";
import { parseString } from "@/utils";

interface Props {
	paper: Paper;
}

export const PaperDetails = ({ paper }: Props) => {
	const [isPDFOpen, setIsPDFOpen] = useState(false);

	return (
		<ScrollArea className="h-[calc(80vh-8rem)]">
			<div className="space-y-6">
				<div>
					<h3 className="text-lg font-semibold">Abstract</h3>
					<p className="mt-2 text-gray-600 text-wrap">{paper.abstract}</p>
				</div>

				<div>
					<h3 className="text-lg font-semibold">Authors</h3>
					<p className="mt-2 text-gray-600 text-wrap">
						{parseString(paper.authors).join(", ")}
					</p>
				</div>

				<div>
					<h3 className="text-lg font-semibold">Keywords</h3>
					<div className="mt-2 flex flex-wrap gap-2">
						{parseString(paper.keywords).map((keyword, idx) => (
							<Badge key={idx} variant="secondary">
								{keyword}
							</Badge>
						))}
					</div>
				</div>

				{paper.pdf && (
					<div>
						<h3 className="text-lg font-semibold mb-1">PDF Preview</h3>
						<div className="flex items-center justify-between">
							<div className="flex gap-2">
								<Button
									variant="outline"
									size="sm"
									onClick={() => setIsPDFOpen(true)}
									className="flex items-center gap-2"
								>
									<Maximize2 className="w-4 h-4" />
									Open PDF
								</Button>
								<a
									href={paper.pdf}
									target="_blank"
									rel="noopener noreferrer"
									className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
								>
									<FileText className="w-4 h-4" />
									Download
								</a>
							</div>
						</div>

						<PDFDialog
							url={paper.pdf}
							isOpen={isPDFOpen}
							onClose={() => setIsPDFOpen(false)}
							title={paper.title}
						/>
					</div>
				)}
			</div>
		</ScrollArea>
	);
};
