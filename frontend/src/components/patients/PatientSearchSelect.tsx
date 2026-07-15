import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, X } from "lucide-react";
import { searchPatients } from "@/api/patients";
import { Input } from "@/components/ui/input";
import { PatientInfoCard } from "@/components/ui/PatientInfoCard";
import { LoadingState } from "@/components/ui/LoadingState";
import type { PatientSummary } from "@/lib/types";

interface PatientSearchSelectProps {
  selected: PatientSummary | null;
  onSelect: (patient: PatientSummary | null) => void;
}

/**
 * Debounced (300ms) search against the existing GET /patients?name=
 * endpoint from Module 5 — no backend change needed. Not built as a
 * generic reusable "SearchSelect" since patient search has a distinct
 * result shape (PatientInfoCard); a truly generic version can be
 * extracted later if a second use case actually needs it (YAGNI).
 */
export function PatientSearchSelect({ selected, onSelect }: PatientSearchSelectProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  const { data: results, isFetching } = useQuery({
    queryKey: ["patients", "search", debouncedQuery],
    queryFn: () => searchPatients({ name: debouncedQuery }),
    enabled: debouncedQuery.trim().length >= 2,
  });

  if (selected) {
    return (
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <PatientInfoCard patient={selected} />
        </div>
        <button
          type="button"
          onClick={() => {
            onSelect(null);
            setQuery("");
          }}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-neutral-500 hover:bg-neutral-100"
          aria-label="Change patient"
          title="Change patient"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" aria-hidden="true" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search patient by name…"
          className="pl-9"
          aria-label="Search patient by name"
        />
      </div>

      {debouncedQuery.trim().length >= 2 && (
        <div className="absolute z-10 mt-1 w-full rounded-lg border border-neutral-200 bg-white shadow-md">
          {isFetching ? (
            <LoadingState label="Searching…" />
          ) : results && results.length > 0 ? (
            <ul role="listbox" className="max-h-64 overflow-y-auto py-1">
              {results.map((patient) => (
                <li key={patient.id}>
                  <button
                    type="button"
                    role="option"
                    aria-selected={false}
                    onClick={() => {
                      onSelect(patient);
                      setQuery("");
                    }}
                    className="flex w-full items-center justify-between px-4 py-2.5 text-left text-sm hover:bg-neutral-50 focus-visible:outline-none focus-visible:bg-neutral-50"
                  >
                    <span className="font-medium text-neutral-900">{patient.full_name}</span>
                    <span className="text-neutral-500">
                      {patient.age} yrs · {patient.village}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="px-4 py-3 text-sm text-neutral-500">No patients found matching "{debouncedQuery}".</p>
          )}
        </div>
      )}
    </div>
  );
}
