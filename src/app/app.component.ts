import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule],
  template: `
    <div class="app-container">
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
          <a class="navbar-brand" href="#">
            <i class="fas fa-graduation-cap me-2"></i>
            Skill Management Portal
          </a>
        </div>
      </nav>
      
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    
    .main-content {
      flex: 1;
      padding: 20px 0;
    }
    
    .navbar-brand {
      font-weight: 600;
      font-size: 1.5rem;
    }
  `]
})
export class AppComponent {
  title = 'SkillManagementPortal';
}