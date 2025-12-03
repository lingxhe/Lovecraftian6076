"use client";

import { useEffect, useRef } from "react";

interface Dice3DOverlayProps {
  show: boolean;
  onClose: () => void;
  rollNotation?: string;
  onResult?: (value: number) => void;
}

export function Dice3DOverlay({ show, onClose, rollNotation = "1d100", onResult }: Dice3DOverlayProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!show) return;

    let box: any;
    let cancelled = false;

    (async () => {
      try {
        const mod = await import("@3d-dice/dice-box");
        const DiceBox = (mod as any).default || (mod as any);

        // v1.1+ API: constructor takes a single config object
        box = new DiceBox({
          container: "#dice-box-3d-container",
          assetPath: "/assets/", // served from public/assets/*
          themeColor: "#f97316",
          lightIntensity: 1.1,
          scale: 5,
        });

        await box.init();
        if (cancelled) return;

        const results = await box.roll(rollNotation);
        if (!cancelled && onResult && Array.isArray(results)) {
          try {
            const total = results.reduce(
              (sum: number, r: any) => sum + (typeof r?.value === "number" ? r.value : 0),
              0
            );
            onResult(total);
          } catch (e) {
            console.error("Dice3DOverlay parse result error:", e);
          }
        }
      } catch (err) {
        console.error("Dice3DOverlay init error:", err);
      }
    })();

    return () => {
      cancelled = true;
      if (box && typeof box.clear === "function") {
        try {
          box.clear();
        } catch {
          // ignore
        }
      }
    };
  }, [show]);

  if (!show) return null;

  return (
    <div
      className="fixed inset-0 z-50 cursor-pointer"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/60" />
      <div className="relative z-10 w-full h-full pointer-events-none">
        <div
          id="dice-box-3d-container"
          ref={containerRef}
          className="w-full h-full"
        />
      </div>
    </div>
  );
}


