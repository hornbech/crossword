import { Component, inject, signal, OnInit } from '@angular/core';
import { CrosswordService, CrosswordResponse } from './crossword.service';
import { StatsService } from './stats.service';
import { CrosswordGridComponent } from './crossword-grid/crossword-grid.component';
import {
  ControlPanelComponent,
  GenerateParams,
} from './control-panel/control-panel.component';
import { InfoOverlayComponent } from './info-overlay/info-overlay.component';

@Component({
  selector: 'app-root',
  imports: [CrosswordGridComponent, ControlPanelComponent, InfoOverlayComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  private readonly crosswordService = inject(CrosswordService);
  readonly stats = inject(StatsService);

  readonly puzzle = signal<CrosswordResponse | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly showInfo = signal(false);

  ngOnInit() {
    this.stats.init();
  }

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
          const detail =
            err.error?.detail ?? 'Failed to generate crossword. Is the backend running?';
          this.error.set(detail);
          this.loading.set(false);
        },
      });
  }
}
