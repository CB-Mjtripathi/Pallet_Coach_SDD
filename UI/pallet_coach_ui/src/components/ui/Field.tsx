import type { ReactNode } from "react";

interface FieldProps {
  label: string;
  required?: boolean;
  helperText?: string;
  children: ReactNode;
}

export function Field({ label, required, helperText, children }: FieldProps): JSX.Element {
  return (
    <label className="field">
      <span className="field-label">
        {label}
        {required ? <span className="ml-1 text-[rgb(var(--danger))]">*</span> : null}
      </span>
      {children}
      {helperText ? <span className="field-help">{helperText}</span> : null}
    </label>
  );
}
