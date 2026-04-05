import {
  Component,
  input,
  signal,
  computed,
  effect,
  ElementRef,
  viewChildren,
  QueryList,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CrosswordResponse, PlacedWord } from '../crossword.service';

interface CellState {
  row: number;
  col: number;
  isBlack: boolean;
  clueNumber: number | null;
  answer: string; // correct letter
  userInput: string; // what the user typed
}

@Component({
  selector: 'app-crossword-grid',
  imports: [FormsModule],
  template: `
    @if (data(); as puzzle) {
      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Grid -->
        <div>
          <div class="inline-block border border-[#30363d] rounded-lg overflow-hidden">
            @for (row of cells(); track $index; let r = $index) {
              <div class="flex">
                @for (cell of row; track $index; let c = $index) {
                  @if (cell.isBlack) {
                    <div class="w-10 h-10 bg-[#0d1117] border border-[#21262d]"></div>
                  } @else {
                    <div
                      class="relative w-10 h-10 border border-[#21262d] flex items-center justify-center cursor-pointer"
                      [class]="cellClass(cell)"
                      (click)="focusCell(r, c)"
                    >
                      @if (cell.clueNumber) {
                        <span
                          class="absolute top-0 left-0.5 text-[9px] font-medium text-[#656d76] leading-none"
                          >{{ cell.clueNumber }}</span
                        >
                      }
                      @if (revealed()) {
                        <span class="text-sm font-bold text-[#e6edf3]">{{
                          cell.answer
                        }}</span>
                      } @else {
                        <input
                          #cellInput
                          [attr.data-row]="r"
                          [attr.data-col]="c"
                          type="text"
                          maxlength="1"
                          [value]="cell.userInput"
                          (input)="onCellInput($event, r, c)"
                          (keydown)="onKeyDown($event, r, c)"
                          (focus)="onFocus(r, c)"
                          class="w-full h-full text-center text-sm font-bold uppercase bg-transparent text-[#e6edf3] outline-none caret-[#58a6ff]"
                        />
                      }
                    </div>
                  }
                }
              </div>
            }
          </div>

          <!-- Controls below grid -->
          <div class="mt-4 flex items-center gap-3">
            @if (!revealed()) {
              <button
                (click)="checkAnswers()"
                class="text-xs text-[#8b949e] hover:text-[#e6edf3] border border-[#30363d] rounded-lg px-3 py-1.5 transition-colors"
              >
                Check
              </button>
              <button
                (click)="revealed.set(true)"
                class="text-xs text-[#8b949e] hover:text-[#e6edf3] border border-[#30363d] rounded-lg px-3 py-1.5 transition-colors"
              >
                Reveal
              </button>
              <button
                (click)="clearGrid()"
                class="text-xs text-[#656d76] hover:text-[#8b949e] transition-colors"
              >
                Clear
              </button>
            } @else {
              <button
                (click)="hideAnswers()"
                class="text-xs text-[#8b949e] hover:text-[#e6edf3] border border-[#30363d] rounded-lg px-3 py-1.5 transition-colors"
              >
                Hide Answers
              </button>
            }
            @if (checked() && !revealed()) {
              <span class="text-xs text-[#656d76]">
                {{ correctCount() }}/{{ totalCells() }} correct
              </span>
            }
          </div>
        </div>

        <!-- Clues -->
        <div class="flex-1 min-w-0 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-6">
          <div>
            <h3 class="text-sm font-semibold text-[#e6edf3] mb-2">Across</h3>
            <ul class="space-y-1">
              @for (clue of acrossClues(); track clue.clue_number) {
                <li
                  class="text-sm cursor-pointer rounded px-1.5 py-0.5 -mx-1.5 transition-colors"
                  [class.bg-[#1c2128]]="
                    selectedClue()?.clue_number === clue.clue_number &&
                    selectedClue()?.direction === 'across'
                  "
                  [class.text-[#e6edf3]]="
                    selectedClue()?.clue_number === clue.clue_number &&
                    selectedClue()?.direction === 'across'
                  "
                  [class.text-[#8b949e]]="
                    selectedClue()?.clue_number !== clue.clue_number ||
                    selectedClue()?.direction !== 'across'
                  "
                  (click)="selectClue(clue)"
                >
                  <span class="font-medium text-[#e6edf3]"
                    >{{ clue.clue_number }}.</span
                  >
                  {{ clue.length }} letters
                </li>
              }
            </ul>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-[#e6edf3] mb-2">Down</h3>
            <ul class="space-y-1">
              @for (clue of downClues(); track clue.clue_number) {
                <li
                  class="text-sm cursor-pointer rounded px-1.5 py-0.5 -mx-1.5 transition-colors"
                  [class.bg-[#1c2128]]="
                    selectedClue()?.clue_number === clue.clue_number &&
                    selectedClue()?.direction === 'down'
                  "
                  [class.text-[#e6edf3]]="
                    selectedClue()?.clue_number === clue.clue_number &&
                    selectedClue()?.direction === 'down'
                  "
                  [class.text-[#8b949e]]="
                    selectedClue()?.clue_number !== clue.clue_number ||
                    selectedClue()?.direction !== 'down'
                  "
                  (click)="selectClue(clue)"
                >
                  <span class="font-medium text-[#e6edf3]"
                    >{{ clue.clue_number }}.</span
                  >
                  {{ clue.length }} letters
                </li>
              }
            </ul>
          </div>
        </div>
      </div>
    }
  `,
})
export class CrosswordGridComponent {
  readonly data = input<CrosswordResponse | null>(null);
  readonly cells = signal<CellState[][]>([]);
  readonly revealed = signal(false);
  readonly checked = signal(false);
  readonly selectedClue = signal<PlacedWord | null>(null);
  readonly focusedCell = signal<{ row: number; col: number } | null>(null);
  readonly direction = signal<'across' | 'down'>('across');

  readonly correctCount = signal(0);
  readonly totalCells = signal(0);

  readonly acrossClues = computed(() => {
    const d = this.data();
    if (!d) return [];
    return d.words
      .filter((w) => w.direction === 'across')
      .sort((a, b) => a.clue_number - b.clue_number);
  });

  readonly downClues = computed(() => {
    const d = this.data();
    if (!d) return [];
    return d.words
      .filter((w) => w.direction === 'down')
      .sort((a, b) => a.clue_number - b.clue_number);
  });

  private clueMap = new Map<string, number>();
  private wordMap = new Map<string, PlacedWord>(); // "row,col,dir" -> word

  constructor() {
    effect(() => {
      const d = this.data();
      if (!d) return;
      this.buildCells(d);
      this.revealed.set(false);
      this.checked.set(false);
      this.selectedClue.set(null);
    });
  }

  private buildCells(puzzle: CrosswordResponse) {
    this.clueMap.clear();
    this.wordMap.clear();

    for (const w of puzzle.words) {
      const key = `${w.row},${w.col}`;
      if (!this.clueMap.has(key)) {
        this.clueMap.set(key, w.clue_number);
      }
      this.wordMap.set(`${w.row},${w.col},${w.direction}`, w);
    }

    const grid: CellState[][] = [];
    let total = 0;
    for (let r = 0; r < puzzle.size; r++) {
      const row: CellState[] = [];
      for (let c = 0; c < puzzle.size; c++) {
        const isBlack = puzzle.grid[r][c] === '#';
        if (!isBlack) total++;
        row.push({
          row: r,
          col: c,
          isBlack,
          clueNumber: this.clueMap.get(`${r},${c}`) ?? null,
          answer: puzzle.grid[r][c],
          userInput: '',
        });
      }
      grid.push(row);
    }
    this.cells.set(grid);
    this.totalCells.set(total);
  }

  cellClass(cell: CellState): string {
    if (cell.isBlack) return 'bg-[#0d1117]';
    const focused = this.focusedCell();
    const isFocused = focused?.row === cell.row && focused?.col === cell.col;

    // Highlight cells in the selected word
    const clue = this.selectedClue();
    let inWord = false;
    if (clue) {
      if (clue.direction === 'across' && cell.row === clue.row) {
        inWord = cell.col >= clue.col && cell.col < clue.col + clue.length;
      } else if (clue.direction === 'down' && cell.col === clue.col) {
        inWord = cell.row >= clue.row && cell.row < clue.row + clue.length;
      }
    }

    if (this.checked()) {
      if (cell.userInput && cell.userInput === cell.answer) {
        return isFocused
          ? 'bg-[rgba(63,185,80,0.2)] ring-1 ring-[#3fb950]'
          : 'bg-[rgba(63,185,80,0.1)]';
      }
      if (cell.userInput && cell.userInput !== cell.answer) {
        return isFocused
          ? 'bg-[rgba(248,81,73,0.2)] ring-1 ring-[#f85149]'
          : 'bg-[rgba(248,81,73,0.1)]';
      }
    }

    if (isFocused) return 'bg-[#264f78] ring-1 ring-[#58a6ff]';
    if (inWord) return 'bg-[#1c2128]';
    return 'bg-[#161b22]';
  }

  focusCell(row: number, col: number) {
    this.focusedCell.set({ row, col });
    this.findAndSelectClue(row, col);
    // Focus the input
    setTimeout(() => {
      const input = document.querySelector(
        `input[data-row="${row}"][data-col="${col}"]`,
      ) as HTMLInputElement | null;
      input?.focus();
    });
  }

  onFocus(row: number, col: number) {
    this.focusedCell.set({ row, col });
    this.findAndSelectClue(row, col);
  }

  private findAndSelectClue(row: number, col: number) {
    const d = this.data();
    if (!d) return;

    // If clicking the same cell, toggle direction
    const current = this.selectedClue();
    if (current) {
      const inCurrentWord = this.isCellInWord(row, col, current);
      if (inCurrentWord) {
        // Check if there's a word in the other direction at this cell
        const otherDir = current.direction === 'across' ? 'down' : 'across';
        const otherWord = d.words.find(
          (w) =>
            w.direction === otherDir &&
            this.isCellInWord(row, col, w),
        );
        if (otherWord) {
          this.selectedClue.set(otherWord);
          this.direction.set(otherDir);
          return;
        }
        return; // Stay on current word
      }
    }

    // Find a word containing this cell, prefer current direction
    const dir = this.direction();
    const preferred = d.words.find(
      (w) => w.direction === dir && this.isCellInWord(row, col, w),
    );
    if (preferred) {
      this.selectedClue.set(preferred);
      return;
    }
    const any = d.words.find((w) => this.isCellInWord(row, col, w));
    if (any) {
      this.selectedClue.set(any);
      this.direction.set(any.direction);
    }
  }

  private isCellInWord(row: number, col: number, w: PlacedWord): boolean {
    if (w.direction === 'across') {
      return row === w.row && col >= w.col && col < w.col + w.length;
    }
    return col === w.col && row >= w.row && row < w.row + w.length;
  }

  onCellInput(event: Event, row: number, col: number) {
    const input = event.target as HTMLInputElement;
    const value = input.value.toUpperCase().replace(/[^A-Z]/g, '');
    input.value = value;

    const grid = this.cells();
    grid[row][col].userInput = value;
    this.cells.set([...grid]);
    this.checked.set(false);

    if (value) {
      this.advanceCursor(row, col);
    }
  }

  onKeyDown(event: KeyboardEvent, row: number, col: number) {
    if (event.key === 'Backspace') {
      const grid = this.cells();
      if (!grid[row][col].userInput) {
        // Move back if current cell is empty
        event.preventDefault();
        this.retreatCursor(row, col);
      } else {
        grid[row][col].userInput = '';
        this.cells.set([...grid]);
        this.checked.set(false);
      }
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      this.moveCursor(row, col, 0, 1);
    } else if (event.key === 'ArrowLeft') {
      event.preventDefault();
      this.moveCursor(row, col, 0, -1);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      this.moveCursor(row, col, 1, 0);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      this.moveCursor(row, col, -1, 0);
    } else if (event.key === 'Tab') {
      event.preventDefault();
      this.advanceToNextWord(event.shiftKey);
    }
  }

  private advanceCursor(row: number, col: number) {
    const dir = this.direction();
    if (dir === 'across') {
      this.moveCursor(row, col, 0, 1);
    } else {
      this.moveCursor(row, col, 1, 0);
    }
  }

  private retreatCursor(row: number, col: number) {
    const dir = this.direction();
    if (dir === 'across') {
      this.moveCursor(row, col, 0, -1);
    } else {
      this.moveCursor(row, col, -1, 0);
    }
  }

  private moveCursor(row: number, col: number, dr: number, dc: number) {
    const grid = this.cells();
    const size = grid.length;
    let nr = row + dr;
    let nc = col + dc;
    while (nr >= 0 && nr < size && nc >= 0 && nc < size) {
      if (!grid[nr][nc].isBlack) {
        this.focusCell(nr, nc);
        return;
      }
      nr += dr;
      nc += dc;
    }
  }

  private advanceToNextWord(backward: boolean) {
    const d = this.data();
    const current = this.selectedClue();
    if (!d || !current) return;

    const dir = this.direction();
    const words = d.words
      .filter((w) => w.direction === dir)
      .sort((a, b) => a.clue_number - b.clue_number);
    const idx = words.findIndex(
      (w) => w.clue_number === current.clue_number && w.direction === dir,
    );
    const next = backward
      ? words[(idx - 1 + words.length) % words.length]
      : words[(idx + 1) % words.length];
    this.selectClue(next);
  }

  selectClue(clue: PlacedWord) {
    this.selectedClue.set(clue);
    this.direction.set(clue.direction);
    this.focusCell(clue.row, clue.col);
  }

  checkAnswers() {
    const grid = this.cells();
    let correct = 0;
    for (const row of grid) {
      for (const cell of row) {
        if (!cell.isBlack && cell.userInput && cell.userInput === cell.answer) {
          correct++;
        }
      }
    }
    this.correctCount.set(correct);
    this.checked.set(true);
  }

  clearGrid() {
    const grid = this.cells();
    for (const row of grid) {
      for (const cell of row) {
        cell.userInput = '';
      }
    }
    this.cells.set([...grid]);
    this.checked.set(false);
  }

  hideAnswers() {
    this.revealed.set(false);
  }
}
