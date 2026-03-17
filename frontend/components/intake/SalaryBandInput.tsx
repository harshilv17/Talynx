"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SalaryBandInputProps {
  minValue: number;
  maxValue: number;
  currency: string;
  onMinChange: (value: number) => void;
  onMaxChange: (value: number) => void;
  onCurrencyChange: (value: string) => void;
}

export function SalaryBandInput({
  minValue,
  maxValue,
  currency,
  onMinChange,
  onMaxChange,
  onCurrencyChange,
}: SalaryBandInputProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="sm:col-span-1">
          <Label htmlFor="currency">Currency</Label>
          <Select value={currency} onValueChange={onCurrencyChange}>
            <SelectTrigger id="currency">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="USD">USD</SelectItem>
              <SelectItem value="EUR">EUR</SelectItem>
              <SelectItem value="GBP">GBP</SelectItem>
              <SelectItem value="CAD">CAD</SelectItem>
              <SelectItem value="AUD">AUD</SelectItem>
              <SelectItem value="INR">INR</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="sm:col-span-1">
          <Label htmlFor="salary_min">Minimum</Label>
          <Input
            id="salary_min"
            type="number"
            value={minValue || ""}
            onChange={(e) => onMinChange(Number(e.target.value))}
            placeholder="80000"
          />
        </div>

        <div className="sm:col-span-1">
          <Label htmlFor="salary_max">Maximum</Label>
          <Input
            id="salary_max"
            type="number"
            value={maxValue || ""}
            onChange={(e) => onMaxChange(Number(e.target.value))}
            placeholder="120000"
          />
        </div>
      </div>
    </div>
  );
}
