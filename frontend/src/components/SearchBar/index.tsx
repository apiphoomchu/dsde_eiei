import React from "react";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";

export interface Props {
	value: string;
	onChange: (value: string) => void;
	isLoading: boolean;
}

export const SearchBar = ({ value, onChange, isLoading }: Props) => {
	return (
		<div className="space-y-4">
			<h1 className="text-4xl font-bold text-center">Quantum Physics Papers</h1>
			<Input
				placeholder="Search papers by title..."
				className="max-w-2xl mx-auto"
				value={value}
				onChange={(e) => onChange(e.target.value)}
			/>
			{isLoading && (
				<div className="absolute right-3 top-1/2 -translate-y-1/2">
					<Loader2 className="w-4 h-4 animate-spin text-gray-500" />
				</div>
			)}
		</div>
	);
};
