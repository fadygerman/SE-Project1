import { useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Currency } from "@/openapi/models/Currency";

export function CurrencySelector({ onCurrencyChange, value }: { onCurrencyChange: (value: string) => void; value: string }) {
  const [currency, setCurrency] = useState<string>(value);
  const currencyCodes = Object.values(Currency);

  const handleChange = (newValue: string) => {
    setCurrency(newValue);         // Update local selection
    onCurrencyChange(newValue);    // Notify parent about the new currency
  };

  return (
      <Select value={currency} onValueChange={handleChange}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Currency" />
          </SelectTrigger>
          <SelectContent>
            {currencyCodes.map((code) => (
              <SelectItem key={code} value={code}>
                {code} - {getCurrencyDisplayName(code)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
  );
}

// Helper function
function getCurrencyDisplayName(currency: string): string {
  const displayNames: Record<string, string> = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'CAD': 'Canadian Dollar',
    'AUD': 'Australian Dollar',
    'CHF': 'Swiss Franc',
    'CNY': 'Chinese Yuan',
    'MXN': 'Mexican Peso',
    'INR': 'Indian Rupee',
    'BRL': 'Brazilian Real',
    'ZAR': 'South African Rand',
  };
  return displayNames[currency] || currency;
}
