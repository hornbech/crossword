import { Component, inject, signal } from '@angular/core';
import { CrosswordService, CrosswordResponse } from './crossword.service';
import { CrosswordGridComponent } from './crossword-grid/crossword-grid.component';
import {
  ControlPanelComponent,
  GenerateParams,
} from './control-panel/control-panel.component';

@Component({
  selector: 'app-root',
  imports: [CrosswordGridComponent, ControlPanelComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private readonly crosswordService = inject(CrosswordService);

  readonly puzzle = signal<CrosswordResponse | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  onGenerate(params: GenerateParams) {
    this.loading.set(true);
    this.error.set(null);

    this.crosswordService
      .generate(params.seed, params.lang, params.difficulty, params.size)
      .subscribe({
        next: (result) => {
          this.puzzle.set(result);
          this.loading.set(false);
        },
        error: (err) => {
          const detail = err.error?.detail ?? 'Failed to generate crossword. Is the backend running?';
          this.error.set(detail);
          this.loading.set(false);
        },
      });
  }
}
