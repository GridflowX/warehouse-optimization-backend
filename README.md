# Warehouse Optimization Backend

This project implements algorithms for optimizing warehouse or guideway networks, based on graph theory and mathematical optimization. It provides both a Python backend (with a FastAPI server) and a Jupyter notebook for experimentation and visualization.

## Features

- **Graph-based optimization** for warehouse/guideway layouts.
- **API endpoints** for running optimization and retrieving results.
- **Jupyter notebook** for interactive exploration and visualization.
- **Customizable input**: define your own nodes, edges, capacities, and commodities.

## Project Structure

- `main.py`: Main script to run the optimization algorithm with hardcoded example data.
- `backend/app.py`: FastAPI server exposing endpoints to run the algorithm and fetch results.
- `backend/runner.py`: Logic to run the optimization algorithm with given parameters.
- `main.ipynb`: Jupyter notebook for interactive use.
- `data_store_csv.py`, `plots.py`, etc.: Helper modules for data storage and visualization.

## How to Run

### 1. Clone the Repository

```bash
git clone <repo-url>
cd warehouse-optimization-backend
```

### 2. Run the Jupyter Notebook (for interactive exploration)

Open `main.ipynb` in Jupyter and run the cells. You can modify the input data (nodes, edges, etc.) as needed.

### 3. Run the Backend API

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn backend.app:app --reload
```

The API will be available at `http://127.0.0.1:8000/`.

#### API Endpoints

- `GET /` — Health check.
- `GET /health` — Health check.
- `POST /input` — Run the optimization algorithm.  
  **Body:**  
  ```json
  {
    "alpha": 0.5,
    "beta": 0.5
  }
  ```
- `GET /output` — Retrieve the latest optimization result.

## Customization

- To use your own data, modify the input parameters in `main.py` or send them via the API.
- You can also create new examples in the notebook by changing `input_points` and `edges_input`.

## Output

- Results are saved as JSON (`json_output.json`, `graph_output.json`) and CSV files.
- Plots and visualizations are generated for solution quality and network structure.

## License

See [LICENSE](LICENSE).

---

**Note:** This project is a backend/algorithmic engine. If you need a frontend, you can build one to interact with the API.
