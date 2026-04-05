import { Component, output } from '@angular/core';
import { FormsModule } from '@angular/forms';

export interface GenerateParams {
  seed: string;
  lang: string;
  difficulty: number;
  size: number;
}

@Component({
  selector: 'app-control-panel',
  imports: [FormsModule],
  template: `
    <form (ngSubmit)="onGenerate()" class="space-y-4">
      <div class="flex flex-wrap items-end gap-4">
        <div class="flex flex-col">
          <label for="lang" class="text-xs font-medium text-[#8b949e] mb-1">Language</label>
          <select
            id="lang"
            [(ngModel)]="lang"
            name="lang"
            class="bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#e6edf3] focus:outline-none focus:border-[#58a6ff] transition-colors"
          >
            <option value="en">English</option>
            <option value="da">Danish</option>
          </select>
        </div>

        <div class="flex flex-col">
          <label for="difficulty" class="text-xs font-medium text-[#8b949e] mb-1"
            >Difficulty</label
          >
          <select
            id="difficulty"
            [(ngModel)]="difficulty"
            name="difficulty"
            class="bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#e6edf3] focus:outline-none focus:border-[#58a6ff] transition-colors"
          >
            <option [ngValue]="1">Easy</option>
            <option [ngValue]="2">Medium</option>
            <option [ngValue]="3">Hard</option>
          </select>
        </div>

        <div class="flex flex-col">
          <label for="size" class="text-xs font-medium text-[#8b949e] mb-1">Grid Size</label>
          <select
            id="size"
            [(ngModel)]="size"
            name="size"
            class="bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#e6edf3] focus:outline-none focus:border-[#58a6ff] transition-colors"
          >
            <option [ngValue]="5">5 x 5</option>
            <option [ngValue]="7">7 x 7</option>
            <option [ngValue]="9">9 x 9</option>
            <option [ngValue]="11">11 x 11</option>
            <option [ngValue]="13">13 x 13</option>
            <option [ngValue]="15">15 x 15</option>
          </select>
        </div>

        <button
          type="submit"
          class="bg-[#238636] hover:bg-[#2ea043] text-white font-medium text-sm px-5 py-2 rounded-lg transition-colors"
        >
          New Puzzle
        </button>
      </div>

      <!-- Advanced toggle -->
      <div>
        <button
          type="button"
          (click)="showAdvanced = !showAdvanced"
          class="text-xs text-[#656d76] hover:text-[#8b949e] transition-colors flex items-center gap-1"
        >
          <svg
            class="w-3 h-3 transition-transform"
            [class.rotate-90]="showAdvanced"
            viewBox="0 0 16 16"
            fill="currentColor"
          >
            <path
              d="M6.22 3.22a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L9.94 8 6.22 4.28a.75.75 0 0 1 0-1.06Z"
            />
          </svg>
          Advanced
        </button>
        @if (showAdvanced) {
          <div class="mt-2">
            <label for="seed" class="text-xs font-medium text-[#8b949e] mb-1 block"
              >Seed
              <span class="text-[#656d76] font-normal"
                >&mdash; leave blank for random</span
              ></label
            >
            <input
              id="seed"
              type="text"
              [(ngModel)]="seed"
              name="seed"
              class="bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#e6edf3] w-56 focus:outline-none focus:border-[#58a6ff] transition-colors font-mono"
              placeholder="e.g. my-puzzle-42"
            />
          </div>
        }
      </div>
    </form>
  `,
})
export class ControlPanelComponent {
  readonly generate = output<GenerateParams>();

  seed = '';
  lang = 'en';
  difficulty = 3;
  size = 7;
  showAdvanced = false;

  onGenerate() {
    const seed =
      this.seed.trim() || Math.random().toString(36).substring(2, 10);
    this.generate.emit({
      seed,
      lang: this.lang,
      difficulty: this.difficulty,
      size: this.size,
    });
  }
}
