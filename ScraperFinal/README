Projekt Scraper na zajęcia Przetwarzanie równoległe i rozproszone
Autorstwa: Kacper Zawiszewski 20510 i Bartosz Maciejewski 20461

Uruchomienie w docker:
  cd ScraperFinal
  docker compose build -up

Uruchomienie w kubernetesie za pomoca minikuba:
  minikube start //Uruchomienie minikuba
  cd ScraperFinal //wejscie do głownego katalogu w projekcie
  docker build -t kacperzaw/flask-app:latest -f flaskr/Dockerfile . //Stworzenie obrazu z otagowaniem
  docker push kacperzaw/flask-app:latest //Stworzenie obrazu z otagowaniem
  
  cd web_scraper //wejscie do podkatalogu
  docker build -t kacperzaw/web-scraper:latest . //Stworzenie obrazu z otagowaniem
  docker push kacperzaw/web-scraper:latest //Stworzenie obrazu z otagowaniem
  
  cd .. //wyjście z podkatalogu
  
  kubectl apply -f k8s/mongodb-deployment.yaml //utworzenie deployments i services
  kubectl apply -f k8s/flask-deployment.yaml //utworzenie deployments i services
  kubectl apply -f k8s/scraper-deployment.yaml //utworzenie deployments i services
  
  minikube service flask-service //uruchomienie service flask
