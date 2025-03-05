# README

## 1. Requirements

Afin que le petit programme fonction. Veuillez d'abord vous assurez que les éléments suivants sont installés:

- PostgreSQL
- Python (testé sur 3.10)
- git

## 2. Installation

Clone the repository:
```bash
git clone git@github.com:farochat/bnovate
cd bnovate
```

Create a virtual environment `.venv` and activate it
```bash
python -m venv .venv && . .venv/bin/activate
```

Install dependencies:
```bash
pip install --constraint requirements.txt .[dev]
```
## 3. Setup
Create a `config.yaml` file with the following fields:
```yaml
bnovate:
  host: host
  port: port
  database: dbname
  user: user
  password: password
```
Store in at the root of the repository and complete the fields accordingly.
**Important: make sure to assign new database for the test as this can have a bad impact on existing ones.**

Run the database initialization script (only once):
```bash
python db.py
```
This will create the database and/or tables if they do not already exist.

Run app
```bash
python app.py
```
## 4. Tests

Local tests are included in `test_upload.py`.

## 5. Usage
Open a new terminal window and reactivate python virtual environment
### Uploading CSV files
```bash
python upload.py path/to/csvfiles_folder
```
- The script requires all relevant CSV files to be in the specified folder.
- Only files with a `.csv` extension will be processed.

### Downloading Plots
```bash
python download.py path/to/download_folder
```
- This script fetches the generated plots and saves them in the specified folder.

## 6. Design Choices

### Database Structure
- The database consists of the following tables:
  - `users`: Stores user information.
  - `polygons`: Stores polygon metadata.
  - `vertices`: Stores unique (x, y) coordinate pairs.
  - `polygon_vertices`: Links polygons to their respective vertices.
  - `user_polygons`: Links users to their polygons.
- This design allows polygons to be shared between users without duplication.

### Test Assumptions
- For simplicity, each user currently has only one polygon. This results in some redundant fields (e.g., username and user_id).
- Users are emulated by the scripts, and there is no real authentication mechanism.
- Versioning for polygons was ignored.

## 7. Potential Improvements

- **Testing** Implement unit testing.
- **API Enhancements:** Implement API keys and robust user authentication.
- **Multiple Polygons per User:** Allow users to manage multiple polygons efficiently.
- **Precomputed Metrics:** Store precomputed values like polygon area in the database.
- **Include versioning** Could be done in `polygons` table and making couple `(polygon_id, version)` a primary key.
- **Codebase:** Improve code structure.

## 8. Transparence
- L'exercice m'aura pris plus qu'une heure à compléter.
- Le planning et le design a eu seul ont pris facilement 45 minutes.
- Le premier squelette de l'API a été généré par l'IA, parce que je n'avais jamais utilisé `Flask` et je me suis dit que ça irait plus vite si je la maintenant simple. Environ 15 minutes avant qu'il fonctionne correctement.
- J'ai passé plus de temps que prévu sur l'implémentation (et le design) de la database. Pour l'implémentation j'ai réutilisé du code que j'ai déjà fait dans le passé pour gagner un peu de temps. Refaire les nouvelles queries (dont une en particulier m'a donné un peu de fil à retordre). 30 bonnes minutes de travail.
- Comme j'avais déjà dépassé la durée fixée, j'ai décidé de skippé le testing (autre que le manuel).
- La documentation a pris bien 30 minutes aussi.
- Finalement le déploiement a du être testé, pendant un petit quart d'heure, surtout que j'ai pas développé l'application sur Ubuntu, mais Windows.

