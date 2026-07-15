import { useEffect, useRef } from "react";

interface ConfirmationDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  danger?: boolean;
}

export function ConfirmationDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
  danger = false,
}: ConfirmationDialogProps) {
  const confirmRef = useRef<HTMLButtonElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) confirmRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (!open) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onCancel();
        return;
      }
      // Simple focus trap: only two focusable elements (cancel, confirm),
      // so Tab/Shift+Tab just needs to cycle between them rather than
      // escape to whatever's behind the overlay.
      if (e.key === "Tab") {
        const focusables = [cancelRef.current, confirmRef.current].filter(
          (el): el is HTMLButtonElement => el !== null
        );
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (!first || !last) return;
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-900/40 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirmation-dialog-title"
      aria-describedby="confirmation-dialog-description"
    >
      <div ref={dialogRef} className="w-full max-w-sm rounded-xl bg-white p-6 shadow-lg">
        <h3 id="confirmation-dialog-title" className="font-display text-base font-semibold text-neutral-900">
          {title}
        </h3>
        <p id="confirmation-dialog-description" className="mt-2 text-sm text-neutral-500">
          {description}
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <button
            ref={cancelRef}
            onClick={onCancel}
            className="rounded-lg px-3.5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-100"
          >
            {cancelLabel}
          </button>
          <button
            ref={confirmRef}
            onClick={onConfirm}
            className={
              danger
                ? "rounded-lg bg-danger-600 px-3.5 py-2 text-sm font-medium text-white hover:bg-danger-700"
                : "rounded-lg bg-primary-600 px-3.5 py-2 text-sm font-medium text-white hover:bg-primary-700"
            }
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
