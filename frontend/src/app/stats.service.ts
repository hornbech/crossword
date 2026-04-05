import { Injectable, signal, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class StatsService implements OnDestroy {
  readonly totalVisitors = signal(0);
  readonly activeUsers = signal(0);

  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private http: HttpClient) {}

  init() {
    this.recordVisit();
    this.connectWebSocket();
  }

  private recordVisit() {
    this.http
      .post<{ total_visitors: number; active_users: number }>('/api/visit', {})
      .subscribe({
        next: (res) => {
          this.totalVisitors.set(res.total_visitors);
          this.activeUsers.set(res.active_users);
        },
      });
  }

  private connectWebSocket() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${location.host}/api/ws`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.active_users !== undefined) {
        this.activeUsers.set(data.active_users);
      }
    };

    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connectWebSocket(), 3000);
    };
  }

  ngOnDestroy() {
    this.ws?.close();
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
  }
}
