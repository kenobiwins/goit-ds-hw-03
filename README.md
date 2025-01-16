
# goit-ds-hw-03

## cats_cli

1. Pull the MongoDB image:
   ```zsh
   docker pull mongo
   ```

2. Run MongoDB container:
   ```zsh
   docker run --name mongodb -d -p 27017:27017 mongo
   ```

3. Access MongoDB shell:
   ```zsh
   docker exec -it mongodb mongo
   ```

4. Run the Python application:
   ```zsh
   poetry run python main.py
   ```

## quotes_scraping

1. Pull the MongoDB image:
   ```zsh
   docker pull mongo
   ```

2. Run MongoDB container:
   ```zsh
   docker run --name mongodb -d -p 27017:27017 mongo
   ```

3. Access MongoDB shell:
   ```zsh
   docker exec -it mongodb mongo
   ```

4. Run the Python application:
   ```zsh
   poetry run python main.py
   ```
