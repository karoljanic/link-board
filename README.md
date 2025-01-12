# link-board

**link-board** is a Streamlit app for interactive PCB layout design and visualization. Load, modify, and visualize your PCB designs with ease.

## Features
- Load and interact with PCB designs.
- Modify component positions in real-time.
- Visualize layouts with an intuitive interface.
- Export updated designs as SVG or `.kicad_pcb`.

## Requirements
- Docker

## Quick Start
Clone the repository:
```bash
git clone https://github.com/yourusername/link-board.git
cd link-board
```

Initialize Docker
```bash
systemctl start docker
```

Build and run the Docker container:
```bash
docker build -t link-board .
docker run -it --rm -v $(pwd):/app link-board
```

Clean up
```bash
docker system prune -f
```
