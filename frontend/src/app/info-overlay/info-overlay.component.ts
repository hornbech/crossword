import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-info-overlay',
  template: `
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      (click)="close.emit()"
    >
      <div
        class="bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl max-w-md w-full mx-4 p-6"
        (click)="$event.stopPropagation()"
      >
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-lg font-semibold text-[#e6edf3]">About</h2>
          <button
            (click)="close.emit()"
            class="text-[#8b949e] hover:text-[#e6edf3] transition-colors text-xl leading-none"
          >
            &times;
          </button>
        </div>

        <p class="text-sm text-[#8b949e] leading-relaxed mb-5">
          A deterministic crossword generator powered by the
          <span class="text-[#58a6ff]">Dancing Links (DLX)</span> algorithm.
          Enter a seed to generate a unique puzzle — the same seed always
          produces the same crossword.
        </p>

        <div class="grid grid-cols-2 gap-3 mb-5">
          <div class="bg-[#0d1117] border border-[#30363d] rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-[#3fb950]">{{ totalVisitors() }}</div>
            <div class="text-xs text-[#8b949e] mt-1">Total Visitors</div>
          </div>
          <div class="bg-[#0d1117] border border-[#30363d] rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-[#58a6ff]">{{ activeUsers() }}</div>
            <div class="text-xs text-[#8b949e] mt-1">Online Now</div>
          </div>
        </div>

        <div class="border-t border-[#30363d] pt-4">
          <div class="flex items-center gap-2 text-xs text-[#656d76]">
            <span>Built with Angular + FastAPI + DLX</span>
            <span>&middot;</span>
            <a
              href="/api/docs"
              target="_blank"
              class="text-[#58a6ff] hover:underline"
              >API Docs</a
            >
          </div>
        </div>
      </div>
    </div>
  `,
})
export class InfoOverlayComponent {
  readonly totalVisitors = input(0);
  readonly activeUsers = input(0);
  readonly close = output<void>();
}
