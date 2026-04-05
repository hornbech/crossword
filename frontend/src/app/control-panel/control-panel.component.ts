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
    <form (ngSubmit)="onGenerate()" class="flex flex-wrap items-end gap-4">
      <div class="flex flex-col">
        <label for="seed" class="text-xs font-medium text-gray-500 mb-1">Seed</label>
        <input
          id="seed"
          type="text"
          [(ngModel)]="seed"
          name="seed"
          class="border border-gray-300 rounded-md px-3 py-2 text-sm w-40 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter a seed..."
        />
      </div>

      <div class="flex flex-col">
        <label for="lang" class="text-xs font-medium text-gray-500 mb-1">Language</label>
        <select
          id="lang"
          [(ngModel)]="lang"
          name="lang"
          class="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="en">English</option>
          <option value="da">Danish</option>
        </select>
      </div>

      <div class="flex flex-col">
        <label for="difficulty" class="text-xs font-medium text-gray-500 mb-1"
          >Difficulty</label
        >
        <select
          id="difficulty"
          [(ngModel)]="difficulty"
          name="difficulty"
          class="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option [ngValue]="1">Easy</option>
          <option [ngValue]="2">Medium</option>
          <option [ngValue]="3">Hard</option>
        </select>
      </div>

      <div class="flex flex-col">
        <label for="size" class="text-xs font-medium text-gray-500 mb-1">Grid Size</label>
        <select
          id="size"
          [(ngModel)]="size"
          name="size"
          class="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
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
        class="bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm px-5 py-2 rounded-md transition-colors"
      >
        Generate
      </button>
    </form>
  `,
})
export class ControlPanelComponent {
  readonly generate = output<GenerateParams>();

  seed = 'crossword';
  lang = 'en';
  difficulty = 3;
  size = 13;

  onGenerate() {
    this.generate.emit({
      seed: this.seed,
      lang: this.lang,
      difficulty: this.difficulty,
      size: this.size,
    });
  }
}
