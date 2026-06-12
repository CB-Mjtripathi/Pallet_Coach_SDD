import type { ComponentPropsWithoutRef, ElementType, ReactNode } from "react";

type CardProps<T extends ElementType = "section"> = {
  children: ReactNode;
  className?: string;
  as?: T;
} & Omit<ComponentPropsWithoutRef<T>, "as" | "children" | "className">;

export function Card<T extends ElementType = "section">({
  children,
  className = "",
  as,
  ...rest
}: CardProps<T>): JSX.Element {
  const Tag = (as ?? "section") as ElementType;
  return (
    <Tag className={`card ${className}`.trim()} {...rest}>
      {children}
    </Tag>
  );
}
