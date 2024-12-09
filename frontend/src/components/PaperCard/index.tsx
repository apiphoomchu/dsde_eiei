import React from "react";
import {
	Card,
	CardHeader,
	CardTitle,
	CardDescription,
	CardContent,
	CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, FileText } from "lucide-react";
import { Paper } from "@/types/types";
import { parseString } from "@/utils";

interface Props {
	paper: Paper;
	onSelect: (paper: Paper) => void;
}

export const PaperCard = ({ paper, onSelect }: Props) => {
	return (
		<Card
			className="hover:shadow-lg transition-shadow cursor-pointer"
			onClick={() => onSelect(paper)}
		>
			<CardHeader>
				<div className="flex justify-between items-start">
					<div className="space-y-1">
						<CardTitle className="text-xl">{paper.title}</CardTitle>
						<CardDescription className="text-sm">
							{parseString(paper.authors).join(", ")}
						</CardDescription>
					</div>
					{paper.date && (
						<div className="flex items-center text-sm text-gray-500">
							<Calendar className="w-4 h-4 mr-1" />
							{paper.date}
						</div>
					)}
				</div>
			</CardHeader>
			<CardContent>
				<p className="text-gray-600 line-clamp-3">{paper.abstract}</p>
			</CardContent>
			<CardFooter className="flex justify-between items-center">
				<div className="flex gap-2 flex-wrap">
					{paper.keywords &&
						parseString(paper.keywords).map((keyword, idx) => (
							<Badge key={idx} variant="secondary">
								{keyword}
							</Badge>
						))}
				</div>
				{paper.pdf && (
					<a
						href={paper.pdf}
						target="_blank"
						rel="noopener noreferrer"
						className="flex items-center text-sm text-blue-600 hover:text-blue-800"
						onClick={(e) => e.stopPropagation()}
					>
						<FileText className="w-4 h-4 mr-1" />
						PDF
					</a>
				)}
			</CardFooter>
		</Card>
	);
};
