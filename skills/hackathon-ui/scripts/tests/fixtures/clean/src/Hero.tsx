import { ArrowRight } from "lucide-react";
export function Hero() {
  return (
    <section className="bg-bg text-text">
      <h1 className="text-6xl tracking-tight">The incident desk for teams that ship at night</h1>
      <p className="text-lg text-text-2">Page the right person and get a draft postmortem in 40 seconds.</p>
      <button className="bg-accent focus-visible:ring-2 transition-transform active:scale-[.98]">Start free <ArrowRight size={16} /></button>
      <img src="/app.png" alt="Relay incident view showing INC-2041" />
    </section>
  );
}
