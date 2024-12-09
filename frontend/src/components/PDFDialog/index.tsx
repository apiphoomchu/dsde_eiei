import React from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { PDFViewer } from "../PDFViewer";

interface Props {
	url: string;
	isOpen: boolean;
	onClose: () => void;
	title?: string;
}

export const PDFDialog = ({ url, isOpen, onClose, title }: Props) => {
	return (
		<Dialog open={isOpen} onOpenChange={onClose}>
			<DialogTitle></DialogTitle>
			<DialogContent className="max-w-[90vw] w-[1000px] h-[90vh] flex flex-col p-0">
				<div className="flex justify-between items-center p-4 border-b">
					<h2 className="text-lg font-semibold truncate pr-4">
						{title || "PDF Preview"}
					</h2>
				</div>
				<div className="flex-1 overflow-hidden">
					<PDFViewer url={url} />
				</div>
			</DialogContent>
		</Dialog>
	);
};
