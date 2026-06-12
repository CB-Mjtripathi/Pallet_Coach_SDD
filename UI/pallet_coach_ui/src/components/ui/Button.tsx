import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
}

export function Button({ variant = "secondary", children, className = "", type = "button", ...rest }: ButtonProps): JSX.Element {
  const variantClass =
    variant === "primary" ? "btn-primary" : variant === "ghost" ? "btn-ghost" : "";

  return (
    <button type={type} className={`btn ${variantClass} ${className}`.trim()} {...rest}>
      {children}
    </button>
  );
}
