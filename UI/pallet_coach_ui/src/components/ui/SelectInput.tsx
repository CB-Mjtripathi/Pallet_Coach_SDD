import type { SelectHTMLAttributes } from "react";

type SelectInputProps = SelectHTMLAttributes<HTMLSelectElement>;

export function SelectInput({ className = "", children, ...rest }: SelectInputProps): JSX.Element {
  return (
    <select className={`select-input ${className}`.trim()} {...rest}>
      {children}
    </select>
  );
}
