import type { InputHTMLAttributes } from "react";

type TextInputProps = InputHTMLAttributes<HTMLInputElement>;

export function TextInput({ className = "", ...rest }: TextInputProps): JSX.Element {
  return <input className={`text-input ${className}`.trim()} {...rest} />;
}
