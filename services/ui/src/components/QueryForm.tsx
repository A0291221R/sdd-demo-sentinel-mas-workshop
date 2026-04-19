import { useState } from "react";

interface QueryFormProps {
  onSubmit: (query: string) => void;
  onClearError: () => void;
  loading: boolean;
}

export default function QueryForm({ onSubmit, onClearError, loading }: QueryFormProps) {
  const [value, setValue] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setValue(e.target.value);
    onClearError();
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onClearError();
    if (!value.trim()) {
      setValidationError("Query cannot be empty");
      return;
    }
    setValidationError(null);
    onSubmit(value.trim());
    setValue("");
  }

  return (
    <form onSubmit={handleSubmit} className="query-form">
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder="Enter a security query…"
        disabled={loading}
        className="query-input"
      />
      <button type="submit" disabled={loading} className="query-button">
        {loading ? "Loading…" : "Submit"}
      </button>
      {validationError && (
        <p className="validation-error">{validationError}</p>
      )}
    </form>
  );
}
