import { Component, input } from '@angular/core';
import { CrosswordResponse } from '../crossword.service';

@Component({
  selector: 'app-crossword-grid',
  template: `
    @if (data(); as puzzle) {
      <div class="inline-block border-2 border-gray-800">
        @for (row of puzzle.grid; track $index; let r = $index) {
          <div class="flex">
            @for (cell of row; track $index; let c = $index) {
              <div
                class="relative w-10 h-10 border border-gray-300 flex items-center justify-center text-sm font-bold select-none"
                [class.bg-gray-900]="cell === '#'"
                [class.bg-white]="cell !== '#'"
                [class.text-gray-800]="cell !== '#'"
              >
                @if (cell !== '#') {
                  @if (clueNumber(r, c); as num) {
                    <span
                      class="absolute top-0 left-0.5 text-[9px] font-medium text-gray-500 leading-none"
                      >{{ num }}</span
                    >
                  }
                  <span>{{ cell }}</span>
                }
              </div>
            }
          </div>
        }
      </div>
      <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl">
        <div>
          <h3 class="text-lg font-semibold text-gray-700 mb-2">Across</h3>
          <ul class="space-y-1 text-sm text-gray-600">
            @for (w of acrossWords(); track w.clue_number) {
              <li>
                <span class="font-medium text-gray-800">{{ w.clue_number }}.</span>
                {{ w.word }} ({{ w.length }})
              </li>
            }
          </ul>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-700 mb-2">Down</h3>
          <ul class="space-y-1 text-sm text-gray-600">
            @for (w of downWords(); track w.clue_number) {
              <li>
                <span class="font-medium text-gray-800">{{ w.clue_number }}.</span>
                {{ w.word }} ({{ w.length }})
              </li>
            }
          </ul>
        </div>
      </div>
    }
  `,
})
export class CrosswordGridComponent {
  readonly data = input<CrosswordResponse | null>(null);

  private clueMap = new Map<string, number>();

  acrossWords() {
    const d = this.data();
    if (!d) return [];
    return d.words
      .filter((w) => w.direction === 'across')
      .sort((a, b) => a.clue_number - b.clue_number);
  }

  downWords() {
    const d = this.data();
    if (!d) return [];
    return d.words
      .filter((w) => w.direction === 'down')
      .sort((a, b) => a.clue_number - b.clue_number);
  }

  clueNumber(row: number, col: number): number | null {
    const d = this.data();
    if (!d) return null;

    if (this.clueMap.size === 0) {
      for (const w of d.words) {
        const key = `${w.row},${w.col}`;
        if (!this.clueMap.has(key)) {
          this.clueMap.set(key, w.clue_number);
        }
      }
    }

    return this.clueMap.get(`${row},${col}`) ?? null;
  }
}
