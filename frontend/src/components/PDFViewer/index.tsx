import React, { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
	"pdfjs-dist/build/pdf.worker.min.mjs",
	import.meta.url
).toString();

interface Props {
	url: string;
}

export const PDFViewer = ({ url }: Props) => {
	const [numPages, setNumPages] = useState<number | null>(null);
	const [pageNumber, setPageNumber] = useState(1);
	const [loading, setLoading] = useState(true);

	const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
		setNumPages(numPages);
		setLoading(false);
	};

	const goToPrevPage = () => {
		setPageNumber((prev) => Math.max(prev - 1, 1));
	};

	const goToNextPage = () => {
		setPageNumber((prev) => Math.min(prev + 1, numPages || 1));
	};

	return (
		<div className="h-full flex flex-col">
			<div className="flex-1 overflow-auto p-4">
				<Document
					file={url}
					onLoadSuccess={onDocumentLoadSuccess}
					loading={
						<div className="flex items-center justify-center p-4">
							<Loader2 className="w-6 h-6 animate-spin" />
						</div>
					}
					error={
						<div className="text-red-500 p-4 text-center">
							Failed to load PDF. Please try again later.
						</div>
					}
					className="flex flex-col items-center"
				>
					<Page
						key={pageNumber}
						pageNumber={pageNumber}
						loading={
							<div className="flex items-center justify-center p-4">
								<Loader2 className="w-6 h-6 animate-spin" />
							</div>
						}
						className="shadow-lg"
						renderTextLayer={false}
						renderAnnotationLayer={false}
					/>
				</Document>
			</div>

			{!loading && (
				<div className="flex items-center justify-center gap-4 p-4 border-t bg-white">
					<Button
						onClick={goToPrevPage}
						disabled={pageNumber <= 1}
						variant="outline"
						size="sm"
					>
						Previous
					</Button>
					<p className="text-sm">
						Page {pageNumber} of {numPages}
					</p>
					<Button
						onClick={goToNextPage}
						disabled={pageNumber >= (numPages || 1)}
						variant="outline"
						size="sm"
					>
						Next
					</Button>
				</div>
			)}
		</div>
	);
};
