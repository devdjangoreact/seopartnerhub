# Installation frontend

npm install -g yarn
yarn install
yarn dev

# Installation backend

docker compose -f docker-compose.local.yml up --build
docker compose -f docker-compose.local.yml down
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser

http://127.0.0.1:8000
http://127.0.0.1:8025
http://127.0.0.1:5555
