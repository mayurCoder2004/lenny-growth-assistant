import { useEffect, useRef } from "react";

function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
}) {
  const cancelButtonRef = useRef(null);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    cancelButtonRef.current?.focus();

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onCancel();
      }
    }

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onCancel]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[80] flex items-center justify-center px-4 py-6"
      role="presentation"
    >
      <button
        type="button"
        className="absolute inset-0 cursor-default bg-[#05070b]/70 backdrop-blur-sm"
        onClick={onCancel}
        aria-label="Close confirmation dialog"
      />

      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-description"
        className="relative w-full max-w-[420px] rounded-xl border border-[#27303e] bg-[#10151e] p-5 shadow-[0_30px_90px_rgba(0,0,0,0.46),0_1px_0_rgba(255,255,255,0.04)_inset] sm:p-6"
      >
        <div className="mb-5">
          <p
            id="confirm-dialog-title"
            className="text-lg font-semibold leading-7 text-[#f0f3f8]"
          >
            {title}
          </p>

          <p
            id="confirm-dialog-description"
            className="mt-2 text-sm leading-6 text-[#9aa6b8]"
          >
            {description}
          </p>
        </div>

        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button
            type="button"
            ref={cancelButtonRef}
            onClick={onCancel}
            className="rounded-lg border border-[#27303e] bg-[#111722] px-4 py-2.5 text-sm font-semibold text-[#cbd4e2] transition duration-150 hover:border-[#3a4658] hover:bg-[#171e29] active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/15"
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            onClick={onConfirm}
            className="rounded-lg border border-[#6b2f3b] bg-[#4a1d28] px-4 py-2.5 text-sm font-semibold text-[#ffd7df] transition duration-150 hover:border-[#8a3c4b] hover:bg-[#5a2431] active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#e2b8c7]/20"
          >
            {confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}

export default ConfirmDialog;
