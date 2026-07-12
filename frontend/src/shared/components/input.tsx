import { forwardRef } from "react";

import { cn } from "@/shared/utils/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, id, "aria-describedby": describedBy, ...props }, ref) => {
    const errorId = error && id ? `${id}-error` : undefined;

    return (
      <div className="space-y-1.5">
        <input
          id={id}
          ref={ref}
          aria-invalid={Boolean(error)}
          aria-describedby={cn(describedBy, errorId) || undefined}
          className={cn(
            "h-10 w-full rounded-md border bg-canvas-overlay px-3 text-sm text-ink placeholder:text-ink-faint",
            "transition-colors focus-visible:outline-none",
            error
              ? "border-signal-danger focus-visible:outline-signal-danger"
              : "border-canvas-border focus-visible:outline-trace",
            className,
          )}
          {...props}
        />
        {error && (
          <p id={errorId} className="text-xs text-signal-danger">
            {error}
          </p>
        )}
      </div>
    );
  },
);
Input.displayName = "Input";
