import { useEffect } from "react";

function Toast({ toast, onDismiss }) {
  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      onDismiss(toast.id);
    }, 3600);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [onDismiss, toast.id]);

  const success = toast.type === "success";

  return (
    <div
      role="status"
      aria-live="polite"
      className={[
        "pointer-events-auto flex min-h-[48px] w-full items-start gap-3 rounded-xl border bg-[#10151e] px-4 py-3 text-sm shadow-[0_18px_50px_rgba(0,0,0,0.36),0_1px_0_rgba(255,255,255,0.04)_inset]",
        success
          ? "border-[#2f4539] text-[#d7eadf]"
          : "border-[#4a2d38] text-[#e2b8c7]",
      ].join(" ")}
    >
      <span
        className={[
          "mt-1 h-2 w-2 shrink-0 rounded-full",
          success ? "bg-[#74c69d]" : "bg-[#e2b8c7]",
        ].join(" ")}
        aria-hidden="true"
      />

      <div className="min-w-0 flex-1 leading-6">
        {toast.message}
      </div>

      <button
        type="button"
        onClick={() => onDismiss(toast.id)}
        className="rounded-md px-1.5 text-[#8c97a9] transition hover:bg-[#171e29] hover:text-[#edf1f7] focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/15"
        aria-label="Dismiss notification"
      >
        x
      </button>
    </div>
  );
}

function ToastContainer({ toasts, onDismiss }) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      className="pointer-events-none fixed inset-x-3 bottom-3 z-[90] flex flex-col gap-2 sm:inset-x-auto sm:right-5 sm:bottom-5 sm:w-[360px]"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          toast={toast}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
}

export default ToastContainer;
