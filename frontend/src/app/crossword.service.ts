import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PlacedWord {
  word: string;
  clue_number: number;
  row: number;
  col: number;
  direction: 'across' | 'down';
  length: number;
  clue: string | null;
}

export interface CrosswordResponse {
  size: number;
  seed: string;
  grid: string[][];
  black_cells: number[][];
  words: PlacedWord[];
}

@Injectable({ providedIn: 'root' })
export class CrosswordService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  generate(
    seed: string,
    lang: string,
    difficulty: number,
    size: number,
  ): Observable<CrosswordResponse> {
    const params = new HttpParams()
      .set('seed', seed)
      .set('lang', lang)
      .set('difficulty', difficulty)
      .set('size', size);

    return this.http.get<CrosswordResponse>(`${this.baseUrl}/generate`, {
      params,
    });
  }

  health(): Observable<{ status: string }> {
    return this.http.get<{ status: string }>(`${this.baseUrl}/health`);
  }
}
