# Skill Management Portal

A modern Angular application for managing and assessing technical skills.

## Features

- **Home Dashboard**: Overview of available features
- **Skills Management**: View and track your technical skills
- **Assessment System**: Take interactive skill assessments
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js (version 18 or higher)
- npm (comes with Node.js)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open your browser and navigate to `http://localhost:4200`

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm run watch` - Build and watch for changes
- `npm test` - Run unit tests

## Project Structure

```
src/
├── app/
│   ├── home/           # Home page component
│   ├── skills/         # Skills management component
│   ├── assessment/     # Assessment component
│   ├── app.component.ts # Root component
│   └── app.routes.ts   # Routing configuration
├── assets/             # Static assets
├── environments/       # Environment configurations
└── styles.css         # Global styles
```

## Technologies Used

- Angular 17 (Standalone Components)
- TypeScript
- Bootstrap 5
- Font Awesome Icons
- RxJS

## Development

This project uses Angular's standalone components architecture for better modularity and performance.

### Adding New Components

```bash
ng generate component component-name --standalone
```

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.